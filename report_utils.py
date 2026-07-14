"""Utilities for PDF reports and session management"""
import logging
import os
import pickle
import tempfile
from datetime import datetime
from io import BytesIO

import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF

# ── PDF Font Configuration ──
# Helvetica does NOT support Vietnamese. Use DejaVu or a Unicode font.
# fpdf2 supports Unicode via .add_font() with .ttf files.
_HAS_UNICODE_FONT = False
try:
    # Try to use a DejaVuSans font that ships with fpdf2 or is commonly available
    import os as _os
    _FONT_DIR = _os.path.join(_os.path.dirname(__file__), ".fonts")
    _FONT_PATH = _os.path.join(_FONT_DIR, "DejaVuSans.ttf")
    _FONT_BOLD_PATH = _os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")
    _FONT_ITALIC_PATH = _os.path.join(_FONT_DIR, "DejaVuSans-Oblique.ttf")
    if _os.path.exists(_FONT_PATH):
        _HAS_UNICODE_FONT = True
except Exception:
    pass

from src.utils.exceptions import handle_error, DataValidationError

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════

SESSION_FILE = "saved_session.pkl"

def save_session_state():
    """Save current session state to pickle file"""
    try:
        session_data = {
            "df": st.session_state.get("df"),
            "cleaned_df": st.session_state.get("cleaned_df"),
            "filename": st.session_state.get("filename", ""),
            "saved_at": datetime.now().isoformat(),
        }
        with open(SESSION_FILE, "wb") as f:
            pickle.dump(session_data, f)
        return True, f"✅ Session saved at {datetime.now():%H:%M:%S}"
    except (IOError, pickle.PickleError) as e:
        logger.error("Session save failed: %s", e, exc_info=True)
        return False, f"❌ Save failed: {str(e)}"
    except Exception as e:
        logger.error("Unexpected session save error: %s", e, exc_info=True)
        return False, f"❌ Save failed: unexpected error"

def load_session_state():
    """Load session state from pickle file"""
    try:
        if not os.path.exists(SESSION_FILE):
            return False, "❌ No saved session found"
        with open(SESSION_FILE, "rb") as f:
            session_data = pickle.load(f)
        
        if session_data.get("df") is not None:
            st.session_state.df = session_data["df"]
        if session_data.get("cleaned_df") is not None:
            st.session_state.cleaned_df = session_data["cleaned_df"]
        if session_data.get("filename"):
            st.session_state.filename = session_data["filename"]
        
        saved_at = session_data.get("saved_at", "unknown")
        return True, f"✅ Session loaded (saved: {saved_at})"
    except (IOError, pickle.PickleError) as e:
        logger.error("Session load failed: %s", e, exc_info=True)
        return False, f"❌ Load failed: {str(e)}"
    except Exception as e:
        logger.error("Unexpected session load error: %s", e, exc_info=True)
        return False, f"❌ Load failed: unexpected error"

def has_saved_session():
    """Check if a saved session exists"""
    return os.path.exists(SESSION_FILE)

def get_session_info():
    """Get info about saved session"""
    if not has_saved_session():
        return None
    try:
        with open(SESSION_FILE, "rb") as f:
            data = pickle.load(f)
        return {
            "saved_at": data.get("saved_at", "unknown"),
            "filename": data.get("filename", "unknown"),
            "rows": len(data.get("df", [])),
            "cols": len(data.get("df", pd.DataFrame()).columns) if data.get("df") is not None else 0,
        }
    except (IOError, pickle.PickleError, KeyError) as e:
        logger.warning("Session info read failed: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected session info error: %s", e, exc_info=True)
        return None


# ═══════════════════════════════════════════════════════════════
# PDF REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

class PDFReport(FPDF):
    """Custom PDF class for generating nice reports with Unicode support."""
    
    _STYLES = {"": "", "B": "", "I": "", "BI": ""}
    
    def _font_name(self, style: str = "") -> str:
        if _HAS_UNICODE_FONT:
            return "DejaVu"
        return "Helvetica"
    
    def _setup_fonts(self):
        """Register Unicode fonts if available, otherwise fall back to Helvetica."""
        if _HAS_UNICODE_FONT:
            self.add_font("DejaVu", "", _FONT_PATH, uni=True)
            self.add_font("DejaVu", "B", _FONT_BOLD_PATH, uni=True)
            self.add_font("DejaVu", "I", _FONT_ITALIC_PATH, uni=True)
            self.add_font("DejaVu", "BI", _FONT_BOLD_PATH, uni=True)
    
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
        """Draw a KPI card."""
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


def generate_pdf_report(df, num_cols, cat_cols, filename="DataReport.pdf"):
    """Generate a beautiful PDF report from the current dataset"""
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # ── Title ──
    fnt = pdf._font_name("B")
    pdf.set_font(fnt, "B", 20)
    pdf.set_text_color(91, 107, 247)
    pdf.cell(0, 15, "Data Analysis Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(fnt, "", 9)
    pdf.set_text_color(128, 130, 144)
    pdf.cell(0, 6, f"Generated: {datetime.now():%Y-%m-%d %H:%M}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # ── Overview KPIs ──
    pdf.section_title("1. Dataset Overview")
    
    # KPI row
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
    
    # Dataset info
    pdf.key_value("Filename:", filename)
    pdf.key_value("Numeric columns:", len(num_cols))
    pdf.key_value("Categorical columns:", len(cat_cols))
    pdf.ln(4)
    
    # ── Numeric Summary ──
    if num_cols:
        pdf.add_page()
        pdf.section_title("2. Numeric Columns Summary")
        for col in num_cols[:10]:  # Limit to first 10
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
    
    # ── Categorical Summary ──
    if cat_cols:
        pdf.add_page()
        pdf.section_title("3. Categorical Columns Summary")
        for col in cat_cols[:8]:  # Limit to first 8
            if col not in df.columns:
                continue
            pdf.sub_title(f"📁 {col}")
            vc = df[col].value_counts().head(10)
            pdf.key_value("Unique values:", f"{df[col].nunique()}")
            pdf.key_value("Top:", vc.index[0] if len(vc) > 0 else "N/A")
            pdf.key_value("Top count:", f"{vc.iloc[0]:,}" if len(vc) > 0 else "N/A")
            pdf.key_value("Missing:", f"{df[col].isnull().sum():,}")
            # Top 5 as inline text
            top5 = ", ".join([f"{idx} ({val})" for idx, val in vc.head(5).items()])
            if top5:
                pdf.body_text(f"Top values: {top5}")
            pdf.ln(2)
    
    # ── Correlation ──
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
    
    # ── Data Quality ──
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
    
    # Issues
    issues = []
    if df.isnull().sum().sum() > 0:
        issues.append(f"⚠️ {df.isnull().sum().sum():,} missing values")
    if dup_rows > 0:
        issues.append(f"⚠️ {dup_rows:,} duplicate rows")
    if not issues:
        issues.append("✅ Data is clean!")
    for issue in issues:
        pdf.body_text(issue)
    
    # ── Column List ──
    pdf.section_title("6. Column Details")
    for col in df.columns:
        dtype = str(df[col].dtype)
        missing = df[col].isnull().sum()
        unique = df[col].nunique()
        pdf.body_text(f"  • {col} ({dtype}) — {unique:,} unique, {missing:,} missing")
    
    # Save to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes