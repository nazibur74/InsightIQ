import re
import pandas as pd
import numpy as np


# Recognize common column names across different business datasets.
COLUMN_PATTERNS = {
    "date": r"\b(date|time|timestamp|order_date|created_at|transaction_date)\b",
    "revenue": r"(sales|revenue|turnover|total_amount|order_value|gross_amount)",
    "profit": r"(profit|net_income|earnings|margin_amount)",
    "cost": r"(cost|expense|expenditure|purchase_amount)",
    "quantity": r"(quantity|qty|units_sold|units|order_count)",
    "inventory": r"(stock|inventory|available_quantity|stock_level)",
    "discount": r"(discount|markdown|promotion_amount)",
    "product": r"(product|item|sku|service_name)",
    "region": r"(region|city|country|state|location|territory)",
    "category": r"(category|segment|type|classification)",
    "customer": r"(customer|client|buyer|consumer)",
    "department": r"(department|team|division)",
    "employee": r"(employee|staff|worker|personnel)",
    "campaign": r"(campaign|ad_spend|advertising)",
    "channel": r"(channel|platform|source|medium)",
}


def detect_column_mapping(df):
    """Identify likely business columns using column names and data types."""

    mapping = {}

    for role, pattern in COLUMN_PATTERNS.items():
        for column in df.columns:
            column_name = str(column).strip().lower()

            if re.search(pattern, column_name):
                mapping[role] = column
                break

    return mapping


def detect_business_domain(mapping):
    """Estimate the dataset's business domain from detected columns."""

    if "employee" in mapping or "department" in mapping:
        return "HR"

    if "inventory" in mapping:
        return "Inventory"

    if "campaign" in mapping or "channel" in mapping:
        return "Marketing"

    if "profit" in mapping or "revenue" in mapping or "cost" in mapping:
        return "Sales / Finance"

    if "quantity" in mapping or "product" in mapping:
        return "Sales / Operations"

    return "General Business"


def numeric_column(df, column):
    """Convert a column into numeric values safely."""

    if column not in df.columns:
        return None

    return pd.to_numeric(df[column], errors="coerce")


