from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
from io import BytesIO
import json
import math
import uuid

import pandas as pd

from app.services.data_quality_service import analyze_data_quality
from app.services.profiling_service import analyze_dataset
from app.services.business_diagnostic_service import analyze_business_diagnostics
from app.services.analytics_service import analyze_dataset_analytics
from app.database import SessionLocal
from app import models

from app.services.gemini_service import generate_ai_response
from app.services.anomaly_service import analyze_anomalies
from app.services.forecasting_service import forecast_dataset
from fastapi.responses import StreamingResponse
from app.services.report_service import generate_pdf_report


router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def make_json_safe(value):
    """Convert Pandas/NumPy values into JSON-serializable values."""

    if value is None or value is pd.NA or value is pd.NaT:
        return None

    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            return make_json_safe(value.item())
        except (ValueError, TypeError):
            pass

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def read_csv_with_fallback(content):
    """
    Read CSV files using multiple common encodings.
    """

    encodings = ["utf-8-sig", "cp1252", "latin1"]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                BytesIO(content),
                encoding=encoding
            )

            print(f"CSV successfully decoded using: {encoding}")
            return df

        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to identify the CSV file encoding.")


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only XLSX, XLS and CSV files are supported."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB upload limit."
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    stored_filename = f"{uuid.uuid4().hex}{extension}"
    stored_path = UPLOAD_DIR / stored_filename
    db = SessionLocal()

    try:
        # Read CSV or Excel file.
        if extension == ".csv":
            df = read_csv_with_fallback(content)
        else:
            df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no records."
            )

        # Run all existing analysis engines.
        profile = analyze_dataset(df)
        quality = analyze_data_quality(df)
        diagnostics = analyze_business_diagnostics(df)
        analytics = analyze_dataset_analytics(df)
        anomalies = analyze_anomalies(df)
        forecast = forecast_dataset(df, horizon=3)

        # Save the original file using a generated, collision-resistant name.
        stored_path.write_bytes(content)

        # Save dataset metadata.
        dataset = models.Dataset(
            filename=file.filename or "uploaded_dataset",
            stored_filename=stored_filename,
            file_path=str(stored_path.relative_to(UPLOAD_DIR.parent)),
            file_type=extension.lstrip("."),
            file_size=len(content),
            row_count=int(len(df)),
            column_count=int(len(df.columns))
        )

        db.add(dataset)
        db.flush()

        # Save all analysis results as JSON-compatible data.
        analysis = models.Analysis(
            dataset_id=dataset.id,
            profile=make_json_safe(profile),
            quality=make_json_safe(quality),
            diagnostics=make_json_safe(diagnostics),
            analytics=make_json_safe(analytics),
            anomalies=make_json_safe(anomalies),
            forecast=make_json_safe(forecast)
        )

        db.add(analysis)
        db.commit()
        db.refresh(dataset)
        db.refresh(analysis)

        return {
            "success": True,
            "dataset_id": dataset.id,
            "analysis_id": analysis.id,
            "filename": file.filename,
            "message": "Dataset uploaded, analyzed and saved successfully.",
            "profile": profile,
            "quality": quality,
            "diagnostics": diagnostics,
            "analytics": analytics,
            "anomalies": anomalies,
            "forecast": forecast
        }

    except HTTPException:
        db.rollback()
        if stored_path.exists():
            stored_path.unlink()
        raise

    except Exception as error:
        db.rollback()
        if stored_path.exists():
            stored_path.unlink()

        print(f"Dataset upload and database error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process and save the dataset."
        )

    finally:
        db.close()

