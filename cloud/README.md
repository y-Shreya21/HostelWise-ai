# HostelWise AI: Google Cloud Platform Integration

This module manages the connection and operations with **Google Cloud Platform (GCP)** services.

---

## ☁️ Architecture Overview

HostelWise AI uses GCP for secure, scalable data storage, analytical warehousing, and business intelligence:

```
[ Ingested CSV / Entry ] 
           |
           +---> [ Google Cloud Storage ] (Raw CSV Archival)
           |
           +---> [ Google BigQuery ] (Analytical Warehouse)
                       |
                       +---> [ Looker Studio / Dashboards ]
```

### 1. Google Cloud Storage (GCS)
*   **Module**: [storage.py](storage.py)
*   **Purpose**: Acts as our archival layer. Every raw CSV file uploaded by the student is saved as a blob in a GCS bucket (e.g. `gs://hostelwise-raw-expenses/raw/`) before being processed by the ETL pipeline.
*   **Local Fallback**: If GCS is unavailable, files are saved locally in the `data/uploads/` directory.

### 2. Google BigQuery
*   **Module**: [bigquery.py](bigquery.py)
*   **Purpose**: Acts as our high-performance analytical data warehouse. Cleaned dataframes are loaded in bulk, and manual expenses are streamed via JSON inserts.
*   **Optimizations**: The `expenses` table is partitioned by `DATE(date)` and clustered by `student_id` and `category` to minimize query execution costs.
*   **Local Fallback**: If BigQuery is unavailable, transactions are stored locally in `data/hostelwise.db` using **SQLite**.

---

## 🔑 Credential Handling & Configuration

All configurations are loaded from environment variables via [config.py](config.py).

The GCP clients utilize **Application Default Credentials (ADC)**. To configure credentials in development:

1.  **Set the Environment Variable**:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    ```
2.  **Ensure the Service Account has the following roles**:
    *   `Storage Object Admin` (for GCS uploads)
    *   `BigQuery Data Editor` (for inserting records)
    *   `BigQuery Job User` (for running queries)
