# 🛒 E-Commerce Sales & Customer Analytics Dashboard

> An interactive, multi-page business intelligence dashboard built entirely in Python using **Streamlit** and **Plotly** — analysing 138,000+ e-commerce transactions across 5 years, 24,911 customers, and multiple countries.

---

## 📋 Project Description

This project transforms raw e-commerce data into actionable business intelligence through a fully interactive dashboard. It covers nine analytical domains:

- **Executive Summary** — KPI tiles, annual revenue/profit, sales channel mix
- **Sales Trends** — Monthly/quarterly trends, MoM growth, segment trends
- **Customer Analytics** — Segmentation, CLV, demographics, loyalty points
- **Product Analytics** — Category revenue, top products, brand share, discount analysis
- **Geographic Analysis** — Revenue by region/country, acquisition cost by region
- **Order & Delivery** — On-time rate, shipping methods, delivery distribution
- **Returns & Cancellations** — Return reasons, rates by region, status breakdown
- **Payment & Marketing** — Payment methods, marketing channels, coupon impact, sentiment
- **Data Explorer** — Interactive tabbed raw data explorer with column selector

All pages are connected to **global sidebar filters** for Year, Region, Customer Segment, and Sales Channel — making every chart reactive and filterable in real time.

---

## 📁 Dataset

| File | Description | Records |
|------|-------------|---------|
| `ecommerce_sales_customer_analytics_150k.csv` | Main transactions (2021–2025) | 138,116 rows, 46 columns |
| `customer_master.csv` | Customer profiles | 24,911 customers |
| `order_items.csv` | Line-level order items | 138,116 rows |
| `product_catalog.csv` | Product metadata | All products |
| `dataset_statistics.csv` | Pre-computed summary stats | 1 row summary |

**Dataset Source:** [Kaggle — E-Commerce Sales & Customer Analytics 150K](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data)

**Key Stats:**
- 🗓️ Date Range: 2021-01-01 to 2025-12-31
- 💰 Total Revenue: $177,134,263.74
- 📈 Total Profit: $76,146,395.76
- 🛒 Avg Order Value: $1,282.50
- ⭐ Avg Rating: 3.68 / 5
- ↩️ Return Rate: 6.85%
- ❌ Cancellation Rate: 6.08%

---

## 🛠️ Technologies Used

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Streamlit | 1.35.0 | Web UI, layout, widgets, reactivity |
| **Visualisation** | Plotly | 5.22.0 | Interactive charts (bar, line, pie, histogram, dual-axis) |
| **Backend** | Python | 3.10+ | Core language |
| **Data Processing** | pandas | 2.2.2 | Data loading, merging, grouping, time-series |
| **Numerics** | numpy | 1.26.4 | Array operations |
| **Statistics** | scipy | 1.13.1 | Statistical functions |
| **Office Export** | openpyxl | 3.1.2 | Excel support |
| **Document** | python-docx | 1.1.2 | Word document support |

---

## ⚙️ Setup & Run Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Step 1 — Get the project files
Download or clone this project folder. Ensure all CSV files are in the **same directory** as `app.py`.

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the dashboard
```bash
streamlit run app.py
```

### Step 4 — Open in browser
The dashboard will automatically open at:
```
http://localhost:8501
```

---

## 📂 File Structure

```
project/
│
├── app.py                                        # Main Python application (backend + frontend)
├── requirements.txt                              # Python dependencies
├── README.md                                     # This file
├── HimanshuMandal_ProjectReport.docx             # Full project report
│
├── ecommerce_sales_customer_analytics_150k.csv   # Primary transaction dataset
├── customer_master.csv                           # Customer profile data
├── order_items.csv                               # Line-level order item data
├── product_catalog.csv                           # Product metadata
└── dataset_statistics.csv                        # Pre-computed summary statistics
```

---

## 📊 Dashboard Pages

| Page | Key Charts | Insights |
|------|-----------|----------|
| 📊 Executive Summary | 8 KPI cards, annual bar+line, channel pie | Top-line business health |
| 📈 Sales Trends | Monthly area chart, quarterly bar, MoM growth | Seasonality, growth momentum |
| 👥 Customer Analytics | Segment pie, age histogram, CLV bar, loyalty grouped bar | Who your customers are |
| 📦 Product Analytics | Category revenue, top 15 products, brand pie, discount bar | What sells best |
| 🌍 Geographic Analysis | Region pie, country bar, margin bar, CAC bar | Where revenue comes from |
| 🚚 Order & Delivery | Delivery status pie, shipping method bar, histogram | Fulfilment performance |
| ↩️ Returns & Cancellations | Return reasons bar, region return rate | Revenue leakage analysis |
| 💳 Payment & Marketing | Payment pie, channel bar, coupon impact, sentiment | Marketing ROI |
| 🔍 Data Explorer | 5-tab raw data tables with column selector | Ad-hoc investigation |

---

## 🔑 Key Information

- **No database required** — all data is loaded directly from CSV files at startup.
- **Caching** — `@st.cache_data` ensures CSV files are parsed only once per session, keeping the UI fast even with 138K rows.
- **Global Filters** — Year, Region, Segment, and Channel filters apply across all 9 pages simultaneously.
- **Zero external APIs** — fully offline, no internet connection required after install.
- **Single file** — the entire application lives in `app.py` for simple deployment and sharing.

---

## 👤 Author

**Himanshu Mandal**  
Project: E-Commerce Sales & Customer Analytics Dashboard  
Built with: Python · Streamlit · Plotly · pandas · numpy

---

*Dashboard built for academic/analytical purposes using a synthetic e-commerce dataset.*
