# HostelWise AI: REST API Reference

The HostelWise AI backend is built using **FastAPI** and provides a high-performance REST gateway for expense tracking, machine learning predictions, risk scoring, and Gemini AI queries.

---

## 🚀 Base URL
*   **Local Development**: `http://localhost:8000`
*   **Swagger UI (Interactive Docs)**: `http://localhost:8000/docs`
*   **ReDoc (Alternative Docs)**: `http://localhost:8000/redoc`

---

## 💸 Expense Management Endpoints

### 1. Upload Expense CSV
*   **Endpoint**: `POST /expenses/upload`
*   **Content-Type**: `multipart/form-data`
*   **Description**: Ingests a raw CSV transaction log, runs the cuDF ETL cleaning pipeline, archives the raw file in Google Cloud Storage, and loads the cleaned records into both SQLite and BigQuery.
*   **Request Form**:
    *   `file`: The CSV file containing transaction records.
    *   `student_id` (optional): Identifier of the student. Defaults to `default_student`.
*   **Response (200 OK)**:
    ```json
    {
      "message": "File processed and imported successfully.",
      "records_imported": 1540
    }
    ```

### 2. Add Single Expense
*   **Endpoint**: `POST /expenses/expense`
*   **Content-Type**: `application/json`
*   **Description**: Manually records a single student transaction.
*   **Query Parameters**:
    *   `student_id` (optional): Defaults to `default_student`.
*   **Request Body**:
    ```json
    {
      "amount": 250.0,
      "category": "Food",
      "subcategory": "Canteen",
      "description": "Weekly lunch bill",
      "payment_mode": "UPI",
      "date": "2026-06-30 13:00:00"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "message": "Expense recorded successfully.",
      "expense": {
        "expense_id": "4a5d8b24-7f1a-4c28-98e3-0d3a7e58b1a5",
        "student_id": "default_student",
        "date": "2026-06-30 13:00:00",
        "amount": 250.0,
        "category": "Food",
        "subcategory": "Canteen",
        "description": "Weekly lunch bill",
        "payment_mode": "UPI"
      }
    }
    ```

### 3. Set Monthly Budget
*   **Endpoint**: `POST /expenses/budget`
*   **Content-Type**: `application/json`
*   **Description**: Configures or updates the student's monthly budget limit for a specific category.
*   **Query Parameters**:
    *   `student_id` (optional): Defaults to `default_student`.
*   **Request Body**:
    ```json
    {
      "month_year": "2026-06",
      "category": "ALL",
      "allocated_amount": 12000.0
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "message": "Budget configured successfully."
    }
    ```

### 4. Get Dashboard Summary
*   **Endpoint**: `GET /expenses/dashboard`
*   **Description**: Aggregates all spending statistics, daily trends, payment distribution, forecast calculations, and risk scores in a single high-performance call.
*   **Query Parameters**:
    *   `student_id` (optional): Defaults to `default_student`.
    *   `month_year` (optional): Format `YYYY-MM`. Defaults to the current month.
*   **Response (200 OK)**:
    ```json
    {
      "kpis": {
        "total_expense": 4350.0,
        "avg_daily_spend": 145.0,
        "highest_category": "Food",
        "highest_category_amount": 1800.0,
        "budget_utilization_pct": 36.25
      },
      "category_spending": [{"category": "Food", "amount": 1800.0}],
      "weekly_spending": [{"week": "2026-06-29", "amount": 4350.0}],
      "daily_spending": [{"day": "2026-06-30", "amount": 250.0}],
      "payment_distribution": [{"payment_mode": "UPI", "amount": 4100.0}],
      "risk": {
        "risk_score": 24,
        "risk_level": "LOW",
        "current_spend": 4350.0,
        "projected_spend": 8700.0,
        "budget_limit": 12000.0,
        "is_over_budget": false
      },
      "recommendations": [
        {
          "category": "General",
          "potential_savings": 600.0,
          "recommendation_text": "Saving a flat 5% of your allowance can build a safety net."
        }
      ]
    }
    ```

---

## 🔮 Predictive & AI Endpoints

### 1. Get Spending Forecast
*   **Endpoint**: `POST /forecasts/forecast`
*   **Description**: Fits a Ridge Regression model on historical cyclical features and predicts the total spending for the next 30 days.
*   **Query Parameters**:
    *   `student_id` (optional): Defaults to `default_student`.
*   **Response (200 OK)**:
    ```json
    {
      "predicted_spend": 8240.50,
      "lower_bound": 7450.20,
      "upper_bound": 9030.80,
      "model_type": "Ridge Regression Time-Series"
    }
    ```

### 2. Chat with Gemini AI Advisor
*   **Endpoint**: `POST /chat/chat`
*   **Content-Type**: `application/json`
*   **Description**: Submits a query to the Gemini 1.5 Flash model. Automatically builds a RAG context block containing the student's current spending KPIs, category allocations, risk score, and ML forecasts.
*   **Query Parameters**:
    *   `student_id` (optional): Defaults to `default_student`.
*   **Request Body**:
    ```json
    {
      "query": "Can I afford a ₹1500 purchase this month?",
      "history": [
        {"role": "user", "content": "Hi, who are you?"},
        {"role": "assistant", "content": "Hello! I am your HostelWise AI assistant."}
      ],
      "budget_limit": 12000.0
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "response": "Based on your current data, you have spent ₹4,350 of your ₹12,000 budget. Your projected month-end spend is ₹8,700, leaving you with ₹3,300 of headroom. Therefore, you can afford this ₹1,500 purchase. However, it will increase your projected spend to ₹10,200, raising your budget risk score from 24 to 45. I recommend postponing it if it's not urgent."
    }
    ```

---

## ⚡ Benchmarking Endpoints

### 1. Run Performance Benchmark
*   **Endpoint**: `GET /benchmark/benchmark`
*   **Description**: Triggers the CPU (Pandas) vs. GPU (NVIDIA RAPIDS cuDF) benchmark comparison suite across 100K, 500K, and 1M row scales.
*   **Response (200 OK)**:
    ```json
    {
      "gpu_detected": false,
      "gpu_device_name": "No NVIDIA GPU / cuDF Detected (Running in Simulation Mode)",
      "timestamp": "2026-06-30 10:12:00",
      "benchmarks": [
        {
          "data_volume_rows": 100000,
          "cleaned_rows": 99820,
          "cpu_time_seconds": 0.3521,
          "gpu_time_seconds": 0.0239,
          "speedup": 14.72
        }
      ],
      "average_speedup": 24.35,
      "total_cpu_time_seconds": 5.2716,
      "total_gpu_time_seconds": 0.1864,
      "total_time_saved_seconds": 5.0852
    }
    ```
