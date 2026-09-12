"""PDF forensic report generation."""

import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_pdf_report(analysis: dict, output_path: Path) -> Path:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#00ffaa"))
    heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#333333"))
    body = styles["Normal"]

    story = []
    story.append(Paragraph("BROKEN DISPLAY FORENSIC REPORT", title_style))
    story.append(Paragraph("Dead Pixel Forensics — Because someone had to count the lines.", body))
    story.append(Spacer(1, 0.3 * inch))

    img_info = analysis["image"]
    summary = analysis["summary"]
    lines = analysis["line_statistics"]
    metrics = analysis["metrics"]

    story.append(Paragraph("Image Information", heading))
    info_data = [
        ["Resolution", f"{img_info['width']} × {img_info['height']}"],
        ["Aspect Ratio", str(img_info["aspect_ratio"])],
        ["Filename", img_info.get("filename", "unknown")],
    ]
    story.append(_make_table(info_data))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Damage Summary", heading))
    damage_data = [
        ["Detected Abnormal Area", f"{summary['damage_percentage']}%"],
        ["Unaffected Area", f"{summary['unaffected_percentage']}%"],
        ["Regions Analyzed", "9 (3×3 grid)"],
        ["Disclaimer", summary.get("disclaimer", "")],
    ]
    story.append(_make_table(damage_data))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Line Analysis", heading))
    line_data = [
        ["Total Lines", lines["total"]],
        ["Horizontal", lines["horizontal"]],
        ["Vertical", lines["vertical"]],
        ["Diagonal", lines["diagonal"]],
        ["Curved", lines["curved"]],
        ["Irregular", lines["irregular"]],
        ["Longest", f"{lines['longest']} px"],
        ["Average Length", f"{lines['average_length']} px"],
        ["Average Width", f"{lines['average_width']} px"],
    ]
    story.append(_make_table(line_data))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Custom Metrics", heading))
    metric_data = [
        ["Uselessness Score™", f"{metrics['uselessness']['score']} — {metrics['uselessness']['interpretation']}"],
        ["Chaos Index™", str(metrics["chaos"]["score"])],
        ["Symmetry Score", f"{metrics['symmetry']['score']}%"],
        ["Breakage Level™", f"{metrics['breakage']['level']}/10 — {metrics['breakage']['description']}"],
        ["Display Personality", analysis["personality"]["type"]],
        ["Display DNA ID", analysis["display_dna"]["id"]],
    ]
    story.append(_make_table(metric_data))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Useless Awards™", heading))
    for award in analysis.get("awards", []):
        story.append(Paragraph(f"{award['emoji']} {award['title']}: {award['winner']} ({award['value']})", body))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(
        "<i>Your display may be broken, but our analysis is unnecessarily complete.</i>",
        body,
    ))

    doc.build(story)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    return output_path


def _make_table(data: list[list]) -> Table:
    t = Table(data, colWidths=[2.5 * inch, 4 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    return t
