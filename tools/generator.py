"""
Unified Document & Visual Generator for Zieork.
Supports high-quality Excel (.xlsx), Word (.docx), PDF (.pdf), and Charts (.png).
"""
import os
import sys
import time
import re
from typing import Dict, Any, List, Optional

# Ensure local libs (docx, reportlab, etc.) are available
sys.path.insert(0, os.path.abspath("libs"))
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"

GENERATED_DIR = os.path.abspath("generated")
os.makedirs(GENERATED_DIR, exist_ok=True)


def _sanitize_filename(name: str, ext: str) -> str:
    """Generate a clean, timestamped filename."""
    base = re.sub(r'[^a-zA-Z0-9_\-]', '_', name).strip('_')
    if not base:
        base = "zieork_export"
    timestamp = int(time.time())
    return f"{base}_{timestamp}.{ext.lstrip('.')}"


def create_excel_file(title: str, sheets_data: Dict[str, Any], filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a styled Microsoft Excel (.xlsx) workbook with formulas and auto-width columns.
    
    sheets_data format:
    {
        "SheetName": {
            "headers": ["Col 1", "Col 2", "Price"],
            "rows": [["A", "B", 100], ["C", "D", 200]],
            "has_total": True  # Adds SUM row automatically
        }
    }
    """
    import xlsxwriter

    if not filename:
        filename = _sanitize_filename(title, "xlsx")
    elif not filename.endswith(".xlsx"):
        filename = f"{filename}.xlsx"

    filepath = os.path.join(GENERATED_DIR, filename)

    workbook = xlsxwriter.Workbook(filepath)

    # Styles & Palettes
    header_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#1E293B",  # Slate 800
        "font_color": "#FFFFFF",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#CBD5E1",
        "font_name": "Calibri",
        "font_size": 11
    })

    title_fmt = workbook.add_format({
        "bold": True,
        "font_size": 14,
        "font_color": "#0F172A",
        "valign": "vcenter",
        "font_name": "Calibri"
    })

    cell_even_fmt = workbook.add_format({
        "bg_color": "#FFFFFF",
        "border": 1,
        "border_color": "#E2E8F0",
        "font_name": "Calibri",
        "font_size": 10
    })

    cell_odd_fmt = workbook.add_format({
        "bg_color": "#F8FAFC",  # Slate 50
        "border": 1,
        "border_color": "#E2E8F0",
        "font_name": "Calibri",
        "font_size": 10
    })

    currency_even = workbook.add_format({
        "bg_color": "#FFFFFF",
        "border": 1,
        "border_color": "#E2E8F0",
        "num_format": "$#,##0.00",
        "font_name": "Calibri",
        "font_size": 10
    })

    currency_odd = workbook.add_format({
        "bg_color": "#F8FAFC",
        "border": 1,
        "border_color": "#E2E8F0",
        "num_format": "$#,##0.00",
        "font_name": "Calibri",
        "font_size": 10
    })

    total_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#E2E8F0",
        "border": 1,
        "border_color": "#94A3B8",
        "num_format": "$#,##0.00",
        "font_name": "Calibri",
        "font_size": 11
    })

    total_label_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#E2E8F0",
        "border": 1,
        "border_color": "#94A3B8",
        "font_name": "Calibri",
        "font_size": 11
    })

    total_rows_written = 0

    for sheet_name, content in sheets_data.items():
        clean_sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)[:31] or "Sheet1"
        ws = workbook.add_worksheet(clean_sheet_name)
        ws.set_tab_color("#3B82F6")

        headers = content.get("headers", [])
        rows = content.get("rows", [])
        has_total = content.get("has_total", False)

        # Write Sheet Title
        ws.write(0, 0, f"📊 {title} — {sheet_name}", title_fmt)
        start_row = 2

        # Track max column lengths for auto-width
        col_widths = [len(str(h)) for h in headers] if headers else []

        # Write Headers
        for col_idx, h in enumerate(headers):
            ws.write(start_row, col_idx, h, header_fmt)

        # Write Data Rows
        current_row = start_row + 1
        for row_idx, r in enumerate(rows):
            is_odd = (row_idx % 2 == 1)
            for col_idx, val in enumerate(r):
                col_name = str(headers[col_idx]).lower() if col_idx < len(headers) else ""
                is_currency = any(k in col_name for k in ["price", "cost", "revenue", "budget", "salary", "total", "amount", "$"])

                # Determine cell format
                if is_currency and isinstance(val, (int, float)):
                    fmt = currency_odd if is_odd else currency_even
                else:
                    fmt = cell_odd_fmt if is_odd else cell_even_fmt

                ws.write(current_row, col_idx, val, fmt)

                # Update column width
                val_len = len(str(val))
                if col_idx < len(col_widths):
                    col_widths[col_idx] = max(col_widths[col_idx], val_len)
                else:
                    col_widths.append(val_len)

            current_row += 1
            total_rows_written += 1

        # Write Total / Summary Row if requested
        if has_total and rows:
            ws.write(current_row, 0, "Total", total_label_fmt)
            for col_idx in range(1, len(headers)):
                col_name = str(headers[col_idx]).lower()
                is_numeric = any(k in col_name for k in ["price", "cost", "revenue", "budget", "salary", "total", "amount", "qty", "count"])
                if is_numeric:
                    col_letter = chr(ord('A') + col_idx)
                    formula = f"=SUM({col_letter}{start_row + 2}:{col_letter}{current_row})"
                    ws.write_formula(current_row, col_idx, formula, total_fmt)
                else:
                    ws.write(current_row, col_idx, "", total_label_fmt)

        # Apply auto-fit column widths with padding
        for col_idx, w in enumerate(col_widths):
            ws.set_column(col_idx, col_idx, max(w + 4, 12))

    workbook.close()

    file_size_kb = round(os.path.getsize(filepath) / 1024, 1)

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "download_url": f"/api/download/{filename}",
        "file_size_kb": file_size_kb,
        "sheets": list(sheets_data.keys()),
        "total_rows": total_rows_written
    }


def create_word_document(title: str, sections: List[Dict[str, Any]], filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a styled Microsoft Word document (.docx) with headings, tables, bullets, and callouts.
    """
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    if not filename:
        filename = _sanitize_filename(title, "docx")
    elif not filename.endswith(".docx"):
        filename = f"{filename}.docx"

    filepath = os.path.join(GENERATED_DIR, filename)

    doc = docx.Document()

    # Configure Margins (1 inch all sides)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(title)
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)  # Slate 900
    title_p.paragraph_format.space_after = Pt(4)

    # Subtitle / Metadata
    meta_p = doc.add_paragraph()
    meta_run = meta_p.add_run(f"Generated by Zieork Autonomous Edge Intelligence • {time.strftime('%B %d, %Y')}")
    meta_run.font.name = "Calibri"
    meta_run.font.size = Pt(10)
    meta_run.font.italic = True
    meta_run.font.color.rgb = RGBColor(100, 116, 139)  # Slate 500
    meta_p.paragraph_format.space_after = Pt(20)

    # Render Sections
    for sec in sections:
        sec_type = sec.get("type", "paragraph")

        if sec_type == "heading":
            level = sec.get("level", 1)
            h = doc.add_heading(sec.get("text", ""), level=min(level, 3))
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)
            for r in h.runs:
                r.font.name = "Calibri"
                if level == 1:
                    r.font.color.rgb = RGBColor(30, 41, 59)  # Slate 800
                    r.font.size = Pt(16)
                elif level == 2:
                    r.font.color.rgb = RGBColor(51, 65, 85)  # Slate 700
                    r.font.size = Pt(13)

        elif sec_type == "paragraph":
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(sec.get("text", ""))
            run.font.name = "Calibri"
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(30, 41, 59)

        elif sec_type == "bullet":
            items = sec.get("items", [])
            for item in items:
                bp = doc.add_paragraph(style="List Bullet")
                bp.paragraph_format.space_after = Pt(3)
                r = bp.add_run(item)
                r.font.name = "Calibri"
                r.font.size = Pt(11)

        elif sec_type == "table":
            headers = sec.get("headers", [])
            rows = sec.get("rows", [])
            if headers:
                tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                tbl.autofit = True

                # Format Header Row
                hdr_cells = tbl.rows[0].cells
                for i, h in enumerate(headers):
                    hdr_cells[i].text = str(h)
                    shading_elm = parse_xml(r'<w:shd {} w:fill="1E293B"/>'.format(nsdecls('w')))
                    hdr_cells[i]._tc.get_or_add_tcPr().append(shading_elm)
                    for p in hdr_cells[i].paragraphs:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for r in p.runs:
                            r.font.bold = True
                            r.font.color.rgb = RGBColor(255, 255, 255)
                            r.font.size = Pt(10)

                # Format Data Rows
                for row_idx, r in enumerate(rows):
                    row_cells = tbl.rows[row_idx + 1].cells
                    is_odd = (row_idx % 2 == 1)
                    bg_hex = "F8FAFC" if is_odd else "FFFFFF"
                    for col_idx, val in enumerate(r):
                        if col_idx < len(row_cells):
                            row_cells[col_idx].text = str(val)
                            shd = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), bg_hex))
                            row_cells[col_idx]._tc.get_or_add_tcPr().append(shd)
                            for p in row_cells[col_idx].paragraphs:
                                for run_item in p.runs:
                                    run_item.font.size = Pt(10)
                                    run_item.font.color.rgb = RGBColor(51, 65, 85)

                doc.add_paragraph().paragraph_format.space_after = Pt(10)

        elif sec_type == "callout":
            cp = doc.add_paragraph()
            cp.paragraph_format.left_indent = Inches(0.4)
            cp.paragraph_format.space_after = Pt(10)
            shd = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
            cp._p.get_or_add_pPr().append(shd)
            c_run = cp.add_run(f"💡 {sec.get('text', '')}")
            c_run.font.name = "Calibri"
            c_run.font.size = Pt(10.5)
            c_run.font.italic = True
            c_run.font.color.rgb = RGBColor(30, 41, 59)

    doc.save(filepath)
    file_size_kb = round(os.path.getsize(filepath) / 1024, 1)

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "download_url": f"/api/download/{filename}",
        "file_size_kb": file_size_kb,
        "sections_count": len(sections)
    }


