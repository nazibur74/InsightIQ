import pandas as pd
import numpy as np
import re


def analyze_data_quality(df: pd.DataFrame):

    issues = []
    rows, columns = df.shape

    def add_issue(
        title,
        severity,
        category,
        description,
        recommendation,
        column=None,
        affected_rows=0
    ):
        issues.append({
            "title": title,
            "severity": severity,
            "category": category,
            "description": description,
            "recommendation": recommendation,
            "column": column,
            "affected_rows": int(affected_rows)
        })

    # 1. Missing values
    for col in df.columns:

        missing = int(df[col].isna().sum())

        if missing > 0:
            percentage = (missing / max(rows, 1)) * 100

            severity = (
                "high" if percentage >= 20
                else "medium" if percentage >= 5
                else "low"
            )

            add_issue(
                title="Missing Values Detected",
                severity=severity,
                category="completeness",
                description=(
                    f"{missing} missing values found in "
                    f"'{col}' ({percentage:.2f}%)."
                ),
                recommendation=(
                    "Investigate missing records and consider "
                    "imputation or removal based on business context."
                ),
                column=str(col),
                affected_rows=missing
            )

    # 2. Duplicate records
    duplicates = int(df.duplicated().sum())

    if duplicates > 0:

        percentage = duplicates / max(rows, 1) * 100

        add_issue(
            title="Duplicate Records Detected",
            severity="high" if percentage >= 5 else "medium",
            category="uniqueness",
            description=(
                f"{duplicates} duplicate rows found "
                f"({percentage:.2f}% of records)."
            ),
            recommendation=(
                "Review duplicate records before removing them. "
                "Some repeated transactions may be legitimate."
            ),
            affected_rows=duplicates
        )

    # 3. Blank strings
    for col in df.select_dtypes(include=["object", "string"]).columns:

        blank_mask = df[col].apply(
            lambda value: isinstance(value, str)
            and value.strip() == ""
        )

        blank_count = int(blank_mask.sum())

        if blank_count > 0:

            add_issue(
                title="Blank Text Values",
                severity="medium",
                category="completeness",
                description=(
                    f"{blank_count} blank or whitespace-only "
                    f"values found in '{col}'."
                ),
                recommendation=(
                    "Convert blank strings to missing values "
                    "and handle them appropriately."
                ),
                column=str(col),
                affected_rows=blank_count
            )

    # 4. Inconsistent categorical values
    for col in df.select_dtypes(include=["object", "string"]).columns:

        values = df[col].dropna()

        if len(values) == 0 or values.nunique() > 100:
            continue

        normalized = values.astype(str).str.strip().str.lower()

        variants = (
            pd.DataFrame({
                "original": values.astype(str),
                "normalized": normalized
            })
            .groupby("normalized")["original"]
            .nunique()
        )

        inconsistent = int((variants > 1).sum())

        if inconsistent > 0:

            add_issue(
                title="Inconsistent Category Formatting",
                severity="medium",
                category="consistency",
                description=(
                    f"'{col}' contains {inconsistent} groups "
                    "of values that differ only by capitalization "
                    "or surrounding whitespace."
                ),
                recommendation=(
                    "Standardize category formatting after "
                    "confirming that these values represent "
                    "the same category."
                ),
                column=str(col),
                affected_rows=int(
                    normalized.isin(
                        variants[variants > 1].index
                    ).sum()
                )
            )

    # 5. Numeric values stored as text
    for col in df.select_dtypes(include=["object", "string"]).columns:

        values = df[col].dropna().astype(str).str.strip()

        if len(values) < 2:
            continue

        numeric_values = pd.to_numeric(
            values.str.replace(",", "", regex=False),
            errors="coerce"
        )

        ratio = numeric_values.notna().mean()

        if 0.8 <= ratio < 1:

            add_issue(
                title="Possible Numeric Type Mismatch",
                severity="medium",
                category="validity",
                description=(
                    f"'{col}' appears to contain numeric values "
                    "stored as text, with some non-numeric entries."
                ),
                recommendation=(
                    "Inspect non-numeric values and convert "
                    "the column to a numeric type if appropriate."
                ),
                column=str(col),
                affected_rows=int(numeric_values.isna().sum())
            )

    # 6. Constant columns
    for col in df.columns:

        unique_count = int(df[col].nunique(dropna=False))

        if rows > 1 and unique_count <= 1:

            add_issue(
                title="Constant Column Detected",
                severity="low",
                category="relevance",
                description=(
                    f"'{col}' contains only one distinct value."
                ),
                recommendation=(
                    "Check whether this column is necessary "
                    "for analysis."
                ),
                column=str(col),
                affected_rows=rows
            )

    # 7. Invalid infinite numeric values
    for col in df.select_dtypes(include=[np.number]).columns:

        invalid_count = int(
            np.isinf(df[col].dropna()).sum()
        )

        if invalid_count > 0:

            add_issue(
                title="Infinite Numeric Values",
                severity="high",
                category="validity",
                description=(
                    f"{invalid_count} infinite values found "
                    f"in '{col}'."
                ),
                recommendation=(
                    "Investigate calculations and replace "
                    "infinite values with valid values or missing data."
                ),
                column=str(col),
                affected_rows=invalid_count
            )

    # 8. Suspicious date columns
    date_pattern = re.compile(
        r"date|time|timestamp|created|updated",
        re.IGNORECASE
    )

    for col in df.columns:

        if not date_pattern.search(str(col)):
            continue

        if not (
            pd.api.types.is_object_dtype(df[col])
            or pd.api.types.is_string_dtype(df[col])
        ):
            continue

        values = df[col].dropna()

        if len(values) < 2:
            continue

        parsed = pd.to_datetime(
            values,
            errors="coerce",
            format="mixed"
        )

        invalid_count = int(parsed.isna().sum())

        if invalid_count > 0:

            add_issue(
                title="Potentially Invalid Date Values",
                severity="medium",
                category="validity",
                description=(
                    f"{invalid_count} values in '{col}' "
                    "could not be interpreted as dates."
                ),
                recommendation=(
                    "Inspect date formats and correct invalid "
                    "or inconsistent entries."
                ),
                column=str(col),
                affected_rows=invalid_count
            )

    # 9. Calculate transparent quality score
    penalties = {
        "high": 12,
        "medium": 6,
        "low": 2
    }

    total_penalty = sum(
        penalties[issue["severity"]]
        for issue in issues
    )

    quality_score = max(0, 100 - total_penalty)

    # 10. Quality summary
    severity_counts = {
        "high": sum(i["severity"] == "high" for i in issues),
        "medium": sum(i["severity"] == "medium" for i in issues),
        "low": sum(i["severity"] == "low" for i in issues)
    }

    return {
        "quality_score": quality_score,
        "total_issues": len(issues),
        "severity_counts": severity_counts,
        "issues": issues,
        "score_method": (
            "Heuristic score: 100 minus weighted detected "
            "issue penalties. Each issue is counted once."
        )
    }
