"""
E-Commerce Sales & Customer Analytics Dashboard
================================================
Author : Himanshu Mandal
Backend : Python (pandas, numpy, scipy)
Frontend: Streamlit + Plotly
Datasets:
  - ecommerce_sales_customer_analytics_150k.csv  (main transactions)
  - customer_master.csv                           (customer profiles)
  - order_items.csv                               (line-level order data)
  - product_catalog.csv                           (product metadata)
  - dataset_statistics.csv                        (pre-computed summary)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Main background */
    .main { background-color: #f0f2f6; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #4f46e5;
        margin-bottom: 8px;
    }
    .kpi-label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin-top: 4px;
    }
    .kpi-delta {
        font-size: 13px;
        color: #10b981;
        margin-top: 2px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    [data-testid="stSidebar"] .css-1d391kg { color: white; }

    /* Section headers */
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #1e1b4b;
        border-bottom: 3px solid #4f46e5;
        padding-bottom: 6px;
        margin-bottom: 18px;
    }

    /* Plotly chart container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING  (cached for performance)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading datasets…")
def load_data():
    main = pd.read_csv("ecommerce_sales_customer_analytics_150k.csv", low_memory=False)
    customers = pd.read_csv("customer_master.csv")
    order_items = pd.read_csv("order_items.csv")
    products = pd.read_csv("product_catalog.csv")
    stats = pd.read_csv("dataset_statistics.csv")

    # ── Parse dates ──────────────────────────────────────────────────────────
    main["order_date"] = pd.to_datetime(main["order_date"], errors="coerce")
    main["year"] = main["order_date"].dt.year
    main["month"] = main["order_date"].dt.month
    main["month_name"] = main["order_date"].dt.strftime("%b")
    main["year_month"] = main["order_date"].dt.to_period("M").astype(str)
    main["quarter"] = main["order_date"].dt.to_period("Q").astype(str)
    main["day_of_week"] = main["order_date"].dt.day_name()

    # ── Clean numeric columns ─────────────────────────────────────────────────
    num_cols = ["gross_sales", "net_sales", "profit", "discount_amount",
                "tax_amount", "shipping_cost", "product_cost",
                "profit_margin_percentage", "customer_lifetime_value",
                "loyalty_points_earned", "loyalty_points_redeemed",
                "quantity", "customer_age", "delivery_days"]
    for col in num_cols:
        if col in main.columns:
            main[col] = pd.to_numeric(main[col], errors="coerce")

    main["is_repeat_customer"] = main["is_repeat_customer"].astype(str).str.strip().str.lower() == "true"

    return main, customers, order_items, products, stats


main_df, customers_df, order_items_df, products_df, stats_df = load_data()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR  –  GLOBAL FILTERS
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    "<h2 style='color:white; text-align:center;'>🛒 E-Commerce Analytics</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("<hr style='border-color:#4f46e5;'>", unsafe_allow_html=True)

st.sidebar.markdown("<p style='color:#a5b4fc; font-weight:600;'>NAVIGATION</p>", unsafe_allow_html=True)
pages = [
    "📊 Executive Summary",
    "📈 Sales Trends",
    "👥 Customer Analytics",
    "📦 Product Analytics",
    "🌍 Geographic Analysis",
    "🚚 Order & Delivery",
    "↩️ Returns & Cancellations",
    "💳 Payment & Marketing",
    "🔍 Data Explorer",
]
selected_page = st.sidebar.radio("", pages, label_visibility="collapsed")

st.sidebar.markdown("<hr style='border-color:#4f46e5;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#a5b4fc; font-weight:600;'>GLOBAL FILTERS</p>", unsafe_allow_html=True)

# Year filter
available_years = sorted(main_df["year"].dropna().unique().astype(int).tolist())
selected_years = st.sidebar.multiselect(
    "Year", available_years, default=available_years, key="year_filter"
)

# Region filter
regions = ["All"] + sorted(main_df["region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions, key="region_filter")

# Segment filter
segments = ["All"] + sorted(main_df["customer_segment"].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Customer Segment", segments, key="segment_filter")

# Channel filter
channels = ["All"] + sorted(main_df["sales_channel"].dropna().unique().tolist())
selected_channel = st.sidebar.selectbox("Sales Channel", channels, key="channel_filter")

# ── Apply filters ─────────────────────────────────────────────────────────────
df = main_df.copy()
if selected_years:
    df = df[df["year"].isin(selected_years)]
if selected_region != "All":
    df = df[df["region"] == selected_region]
if selected_segment != "All":
    df = df[df["customer_segment"] == selected_segment]
if selected_channel != "All":
    df = df[df["sales_channel"] == selected_channel]

st.sidebar.markdown("<hr style='border-color:#4f46e5;'>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"<p style='color:#a5b4fc; font-size:12px;'>Showing <b style='color:white;'>{len(df):,}</b> records</p>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
CHART_THEME = "plotly_white"
PALETTE = px.colors.qualitative.Vivid
INDIGO = "#4f46e5"
EMERALD = "#10b981"
ROSE = "#f43f5e"
AMBER = "#f59e0b"


def kpi_card(label, value, delta=None, color="#4f46e5"):
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"""
        <div class='kpi-card' style='border-left-color:{color};'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def fmt_currency(val, prefix="$"):
    if abs(val) >= 1_000_000:
        return f"{prefix}{val/1_000_000:.2f}M"
    elif abs(val) >= 1_000:
        return f"{prefix}{val/1_000:.1f}K"
    return f"{prefix}{val:.2f}"


