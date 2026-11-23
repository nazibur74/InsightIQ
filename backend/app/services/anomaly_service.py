
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def analyze_anomalies(df: pd.DataFrame):
    MIN_IQR_RECORDS = 8
    MIN_IF_RECORDS = 20
    IQR_MULTIPLIER = 1.5

    # Reset the index so row numbers consistently match uploaded file rows.
    data = df.reset_index(drop=True)

    numeric_data = pd.DataFrame(index=data.index)

    # Select suitable numerical columns.
    for column in data.columns:
        values = pd.to_numeric(data[column], errors="coerce")

        if (
            values.notna().sum() >= MIN_IQR_RECORDS
            and values.nunique(dropna=True) >= 4
        ):
            numeric_data[str(column)] = values

    if numeric_data.empty:
        return {
            "status": "insufficient_data",
            "message": (
                "No suitable numerical columns with enough "
                "observations were found for anomaly detection."
            ),
            "total_records": len(data),
            "anomaly_count": 0,
            "anomaly_percentage": 0,
            "severity_counts": {
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "column_anomalies": [],
            "records": [],
            "methods": ["IQR", "Isolation Forest"]
        }

    column_anomalies = []
    flagged_rows = {}

    # -------------------------------------------------
    # 1. IQR ANOMALY DETECTION
    # -------------------------------------------------
    for column in numeric_data.columns:

        values = numeric_data[column].dropna()

        if len(values) < MIN_IQR_RECORDS:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        if not np.isfinite(iqr) or iqr <= 0:
            continue

        lower_bound = q1 - IQR_MULTIPLIER * iqr
        upper_bound = q3 + IQR_MULTIPLIER * iqr

        mask = (
            (numeric_data[column] < lower_bound)
            | (numeric_data[column] > upper_bound)
        )

        anomaly_indices = numeric_data.index[mask].tolist()

        for index in anomaly_indices:

            value = float(numeric_data.loc[index, column])

            if index not in flagged_rows:
                flagged_rows[index] = {
                    "row_number": int(index) + 1,
                    "reasons": [],
                    "methods": []
                }

            flagged_rows[index]["reasons"].append({
                "column": column,
                "value": round(value, 4),
                "lower_bound": round(float(lower_bound), 4),
                "upper_bound": round(float(upper_bound), 4)
            })

            if "IQR" not in flagged_rows[index]["methods"]:
                flagged_rows[index]["methods"].append("IQR")

        column_anomalies.append({
            "column": column,
            "method": "IQR",
            "observations": int(len(values)),
            "anomaly_count": len(anomaly_indices),
            "lower_bound": round(float(lower_bound), 4),
            "upper_bound": round(float(upper_bound), 4),
            "anomaly_indices": [
                int(index) + 1 for index in anomaly_indices
            ]
        })

    # -------------------------------------------------
    # 2. ISOLATION FOREST ANOMALY DETECTION
    # -------------------------------------------------
    if len(numeric_data.columns) >= 2:

        model_data = (
            numeric_data
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
        )

        if len(model_data) >= MIN_IF_RECORDS:

            model = IsolationForest(
                n_estimators=100,
                contamination="auto",
                random_state=42
            )

            predictions = model.fit_predict(model_data)
            scores = model.decision_function(model_data)

            for index, prediction, score in zip(
                model_data.index,
                predictions,
                scores
            ):

                if prediction == -1:

                    if index not in flagged_rows:
                        flagged_rows[index] = {
                            "row_number": int(index) + 1,
                            "reasons": [],
                            "methods": []
                        }

                    if (
                        "Isolation Forest"
                        not in flagged_rows[index]["methods"]
                    ):
                        flagged_rows[index]["methods"].append(
                            "Isolation Forest"
                        )

                    flagged_rows[index]["anomaly_score"] = round(
                        float(score), 4
                    )

                    # Store the numerical features considered by the model.
                    flagged_rows[index]["isolation_forest_features"] = {
                        column: round(float(model_data.loc[index, column]), 4)
                        for column in model_data.columns
                    }

    # -------------------------------------------------
    # 3. EXPLANATIONS AND SEVERITY CLASSIFICATION
    # -------------------------------------------------
    severity_counts = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for record in flagged_rows.values():

        reasons = record["reasons"]
        methods = record["methods"]
        anomaly_score = record.get("anomaly_score")

        explanations = []

        if reasons:
            unusual_columns = [
                reason["column"] for reason in reasons
            ]

            explanations.append(
                "Unusual numerical values detected in: "
                + ", ".join(unusual_columns)
                + "."
            )

        if (
            "Isolation Forest" in methods
            and not reasons
        ):
            explanations.append(
                "An unusual combination of numerical values was "
                "identified by Isolation Forest."
            )

        elif "Isolation Forest" in methods:
            explanations.append(
                "Isolation Forest also identified this record "
                "as unusual based on its numerical feature pattern."
            )

        # Severity is a heuristic, not a measure of business loss.
        if (
            len(reasons) >= 2
            or (
                anomaly_score is not None
                and anomaly_score <= -0.15
            )
        ):
            severity = "high"
            severity_reason = (
                "Multiple unusual numerical values or a strongly "
                "unusual Isolation Forest score."
            )

        elif reasons or (
            anomaly_score is not None
            and anomaly_score <= -0.05
        ):
            severity = "medium"
            severity_reason = (
                "At least one statistical outlier or a moderately "
                "unusual Isolation Forest score."
            )

        else:
            severity = "low"
            severity_reason = (
                "Flagged by Isolation Forest, but without a strong "
                "statistical outlier signal."
            )

        record["explanation"] = " ".join(explanations)
        record["severity"] = severity
        record["severity_reason"] = severity_reason

        severity_counts[severity] += 1

    # -------------------------------------------------
    # 4. FINAL RESPONSE
    # -------------------------------------------------
    records = sorted(
        flagged_rows.values(),
        key=lambda item: item["row_number"]
    )

    anomaly_count = len(records)
    total_records = len(data)

    status = (
        "completed"
        if total_records >= MIN_IQR_RECORDS
        else "insufficient_data"
    )

    return {
        "status": status,
        "message": (
            "Anomaly detection completed."
            if status == "completed"
            else "More records are needed for reliable detection."
        ),
        "total_records": total_records,
        "anomaly_count": anomaly_count,
        "anomaly_percentage": round(
            (anomaly_count / total_records) * 100, 2
        ) if total_records else 0,
        "severity_counts": severity_counts,
        "column_anomalies": column_anomalies,
        "records": records,
        "methods": ["IQR", "Isolation Forest"],
        "configuration": {
            "iqr_multiplier": IQR_MULTIPLIER,
            "minimum_iqr_records": MIN_IQR_RECORDS,
            "minimum_isolation_forest_records": MIN_IF_RECORDS,
            "severity_rules": {
                "high": "2 or more IQR reasons, or score <= -0.15",
                "medium": "At least 1 IQR reason, or score <= -0.05",
                "low": "Isolation Forest flag without the above conditions"
            }
        }
    }
