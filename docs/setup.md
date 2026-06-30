# HostelWise AI: Installation & Setup Guide

This guide provides step-by-step instructions for configuring Google Cloud, setting up a local development environment, installing NVIDIA RAPIDS, and running the application using Docker.

---

## 1. Google Cloud Configuration (Optional)

HostelWise AI operates in **Local Fallback Mode** by default, using local disk storage and an SQLite database. To enable the cloud-native pipeline, configure the following:

### A. GCS Bucket and BigQuery Dataset
1.  Open the [Google Cloud Console](https://console.cloud.google.com).
2.  Create a GCS Bucket (e.g. `hostelwise-raw-expenses`).
3.  Go to BigQuery and create a dataset named `hostelwise_ai_dataset`.
4.  Run the DDL script located in [create_tables.sql](../sql/create_tables.sql) to set up the tables.

### B. Service Account Credentials
1.  Go to **IAM & Admin > Service Accounts** in GCP.
2.  Create a service account with the following roles:
    *   `Storage Object Admin` (for GCS uploads)
    *   `BigQuery Data Editor` (for inserting records)
    *   `BigQuery Job User` (for running queries)
3.  Generate a JSON key and save it locally.
4.  Set the environment variable in your terminal:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    ```

---

## 2. Local Python Environment Setup

1.  **Clone the Repository and Navigate**:
    ```bash
    cd hostelwise-ai
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Core Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create `.env` File**:
    Create a `.env` file in the root directory:
    ```env
    GEMINI_API_KEY=your_gemini_api_key
    GCP_PROJECT=your_gcp_project_id
    GCS_BUCKET_NAME=hostelwise-raw-expenses
    BIGQUERY_DATASET=hostelwise_ai_dataset
    ```

---

## 3. NVIDIA RAPIDS cuDF Installation

To run the GPU-accelerated pipeline, install NVIDIA RAPIDS `cuDF` in your environment.

*   **Via Conda (Recommended)**:
    ```bash
    conda create -n rapids-24.04 -c rapidsai -c conda-forge -c nvidia \
        cudf=24.04 python=3.10 cuda-version=12.0
    ```
*   **Via Pip (Extra Index)**:
    ```bash
    pip install --extra-index-url=https://pypi.nvidia.com cudf-cu12==24.4.*
    ```

---

## 4. Running the Application

### Option A: Local Run
1.  **Start FastAPI Backend**:
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```
2.  **Start Streamlit Dashboard**:
    ```bash
    streamlit run frontend/app.py --server.port 8501
    ```

### Option B: Docker Compose Run (Orchestration)
To build and start both the backend and frontend services in isolated containers:
```bash
docker-compose up --build
```
*   Streamlit Dashboard will be accessible at: `http://localhost:8501`
*   FastAPI docs will be accessible at: `http://localhost:8000/docs`
