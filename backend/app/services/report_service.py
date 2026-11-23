from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
    PageBreak
)

# COLORS

NAVY = colors.HexColor("#1e3a8a")
BLUE = colors.HexColor("#2563eb")
LIGHT_BLUE = colors.HexColor("#eff6ff")
LIGHT_GREY = colors.HexColor("#f1f5f9")
BORDER = colors.HexColor("#cbd5e1")
DARK = colors.HexColor("#1e293b")
MUTED = colors.HexColor("#64748b")

# TEXT HELPERS

def safe_text(value):
    """Escape text safely for ReportLab Paragraphs."""
    if value is None:
        return "N/A"
    return escape(str(value))

def format_value(value):
    """Format numeric values without assuming a currency."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)

# TABLE GENERATOR

def create_table(headers, rows, col_widths=None):
    """Create a professional table with repeating headers."""
    data = [
        [
            Paragraph(
                safe_text(header),
                ParagraphStyle(
                    "TableHeader",
                    fontName="Helvetica-Bold",
                    fontSize=8,
                    leading=10,
                    textColor=colors.white
                )
            )
            for header in headers
        ]
    ]
    for row in rows:
        formatted_row = []
        for value in row:
            formatted_row.append(
                Paragraph(
                    safe_text(value),
                    ParagraphStyle(
                        "TableCell",
                        fontName="Helvetica",
                        fontSize=8,
                        leading=11,
                        textColor=DARK
                    )
                )
            )
        data.append(formatted_row)
    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT_GREY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table

# CHART HELPERS

def create_metric_chart(title, labels, values, series_label):
    """Create a compact monthly bar chart for one report metric."""
    if not labels or not values or len(labels) != len(values):
        return None

    numeric_values = []
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = None
        numeric_values.append(number)

    valid_pairs = [
        (label, value)
        for label, value in zip(labels, numeric_values)
        if value is not None
    ]
    if len(valid_pairs) < 2:
        return None

    chart_labels = [item[0] for item in valid_pairs]
    chart_values = [item[1] for item in valid_pairs]

    drawing = Drawing(480, 220)
    drawing.add(String(12, 202, title, fontName="Helvetica-Bold",
                       fontSize=10, fillColor=NAVY))

    chart = VerticalBarChart()
    chart.x = 48
    chart.y = 42
    chart.width = 410
    chart.height = 145
    chart.data = [chart_values]
    chart.categoryAxis.categoryNames = chart_labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = min(0, min(chart_values))
    chart.valueAxis.forceZero = True
    chart.bars[0].fillColor = BLUE
    chart.bars[0].strokeColor = BLUE
    chart.barSpacing = 5
    drawing.add(chart)
    drawing.add(String(48, 22, series_label, fontName="Helvetica",
                       fontSize=7, fillColor=MUTED))
    return drawing


def create_comparison_chart(title, labels, values, series_label):
    """Create a compact category/severity comparison chart."""
    if not labels or not values or len(labels) != len(values):
        return None

    pairs = []
    for label, value in zip(labels, values):
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        pairs.append((str(label), number))

    if len(pairs) < 1:
        return None

    chart_labels = [item[0] for item in pairs]
    chart_values = [item[1] for item in pairs]

    drawing = Drawing(480, 220)
    drawing.add(String(
        12, 202, title,
        fontName="Helvetica-Bold",
        fontSize=10,
        fillColor=NAVY
    ))

    chart = VerticalBarChart()
    chart.x = 48
    chart.y = 42
    chart.width = 410
    chart.height = 145
    chart.data = [chart_values]
    chart.categoryAxis.categoryNames = chart_labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.angle = 25
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = min(0, min(chart_values))
    chart.valueAxis.forceZero = True
    chart.bars[0].fillColor = BLUE
    chart.bars[0].strokeColor = BLUE
    chart.barSpacing = 7
    drawing.add(chart)
    drawing.add(String(
        48, 22, series_label,
        fontName="Helvetica",
        fontSize=7,
        fillColor=MUTED
    ))
    return drawing


def extract_category_comparison(analytics):
    """Read category comparison data across supported response shapes."""
    comparison = analytics.get("category_comparison", [])
    category_column = analytics.get("filters", {}).get("category_column")

    if isinstance(comparison, dict):
        category_column = (
            comparison.get("category_column")
            or comparison.get("column")
            or category_column
        )
        items = (
            comparison.get("data")
            or comparison.get("items")
            or comparison.get("results")
            or comparison.get("categories")
            or []
        )
        if not items and comparison.get("labels") and comparison.get("values"):
            items = [
                {"category": label, "revenue": value}
                for label, value in zip(
                    comparison["labels"], comparison["values"]
                )
            ]
    else:
        items = comparison

    labels = []
    values = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        label = (
            item.get("category")
            or item.get("name")
            or item.get("label")
            or item.get("value")
        )
        value = next(
            (
                item[key]
                for key in (
                    "revenue", "sales", "total_revenue",
                    "value", "amount", "total"
                )
                if item.get(key) is not None
            ),
            None
        )
        if label is not None and value is not None:
            labels.append(str(label))
            values.append(value)

    return category_column or "Category", labels, values


def create_forecast_chart(metric_name, metric):
    """Compare historical actuals with forecast values for one metric."""
    history = metric.get("history", [])
    forecast_values = metric.get("forecast", [])
    if not history or not forecast_values:
        return None

    actual_by_month = {
        str(item.get("month", "N/A")): item.get("actual")
        for item in history
        if item.get("month") is not None
    }
    predicted_by_month = {
        str(item.get("month", "N/A")): item.get("predicted")
        for item in forecast_values
        if item.get("month") is not None
    }
    labels = list(actual_by_month)
    labels.extend(
        month for month in predicted_by_month if month not in actual_by_month
    )

    actuals = []
    predictions = []
    for month in labels:
        try:
            actuals.append(float(actual_by_month.get(month) or 0))
        except (TypeError, ValueError):
            actuals.append(0)
        try:
            predictions.append(float(predicted_by_month.get(month) or 0))
        except (TypeError, ValueError):
            predictions.append(0)

    if not labels:
        return None

    drawing = Drawing(480, 220)
    drawing.add(String(
        12, 202, f"{metric_name.title()}: Actual vs Forecast",
        fontName="Helvetica-Bold",
        fontSize=10,
        fillColor=NAVY
    ))

    chart = VerticalBarChart()
    chart.x = 48
    chart.y = 42
    chart.width = 410
    chart.height = 145
    chart.data = [actuals, predictions]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = min(0, min(actuals + predictions))
    chart.valueAxis.forceZero = True
    chart.bars[0].fillColor = BLUE
    chart.bars[0].strokeColor = BLUE
    chart.bars[1].fillColor = colors.HexColor("#0f766e")
    chart.bars[1].strokeColor = colors.HexColor("#0f766e")
    chart.groupSpacing = 7
    drawing.add(chart)
    drawing.add(String(
        48, 22, "Blue: actual  |  Teal: forecast",
        fontName="Helvetica",
        fontSize=7,
        fillColor=MUTED
    ))
    return drawing


# MAIN PDF GENERATOR

def generate_pdf_report(
    filename,
    profile,
    quality,
    diagnostics,
    analytics,
    anomalies,
    forecast,
    ai_insights=None
):
    """
    Generate a professional InsightIQ business analysis PDF.
    """
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=22 * mm,
        title="InsightIQ Business Analysis Report",
        author="InsightIQ"
    )

# STYLES

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=31,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SubHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SmallBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=DARK,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="InsightHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=NAVY,
        spaceBefore=9,
        spaceAfter=5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="InsightBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        textColor=DARK,
        spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        name="InsightBullet",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        leftIndent=13,
        firstLineIndent=-9,
        textColor=DARK,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="FooterStyle",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MUTED,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name="CoverBrand",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.white,
        spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=33,
        textColor=colors.white,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#dbeafe")
    ))
    story = []

# HELPER FUNCTIONS

    def add_section(title):
        story.append(
            Paragraph(
                safe_text(title),
                styles["SectionHeading"]
            )
        )
    def add_subheading(title):
        story.append(
            Paragraph(
                safe_text(title),
                styles["SubHeading"]
            )
        )
    def add_text(value):
        story.append(
            Paragraph(
                safe_text(value),
                styles["SmallBody"]
            )
        )
    def add_section_with_table(title, headers, rows):
        """
        Keep the section heading with the beginning
        of its table. Long tables can continue onto
        subsequent pages.
        """
        heading = Paragraph(
            safe_text(title),
            styles["SectionHeading"]
        )
        table = create_table(headers, rows)
        story.append(
            KeepTogether([
                heading,
                Spacer(1, 2),
                table
            ])
        )
    # =================================================
    # PROFESSIONAL COVER PAGE
    overview = profile.get("overview", {})
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
    cover_panel = Table(
        [
            [Paragraph("INSIGHTIQ  |  AUTOMATED ANALYTICS", styles["CoverBrand"])],
            [Paragraph("Business Analysis<br/>Report", styles["CoverTitle"])],
            [Paragraph(
                "A structured view of your data, business performance, "
                "data quality and predictive outlook.",
                styles["CoverSubtitle"]
            )],
            [Spacer(1, 15)],
            [Paragraph(
                f"<b>DATASET</b><br/>{safe_text(filename)}",
                styles["CoverSubtitle"]
            )],
            [Paragraph(
                f"<b>GENERATED</b><br/>{safe_text(generated_at)}",
                styles["CoverSubtitle"]
            )]
        ],
        colWidths=[document.width],
        hAlign="LEFT"
    )
    cover_panel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING", (0, 0), (-1, 0), 25),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
    ]))
    story.append(Spacer(1, 28))
    story.append(cover_panel)
    story.append(Spacer(1, 24))
    quality_score = quality.get("quality_score", "N/A")
    findings_count = diagnostics.get("total_findings", 0)
    anomaly_count = anomalies.get("anomaly_count", 0)
    metric_data = [
        [
            Paragraph(
                f'<font color="#64748b" size="8">TOTAL RECORDS</font><br/>'
                f'<font color="#1e3a8a" size="19"><b>{safe_text(format_value(overview.get("total_rows")))}</b></font>',
                styles["CoverSubtitle"]
            ),
            Paragraph(
                f'<font color="#64748b" size="8">DATA QUALITY</font><br/>'
                f'<font color="#1e3a8a" size="19"><b>{safe_text(format_value(quality_score))}</b></font>'
                f'<font color="#64748b" size="8"> / 100</font>',
                styles["CoverSubtitle"]
            )
        ],
        [
            Paragraph(
                f'<font color="#64748b" size="8">BUSINESS FINDINGS</font><br/>'
                f'<font color="#1e3a8a" size="19"><b>{safe_text(format_value(findings_count))}</b></font>',
                styles["CoverSubtitle"]
            ),
            Paragraph(
                f'<font color="#64748b" size="8">DETECTED ANOMALIES</font><br/>'
                f'<font color="#1e3a8a" size="19"><b>{safe_text(format_value(anomaly_count))}</b></font>',
                styles["CoverSubtitle"]
            )
        ]
    ]
    metric_table = Table(
        metric_data,
        colWidths=[document.width / 2, document.width / 2],
        rowHeights=[68, 68]
    )
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.7, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Prepared by InsightIQ",
        styles["FooterStyle"]
    ))
    story.append(PageBreak())
    # 1. DATASET OVERVIEW
    # =================================================
    overview = profile.get("overview", {})
    overview_rows = [
        ["Total Rows", format_value(overview.get("total_rows"))],
        ["Total Columns", format_value(overview.get("total_columns"))],
        ["Total Cells", format_value(overview.get("total_cells"))],
        ["Missing Values", format_value(overview.get("missing_values"))],
        ["Duplicate Rows", format_value(overview.get("duplicate_rows"))],
        ["Memory Usage (Bytes)", format_value(
            overview.get("memory_usage_bytes")
        )],
    ]
    add_section_with_table(
        "1. Dataset Overview",
        ["Metric", "Value"],
        overview_rows
    )
    # Column Profiles
    add_subheading("Column Profiles")
    column_rows = []
    for column in profile.get("columns", []):
        column_rows.append([
            column.get("name", "N/A"),
            column.get("data_type", "N/A"),
            format_value(column.get("missing_values", 0)),
            format_value(column.get("unique_values"))
        ])
    if column_rows:
        story.append(
            create_table(
                ["Column", "Data Type", "Missing", "Unique Values"],
                column_rows
            )
        )
    else:
        add_text("No column profile information available.")
    # =================================================
    # 2. DATA QUALITY
    # =================================================
    add_section("2. Data Quality Analysis")
    add_text(
        f"Quality Score: {quality.get('quality_score', 'N/A')}/100"
    )
    add_text(
        f"Total Issues: {quality.get('total_issues', 0)}"
    )
    severity = quality.get("severity_counts", {})
    add_text(
        f"High: {severity.get('high', 0)} | "
        f"Medium: {severity.get('medium', 0)} | "
        f"Low: {severity.get('low', 0)}"
    )
    issue_rows = []
    for issue in quality.get("issues", []):
        issue_rows.append([
            issue.get("type", issue.get("issue", "Issue")),
            issue.get("severity", "N/A"),
            issue.get(
                "description",
                issue.get("message", "N/A")
            )
        ])
    if issue_rows:
        story.append(
            KeepTogether([
                Paragraph(
                    "Detected Data Quality Issues",
                    styles["SubHeading"]
                ),
                create_table(
                    ["Issue", "Severity", "Description"],
                    issue_rows
                )
            ])
        )
    else:
        add_text("No data quality issues detected.")
    # =================================================
    # 3. BUSINESS DIAGNOSTICS
    # =================================================
    add_section("3. Business Diagnostics")
    add_text(
        f"Detected Domain: "
        f"{diagnostics.get('detected_domain', 'N/A')}"
    )
    add_text(
        f"Total Findings: {diagnostics.get('total_findings', 0)}"
    )
    finding_rows = []
    for finding in diagnostics.get("findings", []):
        finding_rows.append([
            finding.get(
                "title",
                finding.get("name", "Finding")
            ),
            finding.get("severity", "N/A"),
            finding.get("description", "N/A")
        ])
    if finding_rows:
        story.append(
            KeepTogether([
                Paragraph(
                    "Detected Business Findings",
                    styles["SubHeading"]
                ),
                create_table(
                    ["Finding", "Severity", "Description"],
                    finding_rows
                )
            ])
        )
    else:
        add_text("No business diagnostic findings detected.")
    # =================================================
    # 4. BUSINESS ANALYTICS
    # =================================================
    kpi_rows = []
    for kpi in analytics.get("kpis", []):
        kpi_rows.append([
            kpi.get("label", "N/A"),
            format_value(kpi.get("value")),
            kpi.get("format", "N/A")
        ])
    if kpi_rows:
        add_section_with_table(
            "4. Business Analytics",
            ["Key Performance Indicator", "Value", "Format"],
            kpi_rows
        )
    else:
        add_section("4. Business Analytics")
        add_text("No KPI information available.")
    # Monthly Performance
    trend_rows = []
    for item in analytics.get("monthly_trend", []):
        trend_rows.append([
            item.get("month", "N/A"),
            format_value(item.get("revenue")),
            format_value(item.get("profit"))
        ])
    if trend_rows:
        add_section_with_table(
            "Monthly Performance",
            ["Month", "Revenue", "Profit"],
            trend_rows
        )

        trend_months = [item.get("month", "N/A") for item in analytics.get("monthly_trend", [])]
        revenue_values = [item.get("revenue") for item in analytics.get("monthly_trend", [])]
        profit_values = [item.get("profit") for item in analytics.get("monthly_trend", [])]

        revenue_chart = create_metric_chart(
            "Monthly Revenue Trend", trend_months, revenue_values, "Revenue"
        )
        profit_chart = create_metric_chart(
            "Monthly Profit Trend", trend_months, profit_values, "Profit"
        )

        if revenue_chart:
            story.append(Spacer(1, 8))
            story.append(revenue_chart)
        if profit_chart:
            story.append(Spacer(1, 8))
            story.append(profit_chart)

    category_name, category_labels, category_values = (
        extract_category_comparison(analytics)
    )
    category_chart = create_comparison_chart(
        f"Revenue by {category_name}",
        category_labels[:12],
        category_values[:12],
        "Revenue"
    )
    if category_chart:
        story.append(Spacer(1, 8))
        story.append(category_chart)

    # =================================================
    # 5. ANOMALY DETECTION
    # =================================================
    add_section("5. Anomaly Detection")
    add_text(
        f"Status: {anomalies.get('status', 'N/A')}"
    )
    add_text(
        f"Total Anomalies: {anomalies.get('anomaly_count', 0)}"
    )
    add_text(
        f"Anomaly Percentage: "
        f"{anomalies.get('anomaly_percentage', 0)}%"
    )
    anomaly_rows = []
    for record in anomalies.get("records", [])[:100]:
        anomaly_rows.append([
            record.get("row_number", "N/A"),
            record.get("severity", "N/A"),
            record.get("explanation", "N/A")
        ])
    if anomaly_rows:
        story.append(
            KeepTogether([
                Paragraph(
                    "Detected Anomalous Records",
                    styles["SubHeading"]
                ),
                create_table(
                    ["Row", "Severity", "Explanation"],
                    anomaly_rows
                )
            ])
        )
    else:
        add_text(
            anomalies.get(
                "message",
                "No anomaly records available."
            )
        )

    severity_counts = anomalies.get("severity_counts", {})
    if isinstance(severity_counts, dict):
        severity_labels = [
            level.title()
            for level in ("high", "medium", "low")
            if severity_counts.get(level, 0) is not None
        ]
        severity_values = [
            severity_counts[level.lower()]
            for level in severity_labels
        ]
        severity_chart = create_comparison_chart(
            "Anomalies by Severity",
            severity_labels,
            severity_values,
            "Number of flagged records"
        )
        if severity_chart:
            story.append(Spacer(1, 8))
            story.append(severity_chart)

    story.append(PageBreak())
    # =================================================
    # 6. PREDICTIVE ANALYTICS
    # =================================================
    add_section("6. Predictive Analytics")
    add_text(
        forecast.get(
            "message",
            "Forecast information unavailable."
        )
    )
    add_text(
        f"Forecast Horizon: "
        f"{forecast.get('horizon_months', 'N/A')} months"
    )
    metric_rows = []
    for metric_name, metric in forecast.get("metrics", {}).items():
        if metric.get("status") != "completed":
            continue
        for item in metric.get("forecast", []):
            metric_rows.append([
                metric_name.title(),
                item.get("month", "N/A"),
                format_value(item.get("predicted"))
            ])
    if metric_rows:
        story.append(
            KeepTogether([
                Paragraph(
                    "Forecast Results",
                    styles["SubHeading"]
                ),
                create_table(
                    ["Metric", "Forecast Month", "Predicted Value"],
                    metric_rows
                )
            ])
        )
    else:
        add_text(
            "No completed forecast metrics are available."
        )
    # Historical forecast data
    historical_rows = []
    for metric_name, metric in forecast.get("metrics", {}).items():
        if metric.get("status") != "completed":
            continue
        for item in metric.get("history", []):
            historical_rows.append([
                metric_name.title(),
                item.get("month", "N/A"),
                format_value(item.get("actual"))
            ])
    if historical_rows:
        add_section_with_table(
            "Historical Values",
            ["Metric", "Month", "Actual Value"],
            historical_rows
        )

    for metric_name, metric in forecast.get("metrics", {}).items():
        if metric.get("status") != "completed":
            continue
        forecast_chart = create_forecast_chart(metric_name, metric)
        if forecast_chart:
            story.append(Spacer(1, 8))
            story.append(forecast_chart)

    # =================================================
    # 7. AI PREDICTIVE BUSINESS INSIGHTS
    # =================================================
    add_section("7. AI Predictive Business Insights")
    if ai_insights and ai_insights.strip():
        for raw_line in ai_insights.splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            # Markdown heading: #, ##, ###
            heading_match = re.match(
                r"^#{1,3}\s+(.+)$",
                line
            )
            if heading_match:
                story.append(
                    Paragraph(
                        safe_text(heading_match.group(1)),
                        styles["InsightHeading"]
                    )
                )
                continue
            # Markdown bullet points
            if line.startswith(("- ", "* ")):
                bullet_text = line[2:].strip()
                story.append(
                    Paragraph(
                        "&#8226; " + safe_text(bullet_text),
                        styles["InsightBullet"]
                    )
                )
                continue
            # Numbered lists
            numbered_match = re.match(
                r"^(\d+)\.\s+(.+)$",
                line
            )
            if numbered_match:
                story.append(
                    Paragraph(
                        safe_text(numbered_match.group(1))
                        + ". "
                        + safe_text(numbered_match.group(2)),
                        styles["InsightBullet"]
                    )
                )
                continue
            # Ordinary paragraph
            story.append(
                Paragraph(
                    safe_text(line),
                    styles["InsightBody"]
                )
            )
    else:
        add_text(
            "AI predictive insights were not provided."
        )

# FINAL DISCLAIMER

    story.append(Spacer(1, 15))
    story.append(
        HRFlowable(
            width="100%",
            color=BORDER,
            thickness=0.8,
            spaceBefore=5,
            spaceAfter=8
        )
    )
    story.append(
        Paragraph(
            "Generated automatically by InsightIQ. "
            "Forecasts are statistical estimates and should "
            "not be treated as guaranteed business outcomes. "
            "Business decisions should consider additional "
            "context and validation.",
            styles["FooterStyle"]
        )
    )

# PAGE NUMBER FOOTER

    def add_page_number(canvas, doc):
        canvas.saveState()
        page_width, page_height = A4
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(
            18 * mm,
            15 * mm,
            page_width - 18 * mm,
            15 * mm
        )
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            18 * mm,
            10 * mm,
            "InsightIQ | Business Analysis Report"
        )
        canvas.drawRightString(
            page_width - 18 * mm,
            10 * mm,
            f"Page {doc.page}"
        )
        canvas.restoreState()

# BUILD PDF

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
    buffer.seek(0)
    return buffer
