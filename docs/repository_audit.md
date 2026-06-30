# HostelWise AI: Repository Audit Report

This report presents a formal audit of the **HostelWise AI** repository. It evaluates the project's codebase against software engineering best practices, security standards, and the judging criteria for the Google Cloud + NVIDIA Data Analytics Challenge.

---

## 1. Architectural Review
*   **Decoupling Status**: Core business logic has been successfully separated into `backend/services/` (expenses, forecasting, risk scoring, and recommendations). The API endpoints in `backend/api/routes/` serve solely as a routing gateway, which is a major architectural improvement.
*   **Data Tier**: The database layer is decoupled. `backend/database/models.py` manages local SQLite operations, while `backend/database/bigquery_client.py` wraps BigQuery analytical views. This ensures that the application can run in offline fallback mode without crashing.
*   **AI Integration**: Prompt engineering is isolated in `ai/prompts.py` and session state is managed in `ai/chatbot.py`. This prevents LLM prompt leaks from polluting the business logic.

---

## 2. Code Duplication & Clutter
*   **Monolithic Leftovers**: Several old monolithic files were identified in the root and old directories (e.g. `backend/config.py`, `backend/models.py`, `backend/services/db_service.py`, `forecasting/model.py`, and `benchmark/runner.py`). These have been deleted to prevent duplicate code execution and import confusion.
*   **Visualization Separation**: Plotly chart configurations have been successfully moved from the Streamlit frontend `app.py` into `frontend/charts/plotly_charts.py`. This ensures that visual layouts and data representations are decoupled.

---

## 3. Frontend Multiplicity Review
*   **Audit**: We scanned the repository and verified that only the **Streamlit** frontend exists inside `/frontend/`. No React, Angular, or Vue directories are present.
*   **Status**: Streamlit is designated as the primary production frontend. It is lightweight, python-native, and integrates seamlessly with our data science and machine learning libraries.

---

## 4. Cloud Ingestion & Security
*   **Credential Handling**: The application uses `google.cloud.storage.Client` and `google.cloud.bigquery.Client` which automatically load credentials from the standard `GOOGLE_APPLICATION_CREDENTIALS` environment variable. No hardcoded service account keys exist in the source code.
*   **Local Fallback**: The cloud managers degrade gracefully. If `GCP_PROJECT` is not configured, the app automatically switches to **Local SQLite mode**, ensuring zero-friction setup for new developers.

---

## 5. Testing & Verification
*   **Unit Tests**: The `tests/` directory contains unit tests for data cleaning (`test_cleaning.py`), forecasting (`test_forecasting.py`), and risk scoring (`test_recommendations.py`).
*   **CI/CD**: The repository currently lacks a continuous integration pipeline. We will add a GitHub Actions workflow to run syntax checks and unit tests automatically on commit.

---

## 6. Audit Summary & Action Items

| Category | Finding | Priority | Action Item |
| :--- | :--- | :--- | :--- |
| **Cleanup** | Compiled cache files (`__pycache__/`, `*.pyc`) and OS metadata (`.DS_Store`) lack a `.gitignore` shield. | High | Create a comprehensive `.gitignore` and run a cleanup command. |
| **SQL** | SQL files are not named according to the hackathon specification. | Medium | Rename `create_tables.sql` to `bigquery_schema.sql` and add `forecasting_queries.sql`. |
| **Automation** | Benchmarks do not save a static comparison chart. | Medium | Update `benchmark/compare.py` to auto-generate `benchmark_chart.png`. |
| **DevOps** | No automated CI/CD pipeline exists. | Medium | Create `.github/workflows/test.yml` for GitHub Actions. |
| **Documentation** | Several deployment and API markdown guides are missing. | Low | Create `api.md`, `deployment.md`, and `setup.md` in `docs/`. |