def create_pdf_document(title: str, sections: List[Dict[str, Any]], filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a publication-grade PDF report (.pdf) using ReportLab flowables.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    if not filename:
        filename = _sanitize_filename(title, "pdf")
    elif not filename.endswith(".pdf"):
        filename = f"{filename}.pdf"

    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        "PDFMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=18
    )

    h1_style = ParagraphStyle(
        "PDFH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        "PDFH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        "PDFBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        "PDFCallout",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=6,
        spaceAfter=8
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"Generated by Zieork Autonomous Edge Intelligence • {time.strftime('%B %d, %Y')}", meta_style))

    # Build Document Flowables
    for sec in sections:
        sec_type = sec.get("type", "paragraph")

        if sec_type == "heading":
            level = sec.get("level", 1)
            style_to_use = h1_style if level == 1 else h2_style
            story.append(Paragraph(sec.get("text", ""), style_to_use))

        elif sec_type == "paragraph":
            story.append(Paragraph(sec.get("text", ""), body_style))

        elif sec_type == "bullet":
            for item in sec.get("items", []):
                story.append(Paragraph(f"• {item}", bullet_style))
            story.append(Spacer(1, 4))

        elif sec_type == "table":
            headers = sec.get("headers", [])
            rows = sec.get("rows", [])
            if headers:
                table_data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)) for h in headers]]
                for r in rows:
                    table_data.append([Paragraph(str(val), ParagraphStyle('TD', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#1E293B"))) for val in r])

                t = Table(table_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                ]))
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 8))

        elif sec_type == "callout":
            story.append(Spacer(1, 4))
            callout_text = f"<b>Note:</b> {sec.get('text', '')}"
            callout_p = Paragraph(callout_text, callout_style)
            callout_table = Table([[callout_p]], colWidths=[520])
            callout_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(callout_table)
            story.append(Spacer(1, 6))

    doc.build(story)
    file_size_kb = round(os.path.getsize(filepath) / 1024, 1)

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "download_url": f"/api/download/{filename}",
        "file_size_kb": file_size_kb,
        "sections_count": len(sections)
    }


