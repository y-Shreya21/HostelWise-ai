# HostelWise AI: Test Suite & Coverage

This document outlines the testing architecture and execution instructions for **HostelWise AI**.

---

## 🧪 Testing Architecture

HostelWise AI features a robust automated test suite located in the `tests/` directory. The tests cover the core analytics, machine learning, and decision-support services:

```
tests/
├── test_cleaning.py          # ETL Data Cleaning & Validation
├── test_forecasting.py       # ML Model Training & Inference
└── test_recommendations.py   # Risk Scoring & Savings Recommendations
```

### 1. Data Ingestion & Cleaning (`test_cleaning.py`)
*   **Verify Valid Ingestion**: Checks that a standard CSV is parsed and cleaned correctly.
*   **Duplicate & Anomaly Filter**: Verifies that duplicate rows are dropped and negative transaction amounts are filtered out.
*   **Category Normalization**: Confirms that invalid categories (e.g. `cryptocurrency_purchase`) are mapped to `Other`, and valid categories are capitalized.

### 2. Time-Series Forecasting (`test_forecasting.py`)
*   **Model Training**: Fits a Ridge Regression model on synthetic daily spending history and verifies that model coefficients are successfully created.
*   **Inference**: Verifies that next-month predictions return values within a statistically reasonable range (between lower and upper bounds).
*   **Polynomial Projection**: Tests that the current month-end polynomial curve projection is greater than or equal to the actual spent amount.
*   **Chronological Backtesting**: Runs model evaluations on test splits and verifies that regression metrics (MAE, RMSE, $R^2$) are calculated.

### 3. Risk & Recommendations (`test_recommendations.py`)
*   **Multi-Factor Risk Scoring**: Verifies that low spending relative to the budget yields a `LOW` risk score ($\le 30$) and high spending yields a `HIGH` risk score ($> 70$).
*   **Actionable Recommendations**: Confirms that exceeding category thresholds (e.g., spending ₹1,500 on Food with a ₹2,000 total budget) triggers specific savings cards.

---

## 🚀 Running the Tests

### Option A: Using Python's Built-in Unittest (No Installations Required)
Run the tests directly from the root directory:
```bash
python -m unittest discover -s tests
```

### Option B: Using Pytest
If you have `pytest` installed, run:
```bash
pytest tests/
```

### Option C: Generating a Coverage Report
To verify that our test suite achieves the **70%+ coverage target**:
1.  **Install Coverage**:
    ```bash
    pip install coverage
    ```
2.  **Run Tests with Coverage**:
    ```bash
    coverage run -m unittest discover -s tests
    ```
3.  **View the Report**:
    ```bash
    coverage report -m
    ```
