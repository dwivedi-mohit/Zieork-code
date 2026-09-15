"""File & Document Parser (PDFs, Spreadsheets, Code, Data)."""
import os
import sys

# Ensure local libs (for pypdf) are in path
sys.path.insert(0, os.path.abspath("libs"))

import pandas as pd
from typing import Dict, Any

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image, ExifTags
except ImportError:
    Image = None
    ExifTags = None

def parse_uploaded_file(filepath: str) -> Dict[str, Any]:
    """
    Extract text, metadata, and summaries from uploaded files.
    Supports PDF, CSV, Excel, TXT, JSON, and Code.
    """
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    try:
        # 1. PDF Document
        if ext == ".pdf":
            if not PdfReader:
                return {"error": "pypdf library not available."}
            reader = PdfReader(filepath)
            num_pages = len(reader.pages)
            extracted_pages = []
            for i in range(min(num_pages, 20)):  # Up to 20 pages
                text = reader.pages[i].extract_text() or ""
                extracted_pages.append(f"--- Page {i+1} ---\n{text}")

            full_text = "\n\n".join(extracted_pages)
            return {
                "filename": filename,
                "type": "pdf",
                "num_pages": num_pages,
                "summary": f"PDF document with {num_pages} pages.",
                "content": full_text[:10000]
            }

        # 2. CSV Spreadsheet
        elif ext == ".csv":
            df = pd.read_csv(filepath)
            summary = f"CSV dataset with {df.shape[0]} rows and {df.shape[1]} columns.\nColumns: {', '.join(df.columns)}"
            preview = df.head(10).to_markdown()
            stats = df.describe().to_markdown() if not df.empty else ""
            return {
                "filename": filename,
                "type": "csv",
                "summary": summary,
                "content": f"{summary}\n\n### Data Preview (First 10 Rows):\n{preview}\n\n### Statistics:\n{stats}"
            }

        # 3. Excel Spreadsheet (.xlsx, .xls)
        elif ext in [".xlsx", ".xls"]:
            excel = pd.ExcelFile(filepath)
            sheets_info = []
            for sheet in excel.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet)
                sheets_info.append(f"Sheet '{sheet}': {df.shape[0]} rows, {df.shape[1]} cols\n{df.head(5).to_markdown()}")

            content = "\n\n".join(sheets_info)
            return {
                "filename": filename,
                "type": "excel",
                "summary": f"Excel file with sheets: {', '.join(excel.sheet_names)}",
                "content": content
            }

        # 4. Images (PNG, JPG, JPEG, WEBP, BMP, GIF, TIFF)
        elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"]:
            if not Image:
                return {"filename": filename, "type": "image", "summary": "Image file (PIL not installed)", "content": f"Image file: {filename}"}

            with Image.open(filepath) as img:
                width, height = img.size
                img_format = img.format or ext.replace(".", "").upper()
                img_mode = img.mode

                # Aspect ratio calculation
                import math
                gcd = math.gcd(width, height)
                ratio_w, ratio_h = width // gcd, height // gcd
                ratio_str = f"{ratio_w}:{ratio_h}" if ratio_w <= 16 and ratio_h <= 16 else f"{width/height:.2f}:1"

                # Color tone & brightness analysis
                try:
                    import numpy as np
                    sample_img = img.convert("RGB").resize((100, 100))
                    arr = np.array(sample_img)
                    mean_r = float(arr[:, :, 0].mean())
                    mean_g = float(arr[:, :, 1].mean())
                    mean_b = float(arr[:, :, 2].mean())
                    brightness = float(0.299 * mean_r + 0.587 * mean_g + 0.114 * mean_b)

                    if brightness > 180:
                        lighting = "Bright / High-Key Lighting"
                    elif brightness < 70:
                        lighting = "Low-Light / Night Scene / Dark Tone"
                    else:
                        lighting = "Balanced Ambient Lighting"

                    if abs(mean_r - mean_g) < 15 and abs(mean_g - mean_b) < 15:
                        tone = "Monochrome / Neutral Grayscale"
                    elif mean_r > mean_b + 20 and mean_r > mean_g:
                        tone = "Warm Tones (Red / Amber / Golden)"
                    elif mean_b > mean_r + 20:
                        tone = "Cool Tones (Blue / Cyan / Sky)"
                    elif mean_g > mean_r + 15:
                        tone = "Natural / Foliage Green"
                    else:
                        tone = "Mixed Balanced Spectrum"
                except Exception:
                    brightness = 128.0
                    lighting = "Standard Exposure"
                    tone = "Standard Spectrum"

                # EXIF Metadata extraction
                exif_data = {}
                try:
                    raw_exif = img._getexif()
                    if raw_exif and ExifTags:
                        for tag_id, val in raw_exif.items():
                            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                            if tag_name in ["Make", "Model", "DateTimeOriginal", "DateTime", "ExposureTime", "FNumber", "ISOSpeedRatings"]:
                                exif_data[tag_name] = str(val)
                except Exception:
                    pass

                exif_summary = ", ".join([f"{k}: {v}" for k, v in exif_data.items()]) if exif_data else "No EXIF tags"

                summary = (
                    f"Image {filename} ({width}x{height} px, {ratio_str} aspect ratio, {img_format} {img_mode}). "
                    f"Lighting: {lighting}, Tone: {tone}."
                )

                content = (
                    f"[IMAGE VISUAL GEOMETRY & TELEMETRY]:\n"
                    f"• Filename: {filename}\n"
                    f"• Dimensions: {width} x {height} pixels (Aspect Ratio: {ratio_str})\n"
                    f"• Image Format: {img_format} (Color Mode: {img_mode})\n"
                    f"• Luminance & Lighting: {lighting} (Mean Brightness: {brightness:.1f}/255)\n"
                    f"• Dominant Palette Tone: {tone}\n"
                    f"• Camera / Capture Metadata: {exif_summary}\n"
                )

                return {
                    "filename": filename,
                    "type": "image",
                    "width": width,
                    "height": height,
                    "aspect_ratio": ratio_str,
                    "summary": summary,
                    "content": content
                }

        # 5. Text / Markdown / Code / JSON
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "filename": filename,
                "type": "text",
                "summary": f"Text file with {len(content.splitlines())} lines.",
                "content": content[:12000]
            }

    except Exception as e:
        return {"error": f"Failed to parse file: {str(e)}"}