@router.post("/analytics/filter")
async def filter_dataset_analytics(
    file: UploadFile = File(...),
    start_date: str = Form(None),
    end_date: str = Form(None),
    category_value: str = Form(None)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only XLSX, XLS and CSV files are supported."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB upload limit."
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        # Read uploaded dataset
        if extension == ".csv":
            df = read_csv_with_fallback(content)
        else:
            df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no records."
            )

        # Validate date filters
        if start_date:
            try:
                pd.to_datetime(start_date, errors="raise")
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid start date."
                )

        if end_date:
            try:
                pd.to_datetime(end_date, errors="raise")
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end date."
                )

        if start_date and end_date:
            if pd.to_datetime(start_date) > pd.to_datetime(end_date):
                raise HTTPException(
                    status_code=400,
                    detail="Start date cannot be after end date."
                )

        # Apply filters and calculate analytics
        analytics = analyze_dataset_analytics(
            df,
            start_date=start_date,
            end_date=end_date,
            category_value=category_value
        )

        return {
            "success": True,
            "message": "Analytics filters applied successfully.",
            "analytics": analytics
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to filter dataset: {str(error)}"
        )

@router.post("/ai/ask")
async def ask_dataset_ai(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Answer natural-language questions using dataset analysis
    and Gemini AI.
    """

    extension = Path(file.filename or "").suffix.lower()

    # Validate file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only XLSX, XLS and CSV files are supported."
        )

    # Validate question
    question = question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    if len(question) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Question cannot exceed 1000 characters."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB upload limit."
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        # Read dataset
        if extension == ".csv":
            df = read_csv_with_fallback(content)
        else:
            df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no records."
            )

        # Run existing InsightIQ analysis engines
        profile = analyze_dataset(df)
        quality = analyze_data_quality(df)
        diagnostics = analyze_business_diagnostics(df)
        analytics = analyze_dataset_analytics(df)

        # Prepare analytical context for Gemini
        dataset_context = {
            "filename": file.filename,
            "dataset_shape": {
                "rows": len(df),
                "columns": len(df.columns)
            },
            "column_names": df.columns.tolist(),
            "profile": profile,
            "data_quality": quality,
            "business_diagnostics": diagnostics,
            "analytics": analytics
        }

        context_text = json.dumps(
            dataset_context,
            indent=2,
            default=str
        )

        # Limit context size
        context_text = context_text[:25000]

        prompt = f"""
You are InsightIQ, an intelligent business data analytics assistant.

Your job is to answer questions about a dataset using the
analytical evidence provided below.

USER QUESTION:
{question}

DATASET ANALYSIS:
{context_text}

INSTRUCTIONS:

1. Answer the user's question directly.
2. Use the supplied analytics and diagnostic results as evidence.
3. Never invent numbers, statistics, or business findings.
4. If the available data cannot answer the question, explain why.
5. Explain important findings in simple professional language.
6. When appropriate, provide practical business recommendations.
7. Distinguish between confirmed findings and possible explanations.
8. Do not claim that correlation proves causation.
9. Do not assume information that is not present in the dataset.
10. Use Markdown formatting for readability.

You are analyzing the dataset through InsightIQ.
"""

        # Generate AI response
        ai_answer = generate_ai_response(prompt)

        return {
            "success": True,
            "question": question,
            "filename": file.filename,
            "answer": ai_answer,
            "model": "gemini-3.5-flash-lite"
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"AI analysis error: {error}")

        raise HTTPException(
            status_code=502,
            detail="AI analysis failed. Please try again later."
        )

@router.post("/ai/predictive-insights")
async def generate_predictive_insights(
    file: UploadFile = File(...)
):
    """
    Generate AI-powered business insights from
    historical data and forecasting results.
    """

    extension = Path(file.filename or "").suffix.lower()

    # Validate file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only XLSX, XLS and CSV files are supported."
        )

    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB upload limit."
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        # Read uploaded dataset
        if extension == ".csv":
            df = read_csv_with_fallback(content)
        else:
            df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no records."
            )

        # Generate forecasts using the existing forecasting engine
        forecast = forecast_dataset(df, horizon=3)

        completed_metrics = forecast.get(
            "completed_metrics", []
        )

        # Handle insufficient forecasting data
        if not completed_metrics:
            return {
                "success": True,
                "status": forecast.get("status"),
                "message": (
                    "Predictive insights cannot be generated "
                    "because sufficient forecast data is unavailable."
                ),
                "filename": file.filename,
                "forecast": forecast,
                "insights": None
            }

        # Prepare evidence for Gemini
        predictive_context = {
            "filename": file.filename,
            "dataset_shape": {
                "rows": int(len(df)),
                "columns": int(len(df.columns))
            },
            "column_names": df.columns.tolist(),
            "forecast_results": forecast
        }

        context_text = json.dumps(
            predictive_context,
            indent=2,
            default=str
        )

        context_text = context_text[:20000]

        prompt = f"""
You are InsightIQ, an intelligent business
predictive analytics assistant.

Analyze the historical performance and forecast
results provided below.

DATASET AND FORECAST EVIDENCE:
{context_text}

YOUR TASK:

Generate a professional predictive business analysis.

Include the following sections:

1. Executive Summary
   Summarize the overall predicted business outlook.

2. Revenue Outlook
   Explain the predicted revenue trend using actual
   forecast values.

3. Profit Outlook
   Explain the predicted profit trend using actual
   forecast values.

4. Potential Business Risks
   Identify possible risks supported by the
   historical and forecast data.

5. Business Opportunities
   Identify potential opportunities based on
   observed trends.

6. Recommendations
   Provide practical recommendations supported
   by the available evidence.

IMPORTANT RULES:

- Use only the supplied dataset and forecast results.
- Never invent numbers, statistics, or findings.
- Clearly distinguish historical actual values
  from predicted values.
- Forecasts are estimates, not guaranteed outcomes.
- Do not claim that correlation proves causation.
- Do not present potential risks as confirmed events.
- If only one metric has a completed forecast,
  explain that the other metric is unavailable.
- Mention limitations caused by limited historical data.
- Do not make unsupported claims about market conditions.
- Use clear, professional language.
- Format the response using Markdown.

CURRENCY AND FORMATTING RULES:
- Never assume or invent a currency.
- If the dataset does not explicitly specify a currency,
  display financial values as plain numbers without currency symbols.
- Do not use $, €, £, ৳, or any other currency symbol unless
  the currency is explicitly identified in the dataset.
- Clearly distinguish historical actual values from forecast values.
- Do not present predictions as guaranteed business outcomes.

"""

        # Generate predictive insights using Gemini
        ai_insights = generate_ai_response(prompt)

        return {
            "success": True,
            "status": "completed",
            "filename": file.filename,
            "forecast": forecast,
            "insights": ai_insights,
            "model": "gemini-3.5-flash-lite"
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"Predictive insights error: {error}")

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to generate predictive insights. "
                "Please try again later."
            )
        )

@router.post("/reports/pdf")
async def generate_dataset_pdf_report(
    file: UploadFile = File(...),
    ai_insights: str = Form(None)
):
    """
    Generate a downloadable PDF business analysis report.
    """

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only XLSX, XLS and CSV files are supported."
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 20 MB upload limit."
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:
        # Read dataset
        if extension == ".csv":
            df = read_csv_with_fallback(content)
        else:
            df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="The uploaded dataset contains no records."
            )

        # Run all existing analysis engines
        profile = analyze_dataset(df)
        quality = analyze_data_quality(df)
        diagnostics = analyze_business_diagnostics(df)
        analytics = analyze_dataset_analytics(df)
        anomalies = analyze_anomalies(df)
        forecast = forecast_dataset(df, horizon=3)

        # Generate PDF
        pdf_buffer = generate_pdf_report(
            filename=file.filename,
            profile=profile,
            quality=quality,
            diagnostics=diagnostics,
            analytics=analytics,
            anomalies=anomalies,
            forecast=forecast,
            ai_insights=ai_insights
        )

        # Prepare download filename
        report_filename = (
            f"{Path(file.filename).stem}_InsightIQ_Report.pdf"
        )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{report_filename}"'
                )
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        print(f"PDF report generation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate PDF report."
        )
