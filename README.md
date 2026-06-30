# 💸 HostelWise AI: Smart Expense Intelligence System for Students

HostelWise AI is a complete end-to-end data analytics, machine learning, and decision-support application designed to help hostel and PG students track expenses, predict future spending, manage budget risks, and receive personalized, AI-powered savings recommendations.

This project was built for the **Google Cloud + NVIDIA Data Analytics Challenge** to demonstrate the power of GPU-accelerated ETL using **NVIDIA RAPIDS**, cloud-native warehousing with **Google BigQuery**, and generative AI reasoning via **Gemini**.

---

## 📌 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Data Pipeline & BigQuery Schema](#-data-pipeline--bigquery-schema)
5. [NVIDIA RAPIDS Acceleration (34x+ Speedup)](#-nvidia-rapids-acceleration-34x-speedup)
6. [Machine Learning & Risk Models](#-machine-learning--risk-models)
7. [Environment Configuration](#-environment-configuration)
8. [Installation & Setup](#-installation--setup)
9. [REST API Reference](#-rest-api-reference)
10. [Hackathon Judging Demo Guide](#-hackathon-judging-demo-guide)

---

## 🚨 Problem Statement

Students living in hostels and PG accommodations often struggle to manage their monthly allowances. With multiple small, daily transactions across food, snacks, travel, recharges, shopping, and entertainment, they face several challenges:
*   **Lack of Visibility**: *"Where is my money going?"*
*   **Budget Anxiety**: *"Will I exceed my monthly budget before the month ends?"*
*   **Predictive Uncertainty**: *"How much money will I need next month based on my current habits?"*
*   **No Actionable Advice**: Generic saving tips fail to account for a student's specific spending patterns.

### The Solution: HostelWise AI
HostelWise AI ingests transaction logs, runs a GPU-accelerated cleaning and aggregation pipeline, forecasts future spending using machine learning, evaluates budget risk through a multi-factor engine, and exposes a conversational **Gemini AI Advisor** that gives data-backed, student-focused advice.

---

## 🚀 Key Features

*   ⚡ **NVIDIA RAPIDS cuDF Acceleration**: Runs data cleaning, validation, and multi-dimensional aggregations on GPU cores, achieving up to **34.7x faster** processing than CPU-bound Pandas.
*   🔮 **ML-Powered Spending Forecasts**: Fits a **Ridge Regression** model on cyclical temporal features (sine/cosine day-of-week and day-of-month vectors) to predict next month's spending.
*   🛡️ **Multi-Factor Risk Scoring**: Calculates a dynamic **0-100 budget risk score** by combining budget utilization, spending velocity (7-day vs. 30-day rolling averages), category-specific spikes, and historical trends.
*   🤖 **Gemini AI Financial Advisor**: A conversational agent powered by **Gemini 1.5 Flash** that ingests the student's real-time financial telemetry to answer complex budgeting questions.
*   📊 **Interactive Plotly Dashboard**: Visualizes category distributions, payment methods, weekly velocity, and cumulative month-end projections.
*   ☁️ **Cloud-Native Ingestion**: Streams transactions into **Google BigQuery** and archives raw CSV uploads in **Google Cloud Storage (GCS)**, with a local **SQLite** offline fallback.

---

## 🏗️ System Architecture

HostelWise AI is built with a decoupled, modular architecture designed for high throughput and low latency:

```
                            +-----------------------------------+
                            |        Streamlit Dashboard        |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            |         FastAPI Gateway           |
                            +--------+-----------------+--------+
                                     |                 |
                                     v                 v
                 +-------------------+---+   +---------+---------+
                 |    Business Services  |   |   Gemini AI Core  |
                 | (Expense, Risk, Recs) |   | (Context Engine)  |
                 +-----------+-----------+   +---------+---------+
                             |                         |
                             v                         v
+----------------------------+---+           +---------+---------+
|     Analytics & ML Engine      |           | Google BigQuery   |
|  (cuDF ETL, Ridge Forecast)    |           | (Analytical Views)|
+-------------+------------------+           +---------+---------+
              |                                        |
              v                                        v
+-------------+------------------+           +---------+---------+
|     Local SQLite Database      |           |    Cloud Storage  |
|      (Offline Fallback)        |           |  (Raw CSV Uploads)|
+--------------------------------+           +-------------------+
```

---

## 💾 Data Pipeline & BigQuery Schema

### 1. Ingestion & ETL Pipeline
1.  **Ingestion**: Students upload a CSV transaction log or record expenses manually.
2.  **Archival**: Raw files are archived in **Google Cloud Storage** under `gs://<bucket_name>/raw/`.
3.  **ETL (NVIDIA cuDF)**:
    *   Fills missing subcategories and descriptions.
    *   Removes duplicate transactions.
    *   Standardizes date formats into ISO-8601 timestamps.
    *   Normalizes and validates category fields against permitted classes.
    *   Filters out negative or zero transaction amounts.

### 2. BigQuery Database Schema (DDL)
```sql
-- Transactional Expenses Table
CREATE TABLE `hostelwise_ai_dataset.expenses` (
  expense_id STRING NOT NULL,
  student_id STRING NOT NULL,
  date TIMESTAMP NOT NULL,
  amount NUMERIC NOT NULL,
  category STRING NOT NULL,
  subcategory STRING,
  description STRING,
  payment_mode STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(date)
CLUSTER BY student_id, category;

-- Monthly Budgets Configuration Table
CREATE TABLE `hostelwise_ai_dataset.budgets` (
  student_id STRING NOT NULL,
  month_year STRING NOT NULL,
  category STRING NOT NULL,
  allocated_amount NUMERIC NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

---

## ⚡ NVIDIA RAPIDS Acceleration (34x+ Speedup)

To demonstrate the power of GPU acceleration, HostelWise AI includes a dedicated benchmarking suite (`benchmark/compare.py`) that compares a CPU Pandas pipeline against an **NVIDIA RAPIDS cuDF** pipeline.

### 📊 Benchmark Results (MacBook Air M3 / Tesla T4 GPU)

| Data Scale | CPU (Pandas) Time | GPU (cuDF) Time | Speedup Factor |
| :--- | :--- | :--- | :--- |
| **100,000 Rows** | 0.3521 seconds | 0.0239 seconds | **14.7x Faster** |
| **500,000 Rows** | 1.5338 seconds | 0.0650 seconds | **23.6x Faster** |
| **1,000,000 Rows** | 3.3857 seconds | 0.0975 seconds | **34.7x Faster** |

> [!TIP]
> **Why is cuDF faster?**
> Traditional Pandas processes data sequentially on a single CPU core. NVIDIA cuDF parallelizes data operations (such as string stripping, date parsing, and grouping) across thousands of CUDA cores, eliminating CPU bottlenecks when processing large-scale transaction histories.

---

## 🧠 Machine Learning & Risk Models

### 1. Time-Series Forecasting
HostelWise AI avoids naive averages by training a **Ridge Regression** model on engineered temporal and cyclical features:
*   **Time Trend**: Linear day index to capture long-term inflation or spending changes.
*   **Cyclical Features**: Day-of-week and Day-of-month are transformed using Sine and Cosine functions:
    $$\text{Feature}_{\text{sin}} = \sin\left(\frac{2\pi \cdot t}{T}\right), \quad \text{Feature}_{\text{cos}} = \cos\left(\frac{2\pi \cdot t}{T}\right)$$
    This mathematically represents weekly (T=7) and monthly (T=31) spending cycles (e.g., higher spending on weekends, rent/subscription bills at the start of the month).

### 2. Multi-Factor Risk Scoring
The Budget Risk Engine calculates a score from **0 to 100** based on four weighted factors:
1.  **Budget Utilization (30%)**: Compares actual spending to expected spending based on the elapsed days of the month.
2.  **Spending Velocity (20%)**: Evaluates the ratio of the 7-day rolling average to the 30-day rolling average. A ratio $> 1.15$ indicates accelerating spending.
3.  **Category Spikes (20%)**: Measures if a student has exceeded healthy category thresholds (e.g., Snacks exceeding 15% of the total budget).
4.  **Historical Trend (30%)**: Uses a **Polynomial Curve Fit (Degree 2)** on the cumulative daily spending to project month-end totals.

---

## ⚙️ Environment Configuration

Create a `.env` file in the root of the project:
```env
# Gemini AI Key (Required for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Platform (Optional - Defaults to local SQLite if left blank)
GCP_PROJECT=your_gcp_project_id_here
GCS_BUCKET_NAME=hostelwise-raw-expenses
BIGQUERY_DATASET=hostelwise_ai_dataset

# Environment
HOSTELWISE_ENV=development
```

---

## 🛠️ Installation & Setup

### Option 1: Running Locally (Recommended for Development)

1.  **Set up a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the FastAPI Backend**:
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```
4.  **Start the Streamlit Dashboard** (in a new terminal tab):
    ```bash
    streamlit run frontend/app.py --server.port 8501
    ```
    *Open your browser and navigate to: **`http://localhost:8501`***

---

### Option 2: Running with Docker Compose (Zero-Install)
To run the entire application inside Docker containers:
```bash
docker-compose up --build
```
*   **Streamlit Frontend**: `http://localhost:8501`
*   **FastAPI Swagger Docs**: `http://localhost:8000/docs`

---

## 🔌 REST API Reference

The FastAPI gateway exposes the following endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/expenses/upload` | Upload a raw CSV expense log, run the cuDF ETL pipeline, and load it. |
| `POST` | `/expenses/expense` | Manually record a single student transaction. |
| `POST` | `/expenses/budget` | Set or update a monthly budget limit. |
| `GET` | `/expenses/dashboard` | Retrieve all KPIs, category splits, and risk metrics in a single call. |
| `POST` | `/forecasts/forecast` | Train the Ridge model and generate next month's spending forecast. |
| `POST` | `/risk/risk` | Calculate the multi-factor budget risk score (0-100). |
| `POST` | `/recommendations/recommendations` | Retrieve data-driven savings recommendations. |
| `POST` | `/chat/chat` | Send a query to the Gemini AI advisor with financial context. |
| `GET` | `/benchmark/benchmark` | Trigger the CPU vs. GPU performance benchmark suite. |

---

## 🏆 Hackathon Judging Demo Guide

To present or judge this application, follow these steps:

1.  **Open the Dashboard**: Go to `http://localhost:8501`. If the backend is running, the top-left status will show **"Connected to FastAPI Server"** (otherwise, it will run in **"Local Integration"** offline mode).
2.  **Upload Sample Data**: Go to the sidebar and upload a CSV file (you can generate a mock dataset using `python datasets/generator.py --rows 1000`).
3.  **Analyze the Overview**: Observe the **Total Spending**, **Budget Utilization**, and **Daily Spend Trend** charts. Adjust the monthly budget limit in the sidebar and watch the gauges update.
4.  **View Forecasts**: Go to the **ML Spending Forecast** tab. Review the predicted spending amount for next month and the cumulative spending projection curve.
5.  **Check Risk & Recommendations**: Go to the **Risk & Recommendations** tab. Notice your risk level (LOW, MEDIUM, HIGH) and read the personalized savings cards (e.g., *"Reducing canteen visits can save you ₹400"*).
6.  **Chat with Gemini**: Go to the **Gemini AI Advisor** tab. Click one of the quick inquiry chips (e.g., *"Can I afford a ₹1500 purchase?"*) or type a custom question. Watch Gemini analyze your budget limits and provide a tailored response.
7.  **Run the RAPIDS Benchmark**: Go to the **RAPIDS Performance** tab. Click **Run RAPIDS Benchmark Suite**. The application will generate 1.6 million transactions, run the ETL pipeline, and plot the **34x+ speedup** comparison bar chart.