def create_data_chart(chart_type: str, title: str, data_dict: Dict[str, Any], filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate high-DPI data visualizations (bar, line, pie, scatter, horizontal bar) using Matplotlib.
    """
    import matplotlib.pyplot as plt

    if not filename:
        filename = _sanitize_filename(title, "png")
    elif not filename.endswith(".png"):
        filename = f"{filename}.png"

    filepath = os.path.join(GENERATED_DIR, filename)

    # Modern Dark/Light Hybrid Aesthetic
    plt.figure(figsize=(9, 5.5), dpi=150)
    fig = plt.gcf()
    fig.patch.set_facecolor("#0F172A")  # Slate 900
    ax = plt.gca()
    ax.set_facecolor("#1E293B")  # Slate 800

    labels = data_dict.get("labels", [])
    values = data_dict.get("values", [])
    x_label = data_dict.get("x_label", "")
    y_label = data_dict.get("y_label", "")

    colors_list = ["#38BDF8", "#818CF8", "#34D399", "#FBBF24", "#F87171", "#A78BFA", "#F472B6"]

    c_type = chart_type.lower().strip()

    if c_type in ["bar", "column"]:
        bars = ax.bar(range(len(labels)), values, color=colors_list[:len(labels)], edgecolor="#334155", width=0.6)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, color="#E2E8F0", rotation=15 if len(labels) > 5 else 0)
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:,.0f}" if isinstance(height, (int, float)) and height >= 10 else f"{height}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", color="#94A3B8", fontsize=9)

    elif c_type in ["horizontal_bar", "hbar"]:
        ax.barh(range(len(labels)), values, color=colors_list[:len(labels)], edgecolor="#334155", height=0.6)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, color="#E2E8F0")

    elif c_type in ["line", "trend"]:
        ax.plot(range(len(labels)), values, marker="o", color="#38BDF8", linewidth=2.5, markersize=6, markerfacecolor="#818CF8")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, color="#E2E8F0", rotation=15 if len(labels) > 5 else 0)
        ax.fill_between(range(len(labels)), values, color="#38BDF8", alpha=0.15)

    elif c_type in ["pie", "donut"]:
        fig.patch.set_facecolor("#0F172A")
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors_list[:len(labels)],
            textprops={"color": "#E2E8F0", "fontsize": 9},
            wedgeprops={"edgecolor": "#0F172A", "linewidth": 2}
        )
        for at in autotexts:
            at.set_color("#0F172A")
            at.set_fontweight("bold")

    # Titles & Labels
    ax.set_title(title, color="#F8FAFC", fontsize=13, fontweight="bold", pad=12)
    if x_label and c_type not in ["pie", "donut"]:
        ax.set_xlabel(x_label, color="#94A3B8", fontsize=10, labelpad=8)
    if y_label and c_type not in ["pie", "donut"]:
        ax.set_ylabel(y_label, color="#94A3B8", fontsize=10, labelpad=8)

    # Grid & Spines
    if c_type not in ["pie", "donut"]:
        ax.grid(True, linestyle="--", alpha=0.25, color="#64748B")
        ax.tick_params(colors="#94A3B8")
        for spine in ax.spines.values():
            spine.set_color("#334155")

    plt.tight_layout()
    plt.savefig(filepath, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    file_size_kb = round(os.path.getsize(filepath) / 1024, 1)

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "image_url": f"/api/download/{filename}",
        "download_url": f"/api/download/{filename}",
        "file_size_kb": file_size_kb
    }
