
import pandas as pd
import numpy as np

from app.services.business_diagnostic_service import detect_column_mapping


def safe_number(value):
    """Convert numeric values into JSON-safe Python numbers."""

    if value is None or pd.isna(value):
        return None

    value = float(value)

    if not np.isfinite(value):
        return None

    return round(value, 2)


def get_category_column(df, mapping):
    """Find the most useful categorical dimension."""

    category_roles = [
        "product",
        "region",
        "category",
        "channel",
        "department",
        "customer"
    ]

    for role in category_roles:
        if role in mapping:
            column = mapping[role]

            if df[column].nunique(dropna=True) >= 2:
                return column

    return None


def analyze_dataset_analytics(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    category_value=None
):
    """
    Generate analytics using optional date and category filters.

    All KPIs, charts, and summaries use the same filtered dataset.
    """

    mapping = detect_column_mapping(df)

    # Identify filter columns from the original dataset.
    date_column = mapping.get("date")
    category_column = get_category_column(df, mapping)

    # -------------------------------------------------
    # 1. Prepare filter options from original data
    # -------------------------------------------------

    date_series = None

    if date_column:
        date_series = pd.to_datetime(
            df[date_column],
            errors="coerce",
            format="mixed"
        )

    available_start_date = None
    available_end_date = None

    if date_series is not None and date_series.notna().any():
        available_start_date = date_series.min().strftime("%Y-%m-%d")
        available_end_date = date_series.max().strftime("%Y-%m-%d")

    category_options = []

    if category_column:
        category_options = sorted(
            df[category_column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    # -------------------------------------------------
    # 2. Apply filters
    # -------------------------------------------------

    filtered_df = df.copy()

    if date_series is not None:
        if start_date:
            start = pd.to_datetime(start_date, errors="coerce")

            if pd.notna(start):
                filtered_df = filtered_df.loc[
                    date_series >= start
                ]

        if end_date:
            end = pd.to_datetime(end_date, errors="coerce")

            if pd.notna(end):
                filtered_df = filtered_df.loc[
                    date_series <= end + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
                ]

    if category_value and category_column:
        filtered_df = filtered_df.loc[
            filtered_df[category_column].astype(str) == str(category_value)
        ]

    # -------------------------------------------------
    # 3. General dataset KPIs
    # -------------------------------------------------

    revenue = None
    profit = None

    if "revenue" in mapping:
        revenue = pd.to_numeric(
            filtered_df[mapping["revenue"]],
            errors="coerce"
        )

    if "profit" in mapping:
        profit = pd.to_numeric(
            filtered_df[mapping["profit"]],
            errors="coerce"
        )

    kpis = [
        {
            "label": "Total Records",
            "value": int(len(filtered_df)),
            "format": "number"
        },
        {
            "label": "Total Columns",
            "value": int(len(filtered_df.columns)),
            "format": "number"
        }
    ]

    if revenue is not None:
        kpis.extend([
            {
                "label": "Total Revenue",
                "value": safe_number(revenue.sum()),
                "format": "currency",
                "column": str(mapping["revenue"])
            },
            {
                "label": "Average Revenue",
                "value": safe_number(revenue.mean()),
                "format": "currency",
                "column": str(mapping["revenue"])
            }
        ])

    if profit is not None:
        kpis.append({
            "label": "Total Profit",
            "value": safe_number(profit.sum()),
            "format": "currency",
            "column": str(mapping["profit"])
        })

        if revenue is not None:
            total_revenue = revenue.sum()
            total_profit = profit.sum()

            margin = (
                (total_profit / total_revenue) * 100
                if total_revenue != 0
                else None
            )

            kpis.append({
                "label": "Profit Margin",
                "value": safe_number(margin),
                "format": "percentage"
            })

    # -------------------------------------------------
    # 4. Monthly revenue and profit trend
    # -------------------------------------------------

    monthly_trend = []

    if date_column and (revenue is not None or profit is not None):

        trend_data = pd.DataFrame({
            "date": pd.to_datetime(
                filtered_df[date_column],
                errors="coerce"
            )
        })

        if revenue is not None:
            trend_data["revenue"] = revenue

        if profit is not None:
            trend_data["profit"] = profit

        trend_data = trend_data.dropna(subset=["date"])

        if not trend_data.empty:
            trend_data["month"] = (
                trend_data["date"].dt.to_period("M").astype(str)
            )

            aggregations = {}

            if revenue is not None:
                aggregations["revenue"] = "sum"

            if profit is not None:
                aggregations["profit"] = "sum"

            grouped = (
                trend_data.groupby("month")
                .agg(aggregations)
                .reset_index()
                .sort_values("month")
            )

            for _, row in grouped.iterrows():
                item = {"month": str(row["month"])}

                if revenue is not None:
                    item["revenue"] = safe_number(row["revenue"])

                if profit is not None:
                    item["profit"] = safe_number(row["profit"])

                monthly_trend.append(item)

    # -------------------------------------------------
    # 5. Category comparison
    # -------------------------------------------------

    category_comparison = []
    category_metric_name = None

    if category_column:

        if revenue is not None:
            category_metric = revenue
            category_metric_name = "revenue"

        elif profit is not None:
            category_metric = profit
            category_metric_name = "profit"

        else:
            category_metric = None

            for column in filtered_df.select_dtypes(
                include="number"
            ).columns:

                category_metric = pd.to_numeric(
                    filtered_df[column],
                    errors="coerce"
                )

                category_metric_name = str(column)
                break

        if category_metric is not None:
            comparison_data = pd.DataFrame({
                "category": filtered_df[category_column].astype("string"),
                "value": category_metric
            }).dropna()

            grouped = (
                comparison_data.groupby("category")["value"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            category_comparison = [
                {
                    "category": str(category),
                    "value": safe_number(value)
                }
                for category, value in grouped.items()
            ]

    # -------------------------------------------------
    # 6. Numeric column summaries
    # -------------------------------------------------

    numeric_summaries = []

    for column in filtered_df.select_dtypes(include="number").columns:

        values = pd.to_numeric(
            filtered_df[column],
            errors="coerce"
        )

        numeric_summaries.append({
            "column": str(column),
            "mean": safe_number(values.mean()),
            "median": safe_number(values.median()),
            "min": safe_number(values.min()),
            "max": safe_number(values.max())
        })

    # -------------------------------------------------
    # 7. Final response
    # -------------------------------------------------

    return {
        "kpis": kpis,
        "monthly_trend": monthly_trend,
        "category_comparison": category_comparison,
        "category_column": (
            str(category_column) if category_column else None
        ),
        "category_metric": category_metric_name,
        "numeric_summaries": numeric_summaries,
        "column_mapping": {
            role: str(column)
            for role, column in mapping.items()
        },
        "filters": {
            "date_column": str(date_column) if date_column else None,
            "category_column": (
                str(category_column) if category_column else None
            ),
            "category_options": category_options[:200],
            "available_start_date": available_start_date,
            "available_end_date": available_end_date,
            "selected_start_date": start_date,
            "selected_end_date": end_date,
            "selected_category": category_value or "All",
            "total_records": int(len(df)),
            "filtered_records": int(len(filtered_df))
        }
    }
