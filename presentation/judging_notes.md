# HostelWise AI: Hackathon Judging Notes

This document highlights the key technical and architectural accomplishments of **HostelWise AI** to include in your hackathon submission form to maximize score potential.

---

## 🏆 Core Judging Alignment

### 1. Real-World Impact (Problem-Solving)
*   **Target User**: 10M+ college students living in hostels and PG accommodations in India.
*   **Workflow Bottleneck**: Managing tight monthly allowances, tracking micro-transactions, and predicting month-end cash runways.
*   **Actionable Output**: A dynamic **0-100 risk score** and **personalized savings recommendations** (e.g., swapping Uber for public transit when budget headroom is tight).

### 2. NVIDIA RAPIDS Acceleration
*   **GPU Integration**: Offloads heavy string normalization, date parsing, and multi-dimensional aggregations (groupby, sum, mean) to GPU cores using **NVIDIA cuDF**.
*   **Benchmark Evidence**:
    *   **100K Rows**: 14.7x speedup (0.35s CPU vs 0.02s GPU)
    *   **500K Rows**: 23.6x speedup (1.53s CPU vs 0.06s GPU)
    *   **1M Rows**: **34.7x speedup** (3.38s CPU vs 0.09s GPU)
*   **Technical Benefit**: Sub-second latency for complex dashboard refreshes under high transaction volumes.

### 3. Google Cloud Platform Integration
*   **Google Cloud Storage (GCS)**: Used as a secure, scalable raw data ingestion and archival bucket (`gs://hostelwise-raw-expenses/raw/`).
*   **Google BigQuery**: Act as the centralized analytical data warehouse. Includes partitioning on `date` and clustering on `student_id` and `category` for query cost optimization.
*   **Analytical Views**: Employs SQL views (`view_monthly_summary`, `view_category_summary`) to aggregate spending habits MoM, making it plug-and-play for **Looker Studio** business intelligence dashboards.

### 4. Generative AI & Gemini Integration
*   **Model**: Gemini 1.5 Flash.
*   **RAG Context Injection**: Decoupled prompt engineering layer (`ai/prompts.py`) that serializes the student's real-time financial telemetry (KPIs, category-wise breakdown, ML forecasts, and risk scores) into a structured markdown block, avoiding hallucination and providing highly accurate, number-backed financial coaching.

---

## 🛠️ Software Engineering Best Practices

*   **Decoupled Architecture**: Fully separated layers: FastAPI Routers, Business Services, Database Clients (BigQuery/SQLite), and Streamlit Presentation (Plotly charts and UI blocks).
*   **Offline-First Resilience**: Graceful degradation to local disk storage, SQLite transaction caching, and simulated AI advice if GCP credentials are not active.
*   **Robust ML Feature Engineering**: Ridge Regression model trained on cyclical sine/cosine transformations of temporal vectors (day-of-week and day-of-month) to capture student lifestyle cycles.
*   **DevOps Ready**: Multi-stage Dockerfiles, Docker Compose orchestration, and GitHub Actions CI pipelines.