def analyze_business_diagnostics(df):
    """
    Detect potential business problems using deterministic rules.
    Findings are based on available data, not assumed business context.
    """

    findings = []
    mapping = detect_column_mapping(df)
    domain = detect_business_domain(mapping)

    def add_finding(
        title,
        severity,
        description,
        recommendation,
        metric=None,
        value=None,
        evidence=None
    ):
        findings.append({
            "title": title,
            "severity": severity,
            "description": description,
            "recommendation": recommendation,
            "metric": metric,
            "value": value,
            "evidence": evidence or {}
        })

    # -------------------------------------------------
    # 1. Negative profit
    # -------------------------------------------------

    if "profit" in mapping:
        profit = numeric_column(df, mapping["profit"])
        negative_profit = profit < 0
        count = int(negative_profit.sum())

        if count > 0:
            add_finding(
                title="Negative Profit Detected",
                severity="high",
                description=(
                    f"{count} records contain negative profit values. "
                    "These records may represent losses."
                ),
                recommendation=(
                    "Review the affected transactions, pricing, "
                    "costs, and operational expenses."
                ),
                metric=str(mapping["profit"]),
                value=count,
                evidence={
                    "affected_records": count,
                    "total_records": len(df)
                }
            )

    # -------------------------------------------------
    # 2. Negative revenue
    # -------------------------------------------------

    if "revenue" in mapping:
        revenue = numeric_column(df, mapping["revenue"])
        negative_revenue = revenue < 0
        count = int(negative_revenue.sum())

        if count > 0:
            add_finding(
                title="Negative Revenue Values",
                severity="high",
                description=(
                    f"{count} records contain negative revenue values."
                ),
                recommendation=(
                    "Check whether these values represent refunds, "
                    "returns, reversals, or incorrect entries."
                ),
                metric=str(mapping["revenue"]),
                value=count,
                evidence={
                    "affected_records": count,
                    "total_records": len(df)
                }
            )

    # -------------------------------------------------
    # 3. Zero revenue
    # -------------------------------------------------

    if "revenue" in mapping:
        revenue = numeric_column(df, mapping["revenue"])
        zero_revenue = revenue == 0
        count = int(zero_revenue.sum())

        if count > 0:
            add_finding(
                title="Zero Revenue Records",
                severity="medium",
                description=(
                    f"{count} records have zero revenue."
                ),
                recommendation=(
                    "Check whether these are cancelled orders, "
                    "free transactions, or incomplete sales records."
                ),
                metric=str(mapping["revenue"]),
                value=count,
                evidence={
                    "affected_records": count
                }
            )

    # -------------------------------------------------
    # 4. Negative quantity
    # -------------------------------------------------

    if "quantity" in mapping:
        quantity = numeric_column(df, mapping["quantity"])
        count = int((quantity < 0).sum())

        if count > 0:
            add_finding(
                title="Negative Quantity Detected",
                severity="medium",
                description=(
                    f"{count} records contain negative quantities."
                ),
                recommendation=(
                    "Review returns, adjustments, and transaction records."
                ),
                metric=str(mapping["quantity"]),
                value=count,
                evidence={
                    "affected_records": count
                }
            )

    # -------------------------------------------------
    # 5. Zero or negative inventory
    # -------------------------------------------------

    if "inventory" in mapping:
        inventory = numeric_column(df, mapping["inventory"])
        unavailable = inventory <= 0
        count = int(unavailable.sum())

        if count > 0:
            add_finding(
                title="Zero or Negative Inventory",
                severity="high",
                description=(
                    f"{count} records have zero or negative stock levels."
                ),
                recommendation=(
                    "Review stock availability and investigate "
                    "potential stockouts or inventory recording errors."
                ),
                metric=str(mapping["inventory"]),
                value=count,
                evidence={
                    "affected_records": count
                }
            )

    # -------------------------------------------------
    # 6. Profit margin analysis
    # -------------------------------------------------

    if "revenue" in mapping and "profit" in mapping:
        revenue = numeric_column(df, mapping["revenue"])
        profit = numeric_column(df, mapping["profit"])

        valid = revenue > 0
        valid = valid & profit.notna()

        if valid.any():
            margins = (profit[valid] / revenue[valid]) * 100

            negative_margins = int((margins < 0).sum())
            unusually_high = int((margins > 100).sum())

            if negative_margins > 0:
                add_finding(
                    title="Negative Profit Margins",
                    severity="high",
                    description=(
                        f"{negative_margins} records have negative "
                        "profit margins."
                    ),
                    recommendation=(
                        "Review pricing, discounts, and costs "
                        "for the affected transactions."
                    ),
                    metric="Profit Margin",
                    value=negative_margins,
                    evidence={
                        "affected_records": negative_margins
                    }
                )

            if unusually_high > 0:
                add_finding(
                    title="Unusually High Profit Margins",
                    severity="medium",
                    description=(
                        f"{unusually_high} records have profit margins "
                        "above 100%."
                    ),
                    recommendation=(
                        "Verify revenue and profit calculations, "
                        "and check whether both metrics use consistent units."
                    ),
                    metric="Profit Margin",
                    value=unusually_high,
                    evidence={
                        "affected_records": unusually_high
                    }
                )

    # -------------------------------------------------
    # 7. Revenue trend analysis
    # -------------------------------------------------

    if "date" in mapping and "revenue" in mapping:
        dates = pd.to_datetime(
            df[mapping["date"]],
            errors="coerce"
        )

        revenue = numeric_column(df, mapping["revenue"])

        trend_data = pd.DataFrame({
            "date": dates,
            "revenue": revenue
        }).dropna()

        if not trend_data.empty:
            trend_data["period"] = (
                trend_data["date"].dt.to_period("M")
            )

            monthly_revenue = (
                trend_data.groupby("period")["revenue"].sum()
                .sort_index()
            )

            if len(monthly_revenue) >= 3:
                first = float(monthly_revenue.iloc[0])
                last = float(monthly_revenue.iloc[-1])

                if first > 0:
                    decline = ((first - last) / first) * 100

                    if decline >= 20:
                        add_finding(
                            title="Revenue Declining Over Time",
                            severity="high",
                            description=(
                                f"Revenue in the latest month is "
                                f"{decline:.1f}% lower than in the first "
                                "month of the available data."
                            ),
                            recommendation=(
                                "Investigate changes in sales volume, "
                                "pricing, customer demand, and seasonality."
                            ),
                            metric="Monthly Revenue",
                            value=round(decline, 2),
                            evidence={
                                "first_month_revenue": round(first, 2),
                                "latest_month_revenue": round(last, 2),
                                "months_analyzed": len(monthly_revenue)
                            }
                        )

    # -------------------------------------------------
    # 8. Revenue concentration by product or region
    # -------------------------------------------------

    if "revenue" in mapping and len(df) >= 10:
        revenue = numeric_column(df, mapping["revenue"])

        for role in ["product", "region", "category"]:
            if role not in mapping:
                continue

            group_column = mapping[role]

            grouped = pd.DataFrame({
                "group": df[group_column],
                "revenue": revenue
            }).dropna()

            if grouped["group"].nunique() < 2:
                continue

            total_revenue = grouped["revenue"].sum()

            if total_revenue <= 0:
                continue

            group_revenue = (
                grouped.groupby("group")["revenue"].sum()
                .sort_values(ascending=False)
            )

            top_group = group_revenue.index[0]
            share = (
                group_revenue.iloc[0] / total_revenue
            ) * 100

            if share >= 60:
                add_finding(
                    title=f"High Revenue Concentration by {role.title()}",
                    severity="medium",
                    description=(
                        f"{share:.1f}% of total revenue comes from "
                        f"one {role}: {top_group}."
                    ),
                    recommendation=(
                        "Review dependency on this segment and explore "
                        "opportunities to diversify revenue."
                    ),
                    metric=str(group_column),
                    value=round(float(share), 2),
                    evidence={
                        "top_group": str(top_group),
                        "revenue_share_percentage": round(float(share), 2)
                    }
                )

    # -------------------------------------------------
    # 9. Result summary
    # -------------------------------------------------

    severity_counts = {
        "high": sum(
            1 for item in findings if item["severity"] == "high"
        ),
        "medium": sum(
            1 for item in findings if item["severity"] == "medium"
        ),
        "low": sum(
            1 for item in findings if item["severity"] == "low"
        )
    }

    return {
        "detected_domain": domain,
        "column_mapping": {
            role: str(column)
            for role, column in mapping.items()
        },
        "total_findings": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "method": (
            "Rule-based business diagnostics using column-name "
            "matching, data types, and numerical patterns. "
            "Findings are potential issues and should be reviewed."
        )
    }
