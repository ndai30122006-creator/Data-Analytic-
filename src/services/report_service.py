"""PDF report generation service"""

import logging
import os
from datetime import datetime
from io import BytesIO
from typing import Optional

import numpy as np
import pandas as pd
from fpdf import FPDF

from src.utils.exceptions import handle_error

logger = logging.getLogger(__name__)

_HAS_UNICODE_FONT = False
try:
    _FONT_DIR = os.path.join(os.path.dirname(__file__), ".fonts")
    _FONT_PATH = os.path.join(_FONT_DIR, "DejaVuSans.ttf")
    _FONT_BOLD_PATH = os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")
    _FONT_ITALIC_PATH = os.path.join(_FONT_DIR, "DejaVuSans-Oblique.ttf")
    if os.path.exists(_FONT_PATH):
        _HAS_UNICODE_FONT = True
except Exception:
    pass


class PDFReport(FPDF):
    """Custom PDF class for generating nice reports with Unicode support."""

    _STYLES = {"": "", "B": "", "I": "", "BI": ""}

    def _font_name(self, style: str = "") -> str:
        if _HAS_UNICODE_FONT:
            return "DejaVu"
        return "Helvetica"

    def _setup_fonts(self):
        if not getattr(self, "_fonts_registered", False):
            if _HAS_UNICODE_FONT:
                self.add_font("DejaVu", "", _FONT_PATH, uni=True)
                self.add_font("DejaVu", "B", _FONT_BOLD_PATH, uni=True)
                self.add_font("DejaVu", "I", _FONT_ITALIC_PATH, uni=True)
                self.add_font("DejaVu", "BI", _FONT_BOLD_PATH, uni=True)
            self._fonts_registered = True

    def header(self):
        self._setup_fonts()
        self.set_font(self._font_name("B"), "B", 10)
        self.set_text_color(91, 107, 247)
        self.cell(0, 8, "Data Analyst Pro v3.0 - Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font(self._font_name("I"), "I", 7)
        self.set_text_color(128, 130, 144)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font(self._font_name("B"), "B", 13)
        self.set_text_color(30, 31, 40)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(91, 107, 247)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font(self._font_name("B"), "B", 10)
        self.set_text_color(60, 61, 70)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font(self._font_name(""), "", 9)
        self.set_text_color(40, 41, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def key_value(self, key, value):
        self.set_font(self._font_name("B"), "B", 9)
        self.set_text_color(60, 61, 70)
        self.cell(50, 6, key)
        self.set_font(self._font_name(""), "", 9)
        self.set_text_color(40, 41, 50)
        self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    def kpi_box(self, label, value):
        x = self.get_x()
        y = self.get_y()
        w = 42
        h = 18
        self.set_draw_color(220, 220, 230)
        self.set_fill_color(245, 246, 250)
        self.rect(x, y, w, h, style="DF")
        self.set_xy(x + 2, y + 2)
        self.set_font(self._font_name(""), "", 6)
        self.set_text_color(128, 130, 144)
        self.cell(w - 4, 4, label, align="C")
        self.set_xy(x + 2, y + 8)
        self.set_font(self._font_name("B"), "B", 10)
        self.set_text_color(30, 31, 40)
        self.cell(w - 4, 8, str(value), align="C")


def generate_pdf_report(df: pd.DataFrame, num_cols: list, cat_cols: list, filename: str = "DataReport.pdf") -> bytes:
    """Generate a beautiful PDF report from the current dataset"""
    try:
        pdf = PDFReport()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        fnt = pdf._font_name("B")
        pdf.set_font(fnt, "B", 20)
        pdf.set_text_color(91, 107, 247)
        pdf.cell(0, 15, "Data Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(fnt, "", 9)
        pdf.set_text_color(128, 130, 144)
        pdf.cell(0, 6, f"Generated: {datetime.now():%Y-%m-%d %H:%M}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

        pdf.section_title("1. Dataset Overview")
        y_start = pdf.get_y()
        pdf.kpi_box("Rows", f"{len(df):,}")
        pdf.set_x(10 + 44)
        pdf.kpi_box("Columns", df.shape[1])
        pdf.set_x(10 + 88)
        missing_pct = round(df.isnull().sum().sum() / (len(df) * df.shape[1]) * 100, 1)
        pdf.kpi_box("Missing", f"{missing_pct}%")
        pdf.set_x(10 + 132)
        dup_pct = round(df.duplicated().sum() / len(df) * 100, 1) if len(df) > 0 else 0
        pdf.kpi_box("Duplicates", f"{dup_pct}%")
        pdf.set_y(y_start + 22)

        pdf.key_value("Filename:", filename)
        pdf.key_value("Numeric columns:", len(num_cols))
        pdf.key_value("Categorical columns:", len(cat_cols))
        pdf.ln(4)

        if num_cols:
            pdf.add_page()
            pdf.section_title("2. Numeric Columns Summary")
            for col in num_cols[:10]:
                if col not in df.columns:
                    continue
                s = df[col].dropna()
                if len(s) == 0:
                    continue
                pdf.sub_title(f"📊 {col}")
                pdf.key_value("Count:", f"{len(s):,}")
                pdf.key_value("Mean:", f"{s.mean():.4f}")
                pdf.key_value("Median:", f"{s.median():.4f}")
                pdf.key_value("Std:", f"{s.std():.4f}")
                pdf.key_value("Min:", f"{s.min():.4f}")
                pdf.key_value("Max:", f"{s.max():.4f}")
                pdf.key_value("Missing:", f"{df[col].isnull().sum():,}")
                pdf.ln(3)

        if cat_cols:
            pdf.add_page()
            pdf.section_title("3. Categorical Columns Summary")
            for col in cat_cols[:8]:
                if col not in df.columns:
                    continue
                pdf.sub_title(f"📁 {col}")
                vc = df[col].value_counts().head(10)
                pdf.key_value("Unique values:", f"{df[col].nunique()}")
                pdf.key_value("Top:", vc.index[0] if len(vc) > 0 else "N/A")
                pdf.key_value("Top count:", f"{vc.iloc[0]:,}" if len(vc) > 0 else "N/A")
                pdf.key_value("Missing:", f"{df[col].isnull().sum():,}")
                top5 = ", ".join([f"{idx} ({val})" for idx, val in vc.head(5).items()])
                if top5:
                    pdf.body_text(f"Top values: {top5}")
                pdf.ln(2)

        if len(num_cols) >= 2:
            pdf.add_page()
            pdf.section_title("4. Correlation Analysis")
            corr = df[num_cols].corr()
            high_corr = []
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    r = corr.iloc[i, j]
                    if abs(r) > 0.5:
                        high_corr.append(f"{num_cols[i]} ↔ {num_cols[j]}: r = {r:.4f}")
            if high_corr:
                pdf.sub_title("High Correlations (|r| > 0.5):")
                for line in high_corr[:10]:
                    pdf.body_text(f"  • {line}")
            else:
                pdf.body_text("No strong correlations found between numeric columns.")

        pdf.add_page()
        pdf.section_title("5. Data Quality")
        total_cells = df.shape[0] * df.shape[1]
        filled = total_cells - df.isnull().sum().sum()
        completeness = filled / total_cells * 100 if total_cells > 0 else 0
        dup_rows = df.duplicated().sum()
        uniqueness = (1 - dup_rows / len(df)) * 100 if len(df) > 0 else 0

        y_start = pdf.get_y()
        pdf.kpi_box("Completeness", f"{completeness:.1f}%")
        pdf.set_x(10 + 44)
        pdf.kpi_box("Uniqueness", f"{uniqueness:.1f}%")
        pdf.set_x(10 + 88)
        pdf.kpi_box("Missing", f"{df.isnull().sum().sum():,}")
        pdf.set_x(10 + 132)
        pdf.kpi_box("Duplicates", f"{dup_rows:,}")
        pdf.set_y(y_start + 22)

        issues = []
        if df.isnull().sum().sum() > 0:
            issues.append(f"⚠️ {df.isnull().sum().sum():,} missing values")
        if dup_rows > 0:
            issues.append(f"⚠️ {dup_rows:,} duplicate rows")
        if not issues:
            issues.append("✅ Data is clean!")
        for issue in issues:
            pdf.body_text(issue)

        pdf.section_title("6. Column Details")
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            unique = df[col].nunique()
            pdf.body_text(f"  • {col} ({dtype}) — {unique:,} unique, {missing:,} missing")

        raw = pdf.output()
        if isinstance(raw, str):
            return raw.encode("latin-1")
        return raw
    except Exception as e:
        handle_error(e, "generate_pdf_report", "Failed to generate PDF report")
        return b""
