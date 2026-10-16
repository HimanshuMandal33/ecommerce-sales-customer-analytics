"""
generate_report.py
==================
Rebuilds HimanshuMandal_ProjectReport.docx with:
  - styled KPI dashboard panel (table-based)
  - 8 embedded matplotlib charts covering all sales analysis areas
  - full narrative text preserved from the original report
Run:  python generate_report.py
"""

import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── Colour palette ────────────────────────────────────────────────────────────
C_INDIGO   = "#4f46e5"
C_EMERALD  = "#10b981"
C_ROSE     = "#f43f5e"
C_AMBER    = "#f59e0b"
C_PURPLE   = "#7c3aed"
C_CYAN     = "#0891b2"
C_DARK     = "#1e1b4b"
C_LIGHT    = "#f0f2f6"

PALETTE = [C_INDIGO, C_EMERALD, C_ROSE, C_AMBER, C_PURPLE, C_CYAN, "#e11d48", "#059669"]

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))

# ── Chart helper: save figure to BytesIO ─────────────────────────────────────
def fig_to_stream(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf

# ── Word helpers ──────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tcPr.append(shd)

def set_cell_border(cell, **kwargs):
    """kwargs: top/bottom/left/right = (size_pt, color_hex)"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side, (sz, color) in kwargs.items():
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(sz * 8))
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color.lstrip("#"))
        tcBorders.append(b)
    tcPr.append(tcBorders)

def para_style(para, bold=False, size=11, color=None, align=None, space_after=6):
    run = para.runs[0] if para.runs else para.add_run(para.text)
    if bold:  run.bold = True
    run.font.size = Pt(size)
    if color:
        r, g, b = (int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        run.font.color.rgb = RGBColor(r, g, b)
    if align:
        para.alignment = align
    para.paragraph_format.space_after = Pt(space_after)

def add_heading(doc, text, level=1, color=C_DARK):
    styles = {1: ("Heading 1", 16), 2: ("Heading 2", 13)}
    style, size = styles.get(level, ("Heading 1", 16))
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    r, g, b = (int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    run.font.color.rgb = RGBColor(r, g, b)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(6)
    return p

def add_body(doc, text, size=11, color=None, bold=False, space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        r, g, b = (int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        run.font.color.rgb = RGBColor(r, g, b)
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_chart(doc, stream, width=Inches(6.2), caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(stream, width=width)
    if caption:
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(10)
        for run in cp.runs:
            run.font.size  = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x57, 0x60, 0x6a)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — KPI Dashboard Panel
# ══════════════════════════════════════════════════════════════════════════════
def chart_kpi_panel():
    kpis = [
        ("Total Revenue",    "$177.1M",  C_INDIGO),
        ("Total Profit",     "$76.1M",   C_EMERALD),
        ("Total Orders",     "138,116",  C_AMBER),
        ("Customers",        "24,911",   C_PURPLE),
        ("Avg Order Value",  "$1,282",   C_ROSE),
        ("Profit Margin",    "45.1%",    C_CYAN),
        ("Avg Rating",       "3.68 / 5", "#e11d48"),
        ("Return Rate",      "6.85%",    "#059669"),
    ]
    fig, axes = plt.subplots(2, 4, figsize=(13, 4.2))
    fig.patch.set_facecolor("#f0f2f6")
    for ax, (label, value, color) in zip(axes.flat, kpis):
        ax.set_facecolor("white")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.axis("off")
        # coloured left border strip
        ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                    linewidth=0, facecolor="white", zorder=0))
        ax.add_patch(plt.Rectangle((0, 0), 0.06, 1, color=color, zorder=1))
        ax.text(0.12, 0.72, label, fontsize=9, color="#6b7280",
                fontweight="bold", va="center", transform=ax.transAxes)
        ax.text(0.12, 0.35, value, fontsize=18, color="#111827",
                fontweight="bold", va="center", transform=ax.transAxes)
        for spine in ax.spines.values():
            spine.set_edgecolor("#e5e7eb"); spine.set_linewidth(1)
    fig.suptitle("Executive KPI Dashboard", fontsize=13, fontweight="bold",
                 color=C_DARK, y=1.01)
    plt.tight_layout(pad=0.6)
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Annual Revenue & Profit (grouped bar + line)
# ══════════════════════════════════════════════════════════════════════════════
def chart_annual():
    years   = [2021, 2022, 2023, 2024, 2025]
    revenue = [35.72, 35.33, 35.53, 35.47, 35.09]
    profit  = [15.33, 15.17, 15.25, 15.29, 15.11]

    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("#fafafa")

    x = np.arange(len(years))
    w = 0.55
    bars = ax1.bar(x, revenue, w, color=C_INDIGO, alpha=0.88, label="Revenue ($M)", zorder=3)
    ax1.bar_label(bars, labels=[f"${v:.1f}M" for v in revenue],
                  padding=3, fontsize=8.5, color=C_DARK, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(x, profit, "o-", color=C_EMERALD, linewidth=2.5, markersize=7,
             label="Profit ($M)", zorder=4)
    for xi, yi in zip(x, profit):
        ax2.annotate(f"${yi:.1f}M", (xi, yi), textcoords="offset points",
                     xytext=(0, 9), ha="center", fontsize=8, color=C_EMERALD, fontweight="bold")

    ax1.set_xticks(x); ax1.set_xticklabels(years, fontsize=10)
    ax1.set_ylabel("Revenue ($M)", color=C_INDIGO, fontsize=10)
    ax2.set_ylabel("Profit ($M)",  color=C_EMERALD, fontsize=10)
    ax1.yaxis.label.set_color(C_INDIGO)
    ax1.tick_params(axis="y", colors=C_INDIGO)
    ax2.tick_params(axis="y", colors=C_EMERALD)
    ax1.set_ylim(0, 45); ax2.set_ylim(0, 22)
    ax1.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ax1.set_title("Annual Revenue & Profit (2021–2025)", fontsize=12,
                  fontweight="bold", color=C_DARK, pad=10)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Monthly Revenue Trend (last 24 months)
# ══════════════════════════════════════════════════════════════════════════════
def chart_monthly():
    labels = [
        "Jan-24","Feb-24","Mar-24","Apr-24","May-24","Jun-24",
        "Jul-24","Aug-24","Sep-24","Oct-24","Nov-24","Dec-24",
        "Jan-25","Feb-25","Mar-25","Apr-25","May-25","Jun-25",
        "Jul-25","Aug-25","Sep-25","Oct-25","Nov-25","Dec-25",
    ]
    values = [
        2.51,2.12,2.75,2.64,2.58,2.64,
        2.83,2.86,2.75,2.89,4.35,4.53,
        2.44,2.02,2.79,2.54,2.42,2.62,
        2.84,2.96,2.84,2.79,4.27,4.56,
    ]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")
    x = np.arange(len(labels))
    ax.fill_between(x, values, alpha=0.18, color=C_INDIGO)
    ax.plot(x, values, "o-", color=C_INDIGO, linewidth=2, markersize=4)
    # highlight Nov/Dec peaks
    peak_idx = [10, 11, 22, 23]
    for i in peak_idx:
        ax.plot(i, values[i], "o", color=C_ROSE, markersize=9, zorder=5)
        ax.annotate(f"${values[i]:.2f}M", (i, values[i]),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=7.5, color=C_ROSE, fontweight="bold")
    ax.set_xticks(x[::2]); ax.set_xticklabels(labels[::2], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Revenue ($M)", fontsize=10)
    ax.set_title("Monthly Revenue Trend — 2024 & 2025 (Peak: Nov–Dec)", fontsize=12,
                 fontweight="bold", color=C_DARK, pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Sales Channel & Customer Segment (2 pies side by side)
# ══════════════════════════════════════════════════════════════════════════════
def chart_channel_segment():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.patch.set_facecolor("white")

    # Sales channel
    ch_labels = ["Mobile App", "Website", "Marketplace", "Social Media"]
    ch_values = [70.83, 61.85, 26.70, 17.75]
    wedges, texts, autotexts = ax1.pie(
        ch_values, labels=ch_labels, autopct="%1.1f%%",
        colors=[C_INDIGO, C_EMERALD, C_AMBER, C_ROSE],
        startangle=140, wedgeprops=dict(width=0.58, edgecolor="white", linewidth=2),
        pctdistance=0.78
    )
    for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold"); at.set_color("white")
    for t  in texts:     t.set_fontsize(9.5)
    ax1.set_title("Revenue by Sales Channel ($M)", fontsize=11,
                  fontweight="bold", color=C_DARK, pad=12)
    ax1.text(0, 0, "$177M\nTotal", ha="center", va="center", fontsize=9,
             fontweight="bold", color=C_DARK)

    # Customer segment
    seg_labels = ["Consumer", "Premium", "VIP", "Business"]
    seg_values = [97.20, 44.27, 17.90, 17.76]
    wedges2, texts2, autos2 = ax2.pie(
        seg_values, labels=seg_labels, autopct="%1.1f%%",
        colors=[C_INDIGO, C_PURPLE, C_ROSE, C_CYAN],
        startangle=140, wedgeprops=dict(width=0.58, edgecolor="white", linewidth=2),
        pctdistance=0.78
    )
    for at in autos2: at.set_fontsize(9); at.set_fontweight("bold"); at.set_color("white")
    for t  in texts2: t.set_fontsize(9.5)
    ax2.set_title("Revenue by Customer Segment ($M)", fontsize=11,
                  fontweight="bold", color=C_DARK, pad=12)
    ax2.text(0, 0, "4 Segments", ha="center", va="center", fontsize=8.5,
             fontweight="bold", color=C_DARK)

    fig.suptitle("Sales Channel & Customer Segment Distribution", fontsize=12,
                 fontweight="bold", color=C_DARK, y=1.0)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Product Category Revenue & Profit (grouped horizontal bar)
# ══════════════════════════════════════════════════════════════════════════════
def chart_product():
    cats    = ["Electronics","Jewelry","Home Appliances","Automotive",
               "Sports & Outdoors","Home & Kitchen","Baby & Kids","Health & Wellness"]
    rev     = [41.15, 25.56, 24.84, 16.45, 15.73, 10.97, 9.69, 9.23]
    profit  = [14.10, 10.39, 10.29,  6.48,  7.23,  5.20, None, None]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")

    y  = np.arange(len(cats))
    h  = 0.38
    ax.barh(y + h/2, rev,    h, color=C_INDIGO, alpha=0.88, label="Revenue ($M)")
    prof_vals = [p if p else 0 for p in profit]
    ax.barh(y - h/2, prof_vals, h, color=C_EMERALD, alpha=0.88, label="Profit ($M)")

    ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=9.5)
    ax.set_xlabel("$M", fontsize=10)
    ax.set_title("Product Category — Revenue vs Profit ($M)", fontsize=12,
                 fontweight="bold", color=C_DARK, pad=10)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.invert_yaxis()
    # value labels
    for i, v in enumerate(rev):
        ax.text(v + 0.3, i + h/2, f"${v:.1f}M", va="center", fontsize=8, color=C_INDIGO, fontweight="bold")
    for i, v in enumerate(prof_vals):
        if v:
            ax.text(v + 0.3, i - h/2, f"${v:.1f}M", va="center", fontsize=8, color=C_EMERALD, fontweight="bold")
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 6 — Regional Revenue (horizontal bar) + Order Status (donut)
# ══════════════════════════════════════════════════════════════════════════════
def chart_region_status():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    # Region bar
    regions = ["South", "Central", "West", "East", "North"]
    rvals   = [55.59, 37.17, 34.76, 27.05, 22.57]
    colors_r = [C_INDIGO, C_PURPLE, C_EMERALD, C_CYAN, C_AMBER]
    bars = ax1.barh(regions, rvals, color=colors_r, alpha=0.88, edgecolor="white")
    ax1.set_facecolor("#fafafa")
    ax1.set_xlabel("Revenue ($M)", fontsize=10)
    ax1.set_title("Revenue by Region ($M)", fontsize=11, fontweight="bold", color=C_DARK, pad=10)
    ax1.grid(axis="x", linestyle="--", alpha=0.4)
    for bar, v in zip(bars, rvals):
        ax1.text(v + 0.4, bar.get_y() + bar.get_height()/2,
                 f"${v:.1f}M", va="center", fontsize=9, fontweight="bold")

    # Order status donut
    os_labels = ["Completed", "Returned", "Cancelled", "Pending"]
    os_vals   = [113559, 9462, 8398, 6697]
    os_colors = [C_EMERALD, C_ROSE, C_AMBER, C_CYAN]
    wedges, texts, autos = ax2.pie(
        os_vals, labels=os_labels, autopct="%1.1f%%",
        colors=os_colors, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        pctdistance=0.78
    )
    for at in autos: at.set_fontsize(9); at.set_fontweight("bold"); at.set_color("white")
    for t  in texts: t.set_fontsize(9.5)
    ax2.set_title("Order Status Distribution", fontsize=11,
                  fontweight="bold", color=C_DARK, pad=12)
    ax2.text(0, 0, "138K\nOrders", ha="center", va="center", fontsize=9,
             fontweight="bold", color=C_DARK)

    fig.suptitle("Geographic Revenue & Order Status", fontsize=12,
                 fontweight="bold", color=C_DARK, y=1.0)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 7 — Quarterly Revenue Trend (clustered bar by year)
# ══════════════════════════════════════════════════════════════════════════════
def chart_quarterly():
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    y2023 = [7.20, 7.85, 8.53, 11.94]
    y2024 = [7.38, 7.85, 8.45, 11.78]
    y2025 = [7.25, 7.57, 8.64, 11.62]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#fafafa")

    x = np.arange(len(quarters))
    w = 0.26
    b1 = ax.bar(x - w, y2023, w, label="2023", color=C_INDIGO,  alpha=0.88)
    b2 = ax.bar(x,     y2024, w, label="2024", color=C_EMERALD, alpha=0.88)
    b3 = ax.bar(x + w, y2025, w, label="2025", color=C_AMBER,   alpha=0.88)

    for bars in [b1, b2, b3]:
        ax.bar_label(bars, labels=[f"${v:.1f}M" for v in [b.get_height() for b in bars]],
                     padding=2, fontsize=7.5, fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels(quarters, fontsize=11)
    ax.set_ylabel("Revenue ($M)", fontsize=10)
    ax.set_title("Quarterly Revenue Comparison (2023–2025)", fontsize=12,
                 fontweight="bold", color=C_DARK, pad=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 8 — Delivery Status & Return/Cancellation Analysis
# ══════════════════════════════════════════════════════════════════════════════
def chart_delivery_returns():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    # Delivery status stacked-look bar
    del_labels = ["On Time", "Cancelled", "Delayed", "Early"]
    del_vals   = [86916, 24557, 16886, 9757]
    del_colors = [C_EMERALD, C_AMBER, C_ROSE, C_CYAN]
    ax1.set_facecolor("#fafafa")
    bars = ax1.bar(del_labels, del_vals, color=del_colors, alpha=0.9, edgecolor="white", linewidth=1.5)
    ax1.bar_label(bars, labels=[f"{v:,}" for v in del_vals],
                  padding=4, fontsize=9, fontweight="bold")
    for bar, color in zip(bars, del_colors):
        pct = bar.get_height() / sum(del_vals) * 100
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                 f"{pct:.1f}%", ha="center", va="center",
                 fontsize=10, fontweight="bold", color="white")
    ax1.set_ylabel("Number of Orders", fontsize=10)
    ax1.set_title("Delivery Status Breakdown\n(138,116 Orders)", fontsize=11,
                  fontweight="bold", color=C_DARK, pad=8)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.set_ylim(0, max(del_vals) * 1.15)

    # Return vs Cancellation rate gauge-style
    metrics = ["Return Rate\n6.85%", "Cancel Rate\n6.08%", "On-Time Rate\n62.9%", "Completion Rate\n82.2%"]
    vals    = [6.85, 6.08, 62.9, 82.2]
    colors2 = [C_ROSE, C_AMBER, C_EMERALD, C_INDIGO]
    ax2.set_facecolor("#fafafa")
    y_pos = np.arange(len(metrics))
    hbars = ax2.barh(y_pos, vals, color=colors2, alpha=0.88,
                     edgecolor="white", height=0.5)
    ax2.set_yticks(y_pos); ax2.set_yticklabels(metrics, fontsize=9.5)
    ax2.set_xlabel("Percentage (%)", fontsize=10)
    ax2.set_title("Key Operational Metrics (%)", fontsize=11,
                  fontweight="bold", color=C_DARK, pad=8)
    ax2.set_xlim(0, 100)
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    for bar, v in zip(hbars, vals):
        ax2.text(v + 1.5, bar.get_y() + bar.get_height()/2,
                 f"{v:.1f}%", va="center", fontsize=9, fontweight="bold")

    fig.suptitle("Delivery Performance & Operational Metrics", fontsize=12,
                 fontweight="bold", color=C_DARK, y=1.0)
    plt.tight_layout()
    return fig_to_stream(fig)

# ══════════════════════════════════════════════════════════════════════════════
# BUILD THE DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════
def build_report():
    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────────
    from docx.oxml.ns import nsmap
    section = doc.sections[0]
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.2)
    section.right_margin  = Cm(2.2)

    # ── COVER BANNER TABLE ────────────────────────────────────────────────────
    banner = doc.add_table(rows=1, cols=1)
    banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = banner.cell(0, 0)
    set_cell_bg(cell, "1e1b4b")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run("🛒  E-Commerce Sales & Customer Analytics Dashboard")
    run.bold = True; run.font.size = Pt(20); run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    p2 = cell.add_paragraph("Project Report")
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.runs[0]; r2.font.size = Pt(13); r2.font.color.rgb = RGBColor(0xa5, 0xb4, 0xfc)

    p3 = cell.add_paragraph("Submitted by: Himanshu Mandal  |  Dataset: 138,116 Transactions (2021–2025)")
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = Pt(18)
    r3 = p3.runs[0]; r3.font.size = Pt(10); r3.font.color.rgb = RGBColor(0xe0, 0xe7, 0xff)

    doc.add_paragraph()  # spacer

    # ── SECTION 1 — Executive Summary ─────────────────────────────────────────
    add_heading(doc, "1. Executive Summary", 1)
    add_body(doc, (
        "This project presents a comprehensive, interactive E-Commerce Sales and Customer Analytics "
        "Dashboard built entirely in Python. It leverages a real-world dataset of over 138,000 "
        "transactions spanning five years (2021–2025), covering 24,911 unique customers across "
        "multiple countries, sales channels, and product categories. The dashboard is powered by "
        "Streamlit (frontend) and pandas/Plotly (backend), offering nine fully interactive "
        "analytical pages covering KPIs, sales trends, customer analytics, product performance, "
        "geographic insights, delivery performance, returns, and marketing attribution."
    ), size=11)

    # ── KPI PANEL CHART ───────────────────────────────────────────────────────
    add_heading(doc, "1.1 Key Performance Indicators", 2, color=C_INDIGO)
    add_body(doc, "The panel below summarises the top-line business metrics across all 5 years of data:", size=10)
    add_chart(doc, chart_kpi_panel(), width=Inches(6.3),
              caption="Figure 1 — Executive KPI Dashboard (2021–2025, all segments)")

    # ── SECTION 2 — Sales Trends ──────────────────────────────────────────────
    add_heading(doc, "2. Sales Trends Analysis", 1)
    add_body(doc, (
        "Revenue is remarkably stable year-over-year, hovering between $35.1M and $35.7M annually. "
        "A clear seasonal pattern emerges with November and December accounting for nearly 30% more "
        "revenue than the monthly average — driven by holiday shopping. Q4 consistently outperforms "
        "all other quarters with $11.6–11.9M in revenue vs $7.2–8.6M in Q1–Q3."
    ), size=11)

    add_heading(doc, "2.1 Annual Revenue & Profit", 2, color=C_INDIGO)
    add_chart(doc, chart_annual(), width=Inches(6.0),
              caption="Figure 2 — Annual Revenue ($M, bars) vs Profit ($M, line) with dual y-axis (2021–2025)")

    add_heading(doc, "2.2 Monthly Revenue Trend", 2, color=C_INDIGO)
    add_body(doc, (
        "Monthly analysis of the last 24 months (2024–2025) confirms strong seasonality. "
        "Revenue dips to ~$2.0–2.1M in February and peaks at ~$4.3–4.6M in November/December "
        "(highlighted in red). The pattern is highly consistent across both years, "
        "confirming reliable seasonal demand cycles."
    ), size=11)
    add_chart(doc, chart_monthly(), width=Inches(6.3),
              caption="Figure 3 — Monthly Revenue Trend 2024–2025 with seasonal peaks highlighted")

    add_heading(doc, "2.3 Quarterly Revenue Comparison", 2, color=C_INDIGO)
    add_body(doc, (
        "Q4 dominates across all three years due to the November–December holiday effect. "
        "Q3 shows moderate strength ($8.4–8.6M) while Q1 and Q2 are the softest quarters. "
        "Revenue is slightly declining in 2025 ($35.09M) vs the 2021 peak ($35.72M), "
        "suggesting maturation effects or increased competition."
    ), size=11)
    add_chart(doc, chart_quarterly(), width=Inches(6.0),
              caption="Figure 4 — Quarterly Revenue Comparison 2023 vs 2024 vs 2025 (clustered bar chart)")

    # ── SECTION 3 — Channel & Segment ─────────────────────────────────────────
    add_heading(doc, "3. Sales Channel & Customer Segment", 1)
    add_body(doc, (
        "Mobile App is the dominant sales channel at 40% of total revenue ($70.8M), "
        "followed by Website at 35% ($61.9M). Together, these digital channels account for "
        "75% of revenue. The Consumer segment is the largest at 54.9% ($97.2M), with Premium "
        "customers contributing 25% ($44.3M). VIP and Business segments together represent ~20% "
        "but typically carry higher average order values and CLV."
    ), size=11)
    add_chart(doc, chart_channel_segment(), width=Inches(6.3),
              caption="Figure 5 — Revenue split by Sales Channel (left) and Customer Segment (right)")

    # ── SECTION 4 — Product Analytics ─────────────────────────────────────────
    add_heading(doc, "4. Product Category Performance", 1)
    add_body(doc, (
        "Electronics leads all product categories at $41.1M in revenue and $14.1M in profit, "
        "representing 23.2% of total revenue. Jewelry ($25.6M) and Home Appliances ($24.8M) "
        "follow closely. The combined top-3 categories account for over 51% of total revenue. "
        "Sports & Outdoors, despite lower revenue than Automotive, achieves a higher profit ($7.2M vs $6.5M), "
        "indicating better margin efficiency. Health & Wellness and Baby & Kids represent "
        "growth opportunity categories with lower current revenue but high demand potential."
    ), size=11)
    add_chart(doc, chart_product(), width=Inches(6.3),
              caption="Figure 6 — Product Category Revenue vs Profit ($M) — horizontal grouped bar chart")

    # ── SECTION 5 — Geographic ────────────────────────────────────────────────
    add_heading(doc, "5. Geographic & Order Status Analysis", 1)
    add_body(doc, (
        "The South region leads revenue at $55.6M (31.4%), more than double the North's $22.6M (12.7%). "
        "Central ($37.2M) and West ($34.8M) are mid-tier contributors. Geographically, "
        "countries such as the USA, Germany, and UAE are key markets based on customer profile data. "
        "Order status analysis reveals a high completion rate of 82.2%, with returns (6.85%) "
        "and cancellations (6.08%) representing significant but manageable revenue leakage."
    ), size=11)
    add_chart(doc, chart_region_status(), width=Inches(6.3),
              caption="Figure 7 — Regional Revenue ($M) and Order Status Distribution (138K orders)")

    # ── SECTION 6 — Delivery & Operations ─────────────────────────────────────
    add_heading(doc, "6. Delivery Performance & Operational Metrics", 1)
    add_body(doc, (
        "62.9% of orders are delivered on time, while 12.2% are delayed and 17.8% are cancelled "
        "(includes orders that never shipped). Only 7.1% arrive early. Improving on-time delivery "
        "from 62.9% to above 75% should be a key operational priority. "
        "The return rate of 6.85% and cancellation rate of 6.08% are within industry norms "
        "but represent over $12M in potential lost revenue annually at current scale."
    ), size=11)
    add_chart(doc, chart_delivery_returns(), width=Inches(6.3),
              caption="Figure 8 — Delivery Status Breakdown and Key Operational KPIs (%)")

    # ── SECTION 7 — Key Findings ──────────────────────────────────────────────
    add_heading(doc, "7. Key Findings & Business Recommendations", 1)
    findings = [
        ("Revenue Stability",     "Revenue is nearly identical year-over-year (~$35.1–35.7M), suggesting a mature market. Growth strategy should focus on new segments or geographies rather than organic volume."),
        ("Seasonal Peak",         "Nov–Dec generates ~$4.3–4.6M/month vs $2.4–2.9M in off-peak months — a 60–80% spike. Inventory, staffing, and marketing budgets must be pre-positioned for Q4."),
        ("Mobile App Dominance",  "40% of revenue flows through the Mobile App. Prioritising app UX, push notifications, and app-exclusive promotions is critical for revenue growth."),
        ("Consumer Segment",      "Consumer customers (54.9% of revenue) are the backbone — but VIP and Premium customers likely have 3–5× higher CLV. Segment-specific retention programs would yield high ROI."),
        ("Electronics Leadership","Electronics alone contributes 23.2% of revenue and 18.5% of total profit. Expanding electronics sub-categories and exclusive brand partnerships is a high-priority growth lever."),
        ("Return/Cancel Leakage", "A combined ~13% return + cancellation rate represents ~$23M in gross revenue at risk annually. Root-cause analysis by product category and return reason should drive corrective action."),
        ("Delivery Performance",  "62.9% on-time rate is below the 80%+ benchmark for leading e-commerce platforms. Improving last-mile logistics, especially in the South and Central regions, will directly impact customer satisfaction and repeat purchase rates."),
        ("South Region",          "The South region at $55.6M (31.4%) outperforms all others. Deepening penetration in East ($27.1M) and North ($22.6M) with targeted campaigns could add $10–15M in incremental revenue."),
    ]
    for title, text in findings:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        r1 = p.add_run(f"▶  {title}: ")
        r1.bold = True; r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(0x4f, 0x46, 0xe5)
        r2 = p.add_run(text)
        r2.font.size = Pt(11)

    # ── SECTION 8 — Tech Stack ────────────────────────────────────────────────
    add_heading(doc, "8. Technologies & Libraries", 1)

    tech_table = doc.add_table(rows=1, cols=4)
    tech_table.style = "Table Grid"
    hdr_cells = tech_table.rows[0].cells
    for cell, label in zip(hdr_cells, ["Layer", "Library", "Version", "Purpose"]):
        set_cell_bg(cell, "1e1b4b")
        p = cell.paragraphs[0]
        run = p.add_run(label)
        run.bold = True; run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    tech_rows = [
        ("Frontend",       "Streamlit",   "1.35.0", "Web UI, layout, reactivity, widgets"),
        ("Visualisation",  "Plotly",      "5.22.0", "Interactive charts (bar, line, pie, etc.)"),
        ("Backend",        "Python",      "3.10+",  "Core programming language"),
        ("Data Processing","pandas",      "2.2.2",  "Data loading, merging, grouping, time-series"),
        ("Numerics",       "numpy",       "1.26.4", "Array operations & calculations"),
        ("Statistics",     "scipy",       "1.13.1", "Statistical distributions & functions"),
        ("Report Gen",     "python-docx", "1.1.2",  "Word document generation"),
        ("Excel Support",  "openpyxl",    "3.1.2",  "Excel read/write support"),
    ]
    alt_colors = ["f7f8fa", "FFFFFF"]
    for i, row_data in enumerate(tech_rows):
        row = tech_table.add_row()
        for j, (cell, val) in enumerate(zip(row.cells, row_data)):
            set_cell_bg(cell, alt_colors[i % 2])
            p = cell.paragraphs[0]
            run = p.add_run(val)
            run.font.size = Pt(10)
            if j == 0: run.bold = True; run.font.color.rgb = RGBColor(0x4f, 0x46, 0xe5)

    doc.add_paragraph()

    # ── SECTION 9 — Architecture ──────────────────────────────────────────────
    add_heading(doc, "9. Project Architecture & File Structure", 1)
    add_body(doc, (
        "The project follows a single-file architecture — app.py contains all backend data "
        "processing logic and frontend Streamlit UI code. Data flows from CSV files → "
        "pandas DataFrames → plotly charts → Streamlit pages, all cached with @st.cache_data "
        "for performance."
    ), size=11)

    file_table = doc.add_table(rows=1, cols=3)
    file_table.style = "Table Grid"
    for cell, label in zip(file_table.rows[0].cells, ["File", "Format", "Description"]):
        set_cell_bg(cell, "312e81")
        p = cell.paragraphs[0]
        run = p.add_run(label)
        run.bold = True; run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    file_rows = [
        ("app.py",                                     ".py",   "Main application — backend + Streamlit frontend"),
        ("requirements.txt",                           ".txt",  "Python dependency list with pinned versions"),
        ("README.md",                                  ".md",   "Project overview, setup instructions, dataset link"),
        ("HimanshuMandal_ProjectReport.docx",          ".docx", "This project report with charts and analysis"),
        ("ecommerce_sales_customer_analytics_150k.csv",".csv",  "Primary transaction dataset — 138K rows, 46 cols"),
        ("customer_master.csv",                        ".csv",  "Customer profiles — 24,911 unique customers"),
        ("order_items.csv",                            ".csv",  "Line-level order item data with financials"),
        ("product_catalog.csv",                        ".csv",  "Product metadata — categories, brands, ratings"),
        ("dataset_statistics.csv",                     ".csv",  "Pre-computed aggregate summary statistics"),
    ]
    for i, (fname, fmt, desc) in enumerate(file_rows):
        row = file_table.add_row()
        cells = row.cells
        set_cell_bg(cells[0], alt_colors[i % 2])
        set_cell_bg(cells[1], alt_colors[i % 2])
        set_cell_bg(cells[2], alt_colors[i % 2])
        r0 = cells[0].paragraphs[0].add_run(fname)
        r0.font.size = Pt(9); r0.bold = True
        r1 = cells[1].paragraphs[0].add_run(fmt)
        r1.font.size = Pt(9); r1.font.color.rgb = RGBColor(0x4f, 0x46, 0xe5)
        r2 = cells[2].paragraphs[0].add_run(desc)
        r2.font.size = Pt(9)

    doc.add_paragraph()

    # ── SECTION 10 — Setup ────────────────────────────────────────────────────
    add_heading(doc, "10. Setup & Run Instructions", 1)
    steps = [
        ("Step 1", "Place all CSV files and app.py in the same project directory."),
        ("Step 2", "Install dependencies:   pip install -r requirements.txt"),
        ("Step 3", "Launch the dashboard:   streamlit run app.py"),
        ("Step 4", "Open browser at:        http://localhost:8501"),
    ]
    for step, desc in steps:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(f"{step}:  ")
        r1.bold = True; r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(0x4f, 0x46, 0xe5)
        r2 = p.add_run(desc)
        r2.font.size = Pt(11)

    doc.add_paragraph()

    # ── SECTION 11 — Conclusion ───────────────────────────────────────────────
    add_heading(doc, "11. Conclusion", 1)
    add_body(doc, (
        "This project demonstrates a complete end-to-end data analytics pipeline built entirely in Python, "
        "transforming raw e-commerce transaction data into rich, actionable business intelligence. "
        "The interactive Streamlit dashboard makes complex multi-dimensional analysis accessible to "
        "business stakeholders without requiring any technical expertise. The eight charts embedded in "
        "this report confirm that revenue is stable but seasonal, Mobile App is the dominant channel, "
        "Electronics leads product performance, and operational improvements in delivery and returns "
        "represent the highest-value near-term opportunities. The architecture is modular and "
        "scalable — datasets can be swapped or extended, and additional analytical pages can be "
        "added with minimal effort."
    ), size=11, space_after=8)

    # ── FOOTER LINE ───────────────────────────────────────────────────────────
    doc.add_paragraph()
    footer_p = doc.add_paragraph(
        "Himanshu Mandal  ·  E-Commerce Sales & Customer Analytics  ·  Python · Streamlit · Plotly  ·  2021–2025"
    )
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = footer_p.runs[0]
    fr.font.size = Pt(9); fr.font.italic = True
    fr.font.color.rgb = RGBColor(0x9c, 0xa3, 0xaf)

    # ── SAVE ─────────────────────────────────────────────────────────────────
    out_path = "HimanshuMandal_ProjectReport.docx"
    doc.save(out_path)
    print(f"✅ Saved: {out_path}")
    return out_path

if __name__ == "__main__":
    build_report()
