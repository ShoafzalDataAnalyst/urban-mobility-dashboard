# 📊 Maven Market Sales Analysis — Power BI Dashboard

> A comprehensive business intelligence dashboard analyzing sales performance, customer behavior, and product profitability for Maven Market — a multi-national grocery chain operating across the USA, Canada, and Mexico (1997–1998).

---

## 📸 Dashboard Preview

![Dashboard Overview](screenshot.png)

---

## 🔖 Interactive Bookmarks

This dashboard includes 3 bookmark views navigated via the button panel:

### 📊 Overview (Default)
Full dashboard showing all 20 product brands, all countries, unfiltered data.

### 🚨 Quality Alert
![Quality Alert View](quality_alert.png)
*Filters to brands with return rates above 0.9% — highlights products requiring supplier review.*

### ⭐ Top 5 Performers
![Top 5 Performers View](top5_performers.png)
*Filters to the 5 highest-profit brands — combined $150K+ profit, 30% of total.*

---

## 📋 Project Overview

| Detail | Info |
|---|---|
| Tool | Microsoft Power BI Desktop |
| Dataset | Maven Market (1997–1998) |
| Records | 269,720 transactions |
| Countries | USA, Canada, Mexico |
| Stores | 24 locations |
| Products | 1,560 items across 20 brands |

---

## 🔍 Key Findings

- **Total Revenue:** $1,764,546 across 2 years
- **Total Transactions:** 269,720
- **Top Performing Brand:** Hermanos ($33,167 profit, 58.54% margin)
- **Quality Concern:** Horatio (1.09% return rate — highest above 0.9% threshold)
- **Revenue Target:** 5% growth target set above current revenue ($1.85M target)
- **USA Dominance:** $1,177.96K revenue (67% of total)

---

## 🗄️ Data Model

Star schema with 2 fact tables and 5 dimension tables.

![Data Model](model_view.png)

| Table | Type | Records | Description |
|---|---|---|---|
| Transactions | Fact | 269,720 | All sales transactions |
| Returns_1997-1998 | Fact | ~5,000 | Product return records |
| Customers | Dimension | 10,000 | Customer demographics |
| Products | Dimension | 1,560 | Product catalog & pricing |
| Stores | Dimension | 24 | Store locations |
| Regions | Dimension | 5 | Geographic regions |
| Calendar | Dimension | 730 days | Date table (1997–1998) |

**Relationships:**
```
Calendar ──────────────────────────┐
                                   ▼
Customers ──────────────────── Transactions ◄──── Returns_1997-1998
                                   ▲
Products ──────────────────────────┤
                                   ▼
Stores ──────────────────────── Regions
```

---

## 📐 DAX Measures (24 Total)

### Core Metrics
| Measure | Formula Logic |
|---|---|
| Total Revenue | SUMX of quantity × retail price |
| Total Cost | SUMX of quantity × product cost |
| Total Profit | Revenue minus cost per transaction |
| Profit Margin | Profit as % of revenue |
| Total Transactions | COUNT of all transactions |
| Quantity Sold | SUM of all units sold |

### Time Intelligence
| Measure | Description |
|---|---|
| Current Month Transactions | MTD transaction count |
| Current Month Profit | MTD profit |
| Current Month Returns | MTD returns |
| Last Month Transactions | Prior month comparison |
| Last Month Revenue | Prior month comparison |
| Last Month Profit | Prior month comparison |
| Last Month Returns | Prior month comparison |
| YTD Revenue | Year-to-date revenue |
| 60-Day Revenue | Rolling 60-day window |

### Returns & Performance
| Measure | Description |
|---|---|
| Total Returns | COUNT of return transactions |
| Quantity Returned | SUM of returned units |
| Return Rate | Returns divided by quantity sold |
| All Returns | Returns ignoring filters |
| All Transactions | Transactions ignoring filters |

### Analysis
| Measure | Description |
|---|---|
| Weekend Transactions | Transactions on weekends only |
| % Weekend Transactions | Weekend share of total |
| Unique Products | Distinct product count |
| Revenue Target | Total revenue × 1.05 |

📄 See `docs/dax_formulas.docx` for full formula code.

---

## 🎛️ Dashboard Features

- **Interactive Bookmarks** — 3 views: Overview, Quality Alert, Top 5 Performers
- **KPI Cards** — Revenue, Transactions, Profit with month-over-month goal comparison
- **Matrix Table** — Top 20 product brands with conditional formatting
- **Treemap** — Revenue distribution by country (USA / Mexico / Canada)
- **Revenue Gauge** — Current revenue vs 5% growth target
- **Monthly Trend Chart** — Revenue trend across 1998
- **Country Slicers** — Filter entire dashboard by country

---

## 📁 Repository Structure

```
maven-market-powerbi/
├── Maven Market Report.pbix     ← Power BI project file
├── README.md                    ← This file
├── screenshot.png               ← Overview dashboard
├── quality_alert.png            ← Quality Alert bookmark view
├── top5_performers.png          ← Top 5 Performers bookmark view
├── model_view.png               ← Data model screenshot
├── docs/
│   ├── data_dictionary.docx     ← Column definitions for all tables
│   └── dax_formulas.docx        ← All 24 DAX measure formulas
└── data/
    ├── Transactions/            ← Folder (1997 + 1998 transaction files)
    ├── MavenMarket_Calendar.csv
    ├── MavenMarket_Customers.csv
    ├── MavenMarket_Products.csv
    ├── MavenMarket_Regions.csv
    ├── MavenMarket_Returns_1997-1998.csv
    └── MavenMarket_Stores.csv
```

---

## 🚀 How to Use

### Prerequisites
- Microsoft Power BI Desktop (free download at powerbi.microsoft.com)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/ShoafzalDataAnalyst/maven-market-powerbi.git
cd maven-market-powerbi
```

2. **Open the report**
   - Open `Maven Market Report.pbix` in Power BI Desktop

3. **Fix data source paths** (if prompted)
   - Go to **Home → Transform data**
   - For each table with a ⚠️ warning, click **Source** in Applied Steps
   - Update the path to point to the `/data` folder in this repo
   - For the Transactions table, point to the `/data/Transactions` **folder** (not individual files)
   - Click **Close & Apply**

4. **Explore the dashboard**
   - Use the **Overview / Quality Alert / Top 5 Performers** buttons to switch views
   - Use the **country slicer** (Select all / Canada / Mexico / USA) to filter by region

---

## 🛠️ Tools & Skills Demonstrated

- **Microsoft Power BI Desktop** — Data modeling, visualization, DAX
- **Power Query (M)** — Data transformation and cleaning
- **DAX** — 24 custom measures including time intelligence
- **Star Schema** — Relational data modeling
- **Business Intelligence** — KPIs, benchmarks, trend analysis
- **Data Visualization** — Treemaps, gauge charts, KPI cards, matrix tables

---

## 📧 Contact

**Shoafzal Shomuhidov**
- GitHub: [@ShoafzalDataAnalyst](https://github.com/ShoafzalDataAnalyst)
- LinkedIn: [shoafzal-shomuhidov](https://www.linkedin.com/in/shoafzal-shomuhidov-15b647389/)
- Email: shomuhidov.shoafzal@gmail.com

---

*Dataset provided by Maven Analytics. Project completed as part of a data analytics portfolio.*