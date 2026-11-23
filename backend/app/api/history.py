
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.database import get_db


router = APIRouter()

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"


@router.get("/history")
def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    datasets = db.scalars(
        select(models.Dataset)
        .options(selectinload(models.Dataset.analyses))
        .order_by(models.Dataset.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    history = []

    for dataset in datasets:
        latest_analysis = max(
            dataset.analyses,
            key=lambda analysis: analysis.created_at,
            default=None
        )

        history.append({
            "dataset_id": dataset.id,
            "filename": dataset.filename,
            "file_type": dataset.file_type,
            "file_size": dataset.file_size,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "uploaded_at": dataset.uploaded_at,
            "analysis_id": latest_analysis.id if latest_analysis else None,
            "analysis_created_at": (
                latest_analysis.created_at if latest_analysis else None
            ),
            "analysis_count": len(dataset.analyses)
        })

    return {
        "success": True,
        "total_returned": len(history),
        "skip": skip,
        "limit": limit,
        "history": history
    }


@router.get("/history/{dataset_id}")
def get_dataset_details(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset = db.scalar(
        select(models.Dataset)
        .options(selectinload(models.Dataset.analyses))
        .where(models.Dataset.id == dataset_id)
    )

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    latest_analysis = max(
        dataset.analyses,
        key=lambda analysis: analysis.created_at,
        default=None
    )

    return {
        "success": True,
        "dataset": {
            "id": dataset.id,
            "filename": dataset.filename,
            "file_type": dataset.file_type,
            "file_size": dataset.file_size,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "uploaded_at": dataset.uploaded_at,
            "analysis_count": len(dataset.analyses),
            "latest_analysis_id": (
                latest_analysis.id if latest_analysis else None
            )
        }
    }


@router.get("/history/{dataset_id}/analysis")
def get_saved_analysis(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset = db.get(models.Dataset, dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    analysis = db.scalar(
        select(models.Analysis)
        .where(models.Analysis.dataset_id == dataset_id)
        .order_by(models.Analysis.created_at.desc())
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No saved analysis found for this dataset."
        )

    return {
        "success": True,
        "dataset": {
            "id": dataset.id,
            "filename": dataset.filename,
            "uploaded_at": dataset.uploaded_at
        },
        "analysis": {
            "id": analysis.id,
            "created_at": analysis.created_at,
            "profile": analysis.profile,
            "quality": analysis.quality,
            "diagnostics": analysis.diagnostics,
            "analytics": analysis.analytics,
            "anomalies": analysis.anomalies,
            "forecast": analysis.forecast,
            "ai_insights": analysis.ai_insights
        }
    }


@router.delete("/history/{dataset_id}")
def delete_dataset_history(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    dataset = db.get(models.Dataset, dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found."
        )

    stored_file = None

    if dataset.file_path:
        candidate = (BACKEND_DIR / dataset.file_path).resolve()
        upload_directory = UPLOAD_DIR.resolve()

        # Only allow deletion of files inside the uploads directory.
        if candidate.is_relative_to(upload_directory):
            stored_file = candidate

    filename = dataset.filename

    try:
        # The model relationships cascade to analyses and reports.
        db.delete(dataset)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not delete dataset history."
        )

    file_deleted = False

    if stored_file and stored_file.is_file():
        try:
            stored_file.unlink()
            file_deleted = True
        except OSError:
            file_deleted = False

    return {
        "success": True,
        "message": "Dataset history deleted successfully.",
        "dataset_id": dataset_id,
        "filename": filename,
        "stored_file_deleted": file_deleted
    }
