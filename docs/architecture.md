# HostelWise AI: System Architecture & Data Flows

This document details the architectural components and data flows of **HostelWise AI**.

---

## 🏗️ 1. High-Level System Architecture

HostelWise AI is designed as a decoupled, multi-tier application. It consists of:
1.  **Presentation Layer**: Streamlit dashboard rendering interactive Plotly charts and managing user inputs.
2.  **API Gateway**: FastAPI REST endpoints orchestrating business operations.
3.  **Service Layer**: Business services managing expense transactions, ML forecasting, multi-factor risk calculations, and AI prompt engineering.
4.  **Storage Layer**: A hybrid model utilizing local **SQLite** (for offline-first capability) and **Google BigQuery / GCS** (for cloud warehousing and file archives).
5.  **Acceleration Layer**: **NVIDIA RAPIDS cuDF** running parallelized ETL and analytical aggregations on GPU cores.

---

## 🔄 2. Core Operational Flows

### A. Data & Ingestion Flow (ETL)
```
[ Raw CSV Upload / Manual Entry ]
               |
               v
[ Save Raw File to GCS (gs://bucket/raw/) ]
               |
               v
[ Ingest into NVIDIA RAPIDS cuDF Pipeline ]
   - Handle missing subcategories/descriptions
   - Remove duplicate rows
   - Parse & standardize ISO-8601 timestamps
   - Normalize categories (map invalid to 'Other')
   - Filter negative/zero amounts
               |
               +-----------------------+
               |                       |
               v                       v
[ Save to Local SQLite ]    [ Load to Google BigQuery ]
```

### B. Cloud Flow (GCP Warehousing)
1.  **Blob Archival**: Raw CSV files are streamed directly from memory to **Google Cloud Storage** as blobs.
2.  **Streaming Ingest**: Manual transactions are streamed into the BigQuery `expenses` table via JSON inserts.
3.  **Batch Ingest**: Cleaned CSV dataframes are loaded into BigQuery using `load_table_from_dataframe`.
4.  **Analytical Views**: BigQuery views (`view_monthly_summary` and `view_category_summary`) aggregate the data at scale, which can be connected to **Looker Studio** for business intelligence dashboards.

### C. AI / RAG Flow (Gemini Advisor)
```
[ User Question ]
       |
       v
[ Fetch Financial Data from Database ]
   - Get current month's KPIs (total spent, daily avg)
   - Get category-wise spending list
   - Get next-month ML spending forecast
   - Get multi-factor budget risk score
   - Get active savings recommendations
       |
       v
[ Prompt Builder (ai/prompts.py) ]
   - Assemble Markdown context block containing telemetry
   - Prepend system instructions
       |
       v
[ Gemini 1.5 Flash API Call ]
       |
       v
[ Structured, Data-backed response returned to Student ]
```

### D. Benchmark Flow (NVIDIA cuDF vs. CPU Pandas)
```
[ Generate Synthetic Datasets (100K, 500K, 1M rows) ]
       |
       +-----------------------+
       |                       |
       v                       v
[ CPU Pandas Pipeline ]     [ GPU cuDF Pipeline ]
   - Read CSV (pandas)         - Read CSV (cudf)
   - Clean data                - Clean data (GPU)
   - Run aggregations          - Run aggregations (GPU)
       |                       |
       +-----------+-----------+
                   |
                   v
[ Compare Exec Times & Calculate Speedup ]
                   |
                   v
[ Save benchmark_report.csv & performance_summary.json ]
                   |
                   v
[ Generate benchmark_chart.png via Matplotlib ]
```
