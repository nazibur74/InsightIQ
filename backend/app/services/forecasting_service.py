
import numpy as np
import pandas as pd

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from app.services.business_diagnostic_service import detect_column_mapping


MIN_HISTORY_MONTHS = 6
ALLOWED_HORIZONS = [3, 6, 12]


def forecast_dataset(df: pd.DataFrame, horizon: int = 3):
    """
    Generate monthly forecasts for revenue and profit.

    Uses Holt's Damped Trend Exponential Smoothing.

    Missing months are preserved as missing observations rather
    than automatically being interpreted as zero business activity.
    """

    if horizon not in ALLOWED_HORIZONS:
        raise ValueError(
            f"Forecast horizon must be one of {ALLOWED_HORIZONS}."
        )

    mapping = detect_column_mapping(df)

    date_column = mapping.get("date")
    revenue_column = mapping.get("revenue")
    profit_column = mapping.get("profit")

    if not date_column:
        return {
            "status": "insufficient_data",
            "message": "No suitable date column was detected.",
            "horizon_months": horizon,
            "metrics": {}
        }

    if not revenue_column and not profit_column:
        return {
            "status": "insufficient_data",
            "message": "No revenue or profit column was detected.",
            "horizon_months": horizon,
            "metrics": {}
        }

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    invalid_date_count = int(data[date_column].isna().sum())

    data = data.dropna(subset=[date_column])

    if data.empty:
        return {
            "status": "insufficient_data",
            "message": "No valid dates were found in the dataset.",
            "horizon_months": horizon,
            "metrics": {}
        }

    data["forecast_month"] = data[date_column].dt.to_period("M")

    metrics = {}

    metric_columns = {
        "revenue": revenue_column,
        "profit": profit_column
    }

    for metric_name, column in metric_columns.items():

        if not column:
            continue

        values = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        metric_data = data.assign(
            forecast_value=values
        ).dropna(subset=["forecast_value"])

        invalid_value_count = int(values.isna().sum())

        if metric_data.empty:
            metrics[metric_name] = {
                "status": "insufficient_data",
                "message": (
                    f"No valid numerical values found for {metric_name}."
                ),
                "invalid_values": invalid_value_count
            }
            continue

        # Aggregate actual observations by month.
        monthly = (
            metric_data.groupby("forecast_month")["forecast_value"]
            .sum()
            .sort_index()
        )

        # Build a continuous monthly index.
        full_months = pd.period_range(
            start=monthly.index.min(),
            end=monthly.index.max(),
            freq="M"
        )

        # Keep missing months as NaN instead of assuming zero.
        monthly = monthly.reindex(full_months)

        missing_months = [
            period.strftime("%Y-%m")
            for period in monthly.index[monthly.isna()]
        ]

        available_months = int(monthly.notna().sum())

        # A model cannot reliably use missing observations.
        if monthly.isna().any():
            metrics[metric_name] = {
                "status": "incomplete_history",
                "message": (
                    "Some months have no valid observations. "
                    "Forecasting was skipped to avoid treating "
                    "missing data as zero activity."
                ),
                "available_months": available_months,
                "required_months": MIN_HISTORY_MONTHS,
                "missing_months": missing_months,
                "invalid_values": invalid_value_count
            }
            continue

        if len(monthly) < MIN_HISTORY_MONTHS:
            metrics[metric_name] = {
                "status": "insufficient_history",
                "message": (
                    f"At least {MIN_HISTORY_MONTHS} months of "
                    f"history are required. Found {len(monthly)} months."
                ),
                "available_months": int(len(monthly)),
                "required_months": MIN_HISTORY_MONTHS,
                "missing_months": missing_months,
                "invalid_values": invalid_value_count
            }
            continue

        monthly_values = monthly.astype(float)

        if not np.isfinite(monthly_values).all():
            metrics[metric_name] = {
                "status": "error",
                "message": "Non-finite values were found in the time series."
            }
            continue

        try:
            model = ExponentialSmoothing(
                monthly_values,
                trend="add",
                damped_trend=True,
                seasonal=None,
                initialization_method="estimated"
            )

            fitted_model = model.fit(optimized=True)

            # Generate forecasts once.
            forecast_values = fitted_model.forecast(
                horizon
            ).to_numpy(dtype=float)

            forecast_dates = pd.date_range(
                start=monthly.index[-1].to_timestamp() + pd.offsets.MonthBegin(1),
                periods=horizon,
                freq="MS"
            )

            metrics[metric_name] = {
                "status": "completed",
                "historical_months": int(len(monthly)),
                "missing_months": [],
                "invalid_values": invalid_value_count,
                "model": "Holt's Damped Trend Exponential Smoothing",

                "history": [
                    {
                        "month": period.strftime("%Y-%m"),
                        "actual": round(float(value), 2)
                    }
                    for period, value in monthly.items()
                ],

                "forecast": [
                    {
                        "month": date.strftime("%Y-%m"),
                        "predicted": round(float(value), 2)
                    }
                    for date, value in zip(
                        forecast_dates,
                        forecast_values
                    )
                ]
            }

        except Exception as error:
            metrics[metric_name] = {
                "status": "error",
                "message": f"Forecasting failed: {str(error)}"
            }

    completed_metrics = [
        name for name, result in metrics.items()
        if result.get("status") == "completed"
    ]

    incomplete_metrics = [
        name for name, result in metrics.items()
        if result.get("status") == "incomplete_history"
    ]

    if completed_metrics:
        overall_status = "completed"
        overall_message = "Forecasting completed successfully."
    elif incomplete_metrics:
        overall_status = "incomplete_history"
        overall_message = (
            "Forecasting could not be completed because "
            "some months have missing observations."
        )
    else:
        overall_status = "insufficient_data"
        overall_message = (
            "Insufficient historical data to generate forecasts."
        )

    return {
        "status": overall_status,
        "message": overall_message,
        "horizon_months": horizon,
        "date_column": date_column,

        "detected_columns": {
            "revenue": revenue_column,
            "profit": profit_column
        },

        "completed_metrics": completed_metrics,
        "metrics": metrics,

        "data_quality": {
            "invalid_dates": invalid_date_count
        },

        "configuration": {
            "minimum_history_months": MIN_HISTORY_MONTHS,
            "forecast_horizons": ALLOWED_HORIZONS,
            "frequency": "monthly",
            "model": "Holt's Damped Trend Exponential Smoothing",
            "missing_month_handling": "preserve_and_report"
        }
    }