def section_header(title):
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 1 – EXECUTIVE SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
if selected_page == "📊 Executive Summary":
    st.markdown("## 📊 Executive Summary")
    st.caption("High-level KPIs and business health metrics across all filtered data.")

    total_revenue = df["net_sales"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_customers = df["customer_id"].nunique()
    avg_order_value = df["net_sales"].mean()
    avg_margin = df["profit_margin_percentage"].mean()
    avg_rating = df["customer_rating"].mean()
    repeat_rate = df["is_repeat_customer"].mean() * 100

    # Row 1 KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Revenue", fmt_currency(total_revenue), color=INDIGO)
    with c2:
        kpi_card("Total Profit", fmt_currency(total_profit), color=EMERALD)
    with c3:
        kpi_card("Total Orders", f"{total_orders:,}", color=AMBER)
    with c4:
        kpi_card("Unique Customers", f"{total_customers:,}", color="#8b5cf6")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2 KPIs
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card("Avg Order Value", fmt_currency(avg_order_value), color=ROSE)
    with c6:
        kpi_card("Avg Profit Margin", f"{avg_margin:.1f}%", color="#06b6d4")
    with c7:
        kpi_card("Avg Customer Rating", f"{avg_rating:.2f} / 5", color=AMBER)
    with c8:
        kpi_card("Repeat Customer Rate", f"{repeat_rate:.1f}%", color=EMERALD)

    st.markdown("---")

    # Revenue & Profit by Year
    section_header("Annual Revenue & Profit")
    annual = df.groupby("year").agg(Revenue=("net_sales", "sum"), Profit=("profit", "sum")).reset_index()
    fig_annual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_annual.add_trace(
        go.Bar(x=annual["year"], y=annual["Revenue"], name="Revenue", marker_color=INDIGO, opacity=0.85),
        secondary_y=False,
    )
    fig_annual.add_trace(
        go.Scatter(x=annual["year"], y=annual["Profit"], name="Profit", mode="lines+markers",
                   line=dict(color=EMERALD, width=3), marker=dict(size=8)),
        secondary_y=True,
    )
    fig_annual.update_layout(template=CHART_THEME, height=360,
                              legend=dict(orientation="h", yanchor="bottom", y=1.02))
    fig_annual.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig_annual.update_yaxes(title_text="Profit ($)", secondary_y=True)
    st.plotly_chart(fig_annual, use_container_width=True)

    # Row: Sales Channel mix + Order Status mix
    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Revenue by Sales Channel")
        ch = df.groupby("sales_channel")["net_sales"].sum().reset_index()
        fig_ch = px.pie(ch, names="sales_channel", values="net_sales",
                        color_discrete_sequence=PALETTE, hole=0.42)
        fig_ch.update_traces(textposition="outside", textinfo="percent+label")
        fig_ch.update_layout(template=CHART_THEME, height=340, showlegend=False)
        st.plotly_chart(fig_ch, use_container_width=True)

    with col_r:
        section_header("Order Status Distribution")
        os_ = df["order_status"].value_counts().reset_index()
        os_.columns = ["Status", "Count"]
        fig_os = px.bar(os_, x="Count", y="Status", orientation="h",
                        color="Count", color_continuous_scale="Purples")
        fig_os.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_os, use_container_width=True)

    # Pre-computed dataset stats
    section_header("Dataset Overview")
    st.dataframe(stats_df, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 2 – SALES TRENDS
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "📈 Sales Trends":
    st.markdown("## 📈 Sales Trends")

    # Monthly trend
    section_header("Monthly Revenue & Profit Trend")
    monthly = (df.groupby("year_month")
               .agg(Revenue=("net_sales", "sum"), Profit=("profit", "sum"), Orders=("order_id", "nunique"))
               .reset_index()
               .sort_values("year_month"))
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["Revenue"],
                                   name="Revenue", fill="tozeroy",
                                   line=dict(color=INDIGO, width=2)), secondary_y=False)
    fig_trend.add_trace(go.Scatter(x=monthly["year_month"], y=monthly["Profit"],
                                   name="Profit", line=dict(color=EMERALD, width=2, dash="dot")),
                        secondary_y=True)
    fig_trend.update_layout(template=CHART_THEME, height=400,
                             xaxis_tickangle=-45, legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # Quarterly revenue
        section_header("Quarterly Revenue")
        qtr = df.groupby("quarter")["net_sales"].sum().reset_index().sort_values("quarter")
        fig_q = px.bar(qtr, x="quarter", y="net_sales", color="net_sales",
                       color_continuous_scale="Blues", labels={"net_sales": "Revenue ($)"})
        fig_q.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_q, use_container_width=True)

    with col2:
        # Day-of-week heatmap
        section_header("Orders by Day of Week")
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = df["day_of_week"].value_counts().reindex(dow_order).reset_index()
        dow.columns = ["Day", "Orders"]
        fig_dow = px.bar(dow, x="Day", y="Orders", color="Orders",
                         color_continuous_scale="Purples")
        fig_dow.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_dow, use_container_width=True)

    # Month-over-month growth
    section_header("Month-over-Month Revenue Growth (%)")
    monthly["MoM_Growth"] = monthly["Revenue"].pct_change() * 100
    fig_mom = px.bar(monthly.dropna(subset=["MoM_Growth"]),
                     x="year_month", y="MoM_Growth",
                     color=monthly.dropna(subset=["MoM_Growth"])["MoM_Growth"].apply(
                         lambda x: "Positive" if x >= 0 else "Negative"),
                     color_discrete_map={"Positive": EMERALD, "Negative": ROSE},
                     labels={"MoM_Growth": "Growth (%)", "year_month": "Month"})
    fig_mom.update_layout(template=CHART_THEME, height=360, xaxis_tickangle=-45,
                          showlegend=False)
    st.plotly_chart(fig_mom, use_container_width=True)

    # Revenue by Segment over time
    section_header("Revenue Trend by Customer Segment")
    seg_time = (df.groupby(["year_month", "customer_segment"])["net_sales"]
                .sum().reset_index().sort_values("year_month"))
    fig_seg = px.line(seg_time, x="year_month", y="net_sales", color="customer_segment",
                      color_discrete_sequence=PALETTE,
                      labels={"net_sales": "Revenue ($)", "year_month": "Month",
                              "customer_segment": "Segment"})
    fig_seg.update_layout(template=CHART_THEME, height=380, xaxis_tickangle=-45)
    st.plotly_chart(fig_seg, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 3 – CUSTOMER ANALYTICS
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "👥 Customer Analytics":
    st.markdown("## 👥 Customer Analytics")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Customers", f"{df['customer_id'].nunique():,}", color=INDIGO)
    with col2:
        kpi_card("Avg CLV", fmt_currency(df['customer_lifetime_value'].mean()), color=EMERALD)
    with col3:
        kpi_card("Repeat Rate", f"{df['is_repeat_customer'].mean()*100:.1f}%", color=AMBER)
    with col4:
        kpi_card("Avg Age", f"{df['customer_age'].mean():.0f} yrs", color=ROSE)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Customer Segment Distribution")
        seg = df["customer_segment"].value_counts().reset_index()
        seg.columns = ["Segment", "Count"]
        fig_seg = px.pie(seg, names="Segment", values="Count",
                         color_discrete_sequence=PALETTE, hole=0.4)
        fig_seg.update_traces(textinfo="percent+label")
        fig_seg.update_layout(template=CHART_THEME, height=340, showlegend=False)
        st.plotly_chart(fig_seg, use_container_width=True)

    with col_r:
        section_header("Customer Type Distribution")
        ct = df["customer_type"].value_counts().reset_index()
        ct.columns = ["Type", "Count"]
        fig_ct = px.bar(ct, x="Type", y="Count", color="Type",
                        color_discrete_sequence=PALETTE)
        fig_ct.update_layout(template=CHART_THEME, height=340, showlegend=False)
        st.plotly_chart(fig_ct, use_container_width=True)

    # Age distribution
    col3a, col3b = st.columns(2)
    with col3a:
        section_header("Customer Age Distribution")
        fig_age = px.histogram(df.drop_duplicates("customer_id"), x="customer_age",
                               nbins=30, color_discrete_sequence=[INDIGO],
                               labels={"customer_age": "Age"})
        fig_age.update_layout(template=CHART_THEME, height=320)
        st.plotly_chart(fig_age, use_container_width=True)

    with col3b:
        section_header("Gender Distribution")
        gen = df["gender"].value_counts().reset_index()
        gen.columns = ["Gender", "Count"]
        fig_gen = px.pie(gen, names="Gender", values="Count",
                         color_discrete_sequence=[INDIGO, ROSE, AMBER], hole=0.45)
        fig_gen.update_traces(textinfo="percent+label")
        fig_gen.update_layout(template=CHART_THEME, height=320, showlegend=False)
        st.plotly_chart(fig_gen, use_container_width=True)

    # CLV by Segment
    section_header("Average Customer Lifetime Value by Segment")
    clv_seg = df.groupby("customer_segment")["customer_lifetime_value"].mean().reset_index()
    fig_clv = px.bar(clv_seg, x="customer_segment", y="customer_lifetime_value",
                     color="customer_segment", color_discrete_sequence=PALETTE,
                     labels={"customer_lifetime_value": "Avg CLV ($)", "customer_segment": "Segment"})
    fig_clv.update_layout(template=CHART_THEME, height=340, showlegend=False)
    st.plotly_chart(fig_clv, use_container_width=True)

    # Loyalty Points
    section_header("Loyalty Points Earned vs Redeemed by Segment")
    loy = df.groupby("customer_segment").agg(
        Earned=("loyalty_points_earned", "sum"),
        Redeemed=("loyalty_points_redeemed", "sum")
    ).reset_index()
    fig_loy = go.Figure()
    fig_loy.add_trace(go.Bar(name="Earned", x=loy["customer_segment"], y=loy["Earned"],
                             marker_color=INDIGO))
    fig_loy.add_trace(go.Bar(name="Redeemed", x=loy["customer_segment"], y=loy["Redeemed"],
                             marker_color=AMBER))
    fig_loy.update_layout(barmode="group", template=CHART_THEME, height=340)
    st.plotly_chart(fig_loy, use_container_width=True)

    # Top 15 customers by revenue
    section_header("Top 15 Customers by Revenue")
    top_cust = (df.groupby(["customer_id", "customer_name"])["net_sales"]
                .sum().reset_index().nlargest(15, "net_sales"))
    fig_tc = px.bar(top_cust, x="net_sales", y="customer_name", orientation="h",
                    color="net_sales", color_continuous_scale="Blues",
                    labels={"net_sales": "Revenue ($)", "customer_name": "Customer"})
    fig_tc.update_layout(template=CHART_THEME, height=420, coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_tc, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 4 – PRODUCT ANALYTICS
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "📦 Product Analytics":
    st.markdown("## 📦 Product Analytics")

    # Merge with product catalog via order_items
    oi_prod = order_items_df.merge(products_df, on="product_id", how="left")
    # Also get main df with products
    prod_main = df.copy()

    col1, col2, col3, col4 = st.columns(4)
    total_prods = products_df["product_id"].nunique()
    cats = products_df["product_category"].nunique()
    avg_prod_rating = products_df["product_rating"].mean()
    total_revenue_oi = oi_prod["net_sales"].sum()
    with col1:
        kpi_card("Total Products", f"{total_prods:,}", color=INDIGO)
    with col2:
        kpi_card("Product Categories", f"{cats}", color=AMBER)
    with col3:
        kpi_card("Avg Product Rating", f"{avg_prod_rating:.2f} / 5", color=EMERALD)
    with col4:
        kpi_card("Total Revenue (Items)", fmt_currency(total_revenue_oi), color=ROSE)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Revenue by Product Category")
        cat_rev = oi_prod.groupby("product_category")["net_sales"].sum().reset_index()
        cat_rev = cat_rev.sort_values("net_sales", ascending=True)
        fig_cat = px.bar(cat_rev, x="net_sales", y="product_category", orientation="h",
                         color="net_sales", color_continuous_scale="Purples",
                         labels={"net_sales": "Revenue ($)", "product_category": "Category"})
        fig_cat.update_layout(template=CHART_THEME, height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        section_header("Profit by Product Subcategory (Top 15)")
        sub_profit = (oi_prod.groupby("product_subcategory")["profit"]
                      .sum().reset_index().nlargest(15, "profit"))
        fig_sub = px.bar(sub_profit, x="profit", y="product_subcategory", orientation="h",
                         color="profit", color_continuous_scale="Greens",
                         labels={"profit": "Profit ($)", "product_subcategory": "Subcategory"})
        fig_sub.update_layout(template=CHART_THEME, height=380, coloraxis_showscale=False,
                               yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_sub, use_container_width=True)

    # Top 15 Products by Revenue
    section_header("Top 15 Products by Revenue")
    top_prod = (oi_prod.groupby(["product_id", "product_name"])["net_sales"]
                .sum().reset_index().nlargest(15, "net_sales"))
    top_prod["short_name"] = top_prod["product_name"].str[:40] + "…"
    fig_tp = px.bar(top_prod, x="net_sales", y="short_name", orientation="h",
                    color="net_sales", color_continuous_scale="Blues",
                    labels={"net_sales": "Revenue ($)", "short_name": "Product"})
    fig_tp.update_layout(template=CHART_THEME, height=450, coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_tp, use_container_width=True)

    col3a, col3b = st.columns(2)
    with col3a:
        section_header("Product Rating Distribution")
        fig_pr = px.histogram(products_df, x="product_rating", nbins=20,
                              color_discrete_sequence=[INDIGO],
                              labels={"product_rating": "Rating"})
        fig_pr.update_layout(template=CHART_THEME, height=320)
        st.plotly_chart(fig_pr, use_container_width=True)

    with col3b:
        section_header("Revenue Share by Brand (Top 10)")
        brand_rev = oi_prod.groupby("brand")["net_sales"].sum().reset_index().nlargest(10, "net_sales")
        fig_br = px.pie(brand_rev, names="brand", values="net_sales",
                        color_discrete_sequence=PALETTE, hole=0.4)
        fig_br.update_traces(textinfo="percent+label")
        fig_br.update_layout(template=CHART_THEME, height=320, showlegend=False)
        st.plotly_chart(fig_br, use_container_width=True)

    # Discount analysis
    section_header("Avg Discount % by Category")
    disc = oi_prod.groupby("product_category")["discount_percentage"].mean().reset_index()
    disc["discount_pct"] = disc["discount_percentage"] * 100
    fig_disc = px.bar(disc, x="product_category", y="discount_pct",
                      color="discount_pct", color_continuous_scale="Reds",
                      labels={"discount_pct": "Avg Discount (%)", "product_category": "Category"})
    fig_disc.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
    st.plotly_chart(fig_disc, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 5 – GEOGRAPHIC ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "🌍 Geographic Analysis":
    st.markdown("## 🌍 Geographic Analysis")

    col1, col2 = st.columns(2)
    with col1:
        section_header("Revenue by Region")
        reg_rev = df.groupby("region")["net_sales"].sum().reset_index()
        fig_reg = px.pie(reg_rev, names="region", values="net_sales",
                         color_discrete_sequence=PALETTE, hole=0.4)
        fig_reg.update_traces(textinfo="percent+label")
        fig_reg.update_layout(template=CHART_THEME, height=360, showlegend=False)
        st.plotly_chart(fig_reg, use_container_width=True)

    with col2:
        section_header("Orders by Region")
        reg_ord = df.groupby("region")["order_id"].nunique().reset_index()
        fig_ro = px.bar(reg_ord, x="region", y="order_id",
                        color="region", color_discrete_sequence=PALETTE,
                        labels={"order_id": "Orders", "region": "Region"})
        fig_ro.update_layout(template=CHART_THEME, height=360, showlegend=False)
        st.plotly_chart(fig_ro, use_container_width=True)

    # Top 15 countries
    section_header("Top 15 Countries by Revenue")
    country_rev = df.groupby("customer_country")["net_sales"].sum().reset_index().nlargest(15, "net_sales")
    fig_cn = px.bar(country_rev, x="net_sales", y="customer_country", orientation="h",
                    color="net_sales", color_continuous_scale="Blues",
                    labels={"net_sales": "Revenue ($)", "customer_country": "Country"})
    fig_cn.update_layout(template=CHART_THEME, height=460, coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cn, use_container_width=True)

    # Profit margin by region
    section_header("Avg Profit Margin by Region")
    pm_reg = df.groupby("region")["profit_margin_percentage"].mean().reset_index()
    fig_pm = px.bar(pm_reg, x="region", y="profit_margin_percentage",
                    color="profit_margin_percentage", color_continuous_scale="Greens",
                    labels={"profit_margin_percentage": "Avg Margin (%)", "region": "Region"})
    fig_pm.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
    st.plotly_chart(fig_pm, use_container_width=True)

    # Customer acquisition cost by region (from customer_master)
    merged_cm = customers_df.merge(
        df[["customer_id", "region"]].drop_duplicates(), on="customer_id", how="inner"
    )
    if not merged_cm.empty:
        section_header("Avg Customer Acquisition Cost by Region")
        acq = merged_cm.groupby("region_y" if "region_y" in merged_cm.columns else "region")[
            "customer_acquisition_cost"].mean().reset_index()
        acq.columns = ["Region", "Avg_CAC"]
        fig_acq = px.bar(acq, x="Region", y="Avg_CAC", color="Avg_CAC",
                         color_continuous_scale="Oranges",
                         labels={"Avg_CAC": "Avg CAC ($)"})
        fig_acq.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
        st.plotly_chart(fig_acq, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 6 – ORDER & DELIVERY
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "🚚 Order & Delivery":
    st.markdown("## 🚚 Order & Delivery Analytics")

    avg_delivery = df["delivery_days"].mean()
    on_time_rate = (df["delivery_status"] == "On Time").mean() * 100
    avg_shipping = df["shipping_cost"].mean()
    completed = (df["order_status"] == "Completed").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Avg Delivery Days", f"{avg_delivery:.1f} days", color=INDIGO)
    with c2:
        kpi_card("On-Time Rate", f"{on_time_rate:.1f}%", color=EMERALD)
    with c3:
        kpi_card("Avg Shipping Cost", fmt_currency(avg_shipping), color=AMBER)
    with c4:
        kpi_card("Completion Rate", f"{completed:.1f}%", color=ROSE)

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Delivery Status Breakdown")
        ds = df["delivery_status"].value_counts().reset_index()
        ds.columns = ["Status", "Count"]
        fig_ds = px.pie(ds, names="Status", values="Count",
                        color_discrete_sequence=PALETTE, hole=0.4)
        fig_ds.update_traces(textinfo="percent+label")
        fig_ds.update_layout(template=CHART_THEME, height=340, showlegend=False)
        st.plotly_chart(fig_ds, use_container_width=True)

    with col_r:
        section_header("Shipping Method Distribution")
        sm = df["shipping_method"].value_counts().reset_index()
        sm.columns = ["Method", "Count"]
        fig_sm = px.bar(sm, x="Method", y="Count", color="Method",
                        color_discrete_sequence=PALETTE)
        fig_sm.update_layout(template=CHART_THEME, height=340, showlegend=False)
        st.plotly_chart(fig_sm, use_container_width=True)

    # Delivery days distribution
    section_header("Distribution of Delivery Days")
    fig_dd = px.histogram(df[df["delivery_days"] > 0], x="delivery_days", nbins=25,
                          color_discrete_sequence=[INDIGO],
                          labels={"delivery_days": "Delivery Days"})
    fig_dd.update_layout(template=CHART_THEME, height=340)
    st.plotly_chart(fig_dd, use_container_width=True)

    # Shipping cost by method
    section_header("Avg Shipping Cost by Method")
    sc_meth = df.groupby("shipping_method")["shipping_cost"].mean().reset_index()
    fig_sc = px.bar(sc_meth, x="shipping_method", y="shipping_cost",
                    color="shipping_cost", color_continuous_scale="Blues",
                    labels={"shipping_cost": "Avg Cost ($)", "shipping_method": "Method"})
    fig_sc.update_layout(template=CHART_THEME, height=320, coloraxis_showscale=False)
    st.plotly_chart(fig_sc, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 7 – RETURNS & CANCELLATIONS
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "↩️ Returns & Cancellations":
    st.markdown("## ↩️ Returns & Cancellations")

    returned = df[df["return_status"].notna() & (df["return_status"] != "")]
    cancelled = df[df["order_status"] == "Cancelled"]
    return_rate = len(returned) / len(df) * 100
    cancel_rate = len(cancelled) / len(df) * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Returns", f"{len(returned):,}", color=ROSE)
    with c2:
        kpi_card("Return Rate", f"{return_rate:.2f}%", color=ROSE)
    with c3:
        kpi_card("Total Cancellations", f"{len(cancelled):,}", color=AMBER)
    with c4:
        kpi_card("Cancellation Rate", f"{cancel_rate:.2f}%", color=AMBER)

    st.markdown("<br>", unsafe_allow_html=True)

    if len(returned) > 0:
        col_l, col_r = st.columns(2)
        with col_l:
            section_header("Return Reasons")
            rr = returned["return_reason"].value_counts().reset_index()
            rr.columns = ["Reason", "Count"]
            fig_rr = px.bar(rr.head(10), x="Count", y="Reason", orientation="h",
                            color="Count", color_continuous_scale="Reds",
                            labels={"Reason": "Return Reason"})
            fig_rr.update_layout(template=CHART_THEME, height=380, coloraxis_showscale=False,
                                 yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_rr, use_container_width=True)

        with col_r:
            section_header("Return Status Distribution")
            rs = returned["return_status"].value_counts().reset_index()
            rs.columns = ["Status", "Count"]
            fig_rs = px.pie(rs, names="Status", values="Count",
                            color_discrete_sequence=[ROSE, AMBER, EMERALD], hole=0.4)
            fig_rs.update_traces(textinfo="percent+label")
            fig_rs.update_layout(template=CHART_THEME, height=380, showlegend=False)
            st.plotly_chart(fig_rs, use_container_width=True)

    # Returns by region
    section_header("Return Rate by Region")
    reg_ret = df.groupby("region").apply(
        lambda x: (x["return_status"].notna() & (x["return_status"] != "")).mean() * 100
    ).reset_index()
    reg_ret.columns = ["Region", "Return_Rate"]
    fig_regret = px.bar(reg_ret, x="Region", y="Return_Rate",
                        color="Return_Rate", color_continuous_scale="Reds",
                        labels={"Return_Rate": "Return Rate (%)"})
    fig_regret.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
    st.plotly_chart(fig_regret, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 8 – PAYMENT & MARKETING
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "💳 Payment & Marketing":
    st.markdown("## 💳 Payment & Marketing Analytics")

    col_l, col_r = st.columns(2)
    with col_l:
        section_header("Revenue by Payment Method")
        pm = df.groupby("payment_method")["net_sales"].sum().reset_index()
        fig_pm = px.pie(pm, names="payment_method", values="net_sales",
                        color_discrete_sequence=PALETTE, hole=0.4)
        fig_pm.update_traces(textinfo="percent+label")
        fig_pm.update_layout(template=CHART_THEME, height=360, showlegend=False)
        st.plotly_chart(fig_pm, use_container_width=True)

    with col_r:
        section_header("Payment Status Breakdown")
        ps = df["payment_status"].value_counts().reset_index()
        ps.columns = ["Status", "Count"]
        fig_ps = px.bar(ps, x="Status", y="Count", color="Status",
                        color_discrete_sequence=PALETTE)
        fig_ps.update_layout(template=CHART_THEME, height=360, showlegend=False)
        st.plotly_chart(fig_ps, use_container_width=True)

    # Marketing channel analysis
    section_header("Revenue by Marketing Channel")
    mc = df.groupby("marketing_channel")["net_sales"].sum().reset_index().sort_values("net_sales", ascending=False)
    fig_mc = px.bar(mc, x="marketing_channel", y="net_sales",
                    color="marketing_channel", color_discrete_sequence=PALETTE,
                    labels={"net_sales": "Revenue ($)", "marketing_channel": "Channel"})
    fig_mc.update_layout(template=CHART_THEME, height=360, showlegend=False)
    st.plotly_chart(fig_mc, use_container_width=True)

    # Avg rating by marketing channel
    section_header("Avg Customer Rating by Marketing Channel")
    mc_rating = df.groupby("marketing_channel")["customer_rating"].mean().reset_index()
    fig_mcr = px.bar(mc_rating, x="marketing_channel", y="customer_rating",
                     color="customer_rating", color_continuous_scale="Greens",
                     labels={"customer_rating": "Avg Rating", "marketing_channel": "Channel"})
    fig_mcr.update_layout(template=CHART_THEME, height=340, coloraxis_showscale=False)
    st.plotly_chart(fig_mcr, use_container_width=True)

    # Coupon usage
    section_header("Coupon Usage Impact on Revenue")
    df["coupon_used"] = df["coupon_code"].notna() & (df["coupon_code"].astype(str).str.strip() != "")
    coupon_grp = df.groupby("coupon_used").agg(
        Revenue=("net_sales", "sum"),
        Orders=("order_id", "nunique"),
        Avg_Discount=("discount_amount", "mean")
    ).reset_index()
    coupon_grp["coupon_used"] = coupon_grp["coupon_used"].map({True: "With Coupon", False: "Without Coupon"})
    fig_coup = px.bar(coupon_grp, x="coupon_used", y="Revenue",
                      color="coupon_used", text="Orders",
                      color_discrete_sequence=[INDIGO, AMBER])
    fig_coup.update_layout(template=CHART_THEME, height=340, showlegend=False)
    st.plotly_chart(fig_coup, use_container_width=True)

    # Review sentiment
    section_header("Review Sentiment Distribution")
    sent = df["review_sentiment"].value_counts().reset_index()
    sent.columns = ["Sentiment", "Count"]
    color_map = {"Positive": EMERALD, "Neutral": AMBER, "Negative": ROSE}
    fig_sent = px.bar(sent, x="Sentiment", y="Count", color="Sentiment",
                      color_discrete_map=color_map)
    fig_sent.update_layout(template=CHART_THEME, height=340, showlegend=False)
    st.plotly_chart(fig_sent, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 9 – DATA EXPLORER
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "🔍 Data Explorer":
    st.markdown("## 🔍 Data Explorer")
    st.caption("Interactively explore the raw filtered data and summary statistics.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Main Transactions",
        "👤 Customers",
        "🛍️ Order Items",
        "📦 Products",
        "📊 Statistics",
    ])

    with tab1:
        st.markdown(f"**{len(df):,} records** matching current filters")
        cols_show = st.multiselect(
            "Columns to display",
            df.columns.tolist(),
            default=["order_id", "order_date", "customer_name", "customer_segment",
                     "sales_channel", "net_sales", "profit", "order_status"],
        )
        if cols_show:
            st.dataframe(df[cols_show].head(500), use_container_width=True, hide_index=True)
        st.markdown("**Numeric Summary**")
        st.dataframe(df[cols_show].describe() if cols_show else df.describe(),
                     use_container_width=True)

    with tab2:
        st.dataframe(customers_df.head(500), use_container_width=True, hide_index=True)
        st.dataframe(customers_df.describe(), use_container_width=True)

    with tab3:
        st.dataframe(order_items_df.head(500), use_container_width=True, hide_index=True)
        st.dataframe(order_items_df.describe(), use_container_width=True)

    with tab4:
        st.dataframe(products_df.head(500), use_container_width=True, hide_index=True)
        st.dataframe(products_df.describe(), use_container_width=True)

    with tab5:
        st.dataframe(stats_df, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:12px;'>"
    "E-Commerce Sales & Customer Analytics Dashboard · Built with Python & Streamlit · "
    "Dataset: 138K+ Transactions (2021–2025)"
    "</p>",
    unsafe_allow_html=True,
)
