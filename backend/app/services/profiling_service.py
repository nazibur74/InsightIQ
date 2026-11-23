import pandas as pd
import numpy as np


def analyze_dataset(df: pd.DataFrame):

    rows, columns = df.shape

    missing_values = df.isnull().sum()

    duplicate_count = int(df.duplicated().sum())

    column_profiles = []

    for column in df.columns:

        series = df[column]

        profile = {
            "name": str(column),
            "data_type": str(series.dtype),
            "missing_values": int(series.isnull().sum()),
            "missing_percentage": round(
                float(series.isnull().mean() * 100), 2
            ),
            "unique_values": int(series.nunique()),
        }

        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()

            profile["statistics"] = {
                "mean": round(float(clean.mean()), 2)
                if not clean.empty else None,
                "median": round(float(clean.median()), 2)
                if not clean.empty else None,
                "min": float(clean.min())
                if not clean.empty else None,
                "max": float(clean.max())
                if not clean.empty else None,
                "std": round(float(clean.std()), 2)
                if not clean.empty else None,
            }

        column_profiles.append(profile)

    total_cells = rows * columns

    total_missing = int(missing_values.sum())

    missing_percentage = (
        round((total_missing / total_cells) * 100, 2)
        if total_cells else 0
    )

    return {
        "overview": {
            "total_rows": rows,
            "total_columns": columns,
            "total_cells": total_cells,
            "missing_values": total_missing,
            "missing_percentage": missing_percentage,
            "duplicate_rows": duplicate_count,
            "memory_usage_bytes": int(
                df.memory_usage(deep=True).sum()
            )
        },
        "columns": column_profiles,
        "column_names": [str(col) for col in df.columns]
    }
