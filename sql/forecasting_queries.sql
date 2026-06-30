-- ============================================================================
-- HOSTELWISE AI - BigQuery Forecasting & Accuracy Queries
-- ============================================================================

-- 1. FETCH LATEST ACTIVE FORECASTS
-- Retrieves the most recent next-month spending prediction for each student.
SELECT
  student_id,
  forecast_date,
  predicted_amount,
  lower_bound,
  upper_bound,
  created_at
FROM (
  SELECT
    student_id,
    forecast_date,
    predicted_amount,
    lower_bound,
    upper_bound,
    created_at,
    ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY created_at DESC) as rn
  FROM
    `hostelwise_ai_dataset.forecasts`
  WHERE
    target_period = 'NEXT_MONTH'
)
WHERE rn = 1;

-- 2. BACKTESTING & ACCURACY EVALUATION (MAPE)
-- Compares historical next-month forecasts against the actual spending 
-- recorded in the subsequent 30 days.
WITH actual_monthly_spends AS (
  SELECT
    student_id,
    FORMAT_TIMESTAMP('%Y-%m', date) AS month_year,
    SUM(amount) AS actual_spent
  FROM
    `hostelwise_ai_dataset.expenses`
  GROUP BY
    student_id, month_year
),
historical_forecasts AS (
  -- Match a forecast generated in Month M to the actual spend in Month M+1
  SELECT
    student_id,
    FORMAT_DATE('%Y-%m', DATE_ADD(forecast_date, INTERVAL 1 MONTH)) AS target_month_year,
    predicted_amount AS predicted_spent
  FROM
    `hostelwise_ai_dataset.forecasts`
  WHERE
    target_period = 'NEXT_MONTH'
)
SELECT
  f.student_id,
  f.target_month_year,
  ROUND(f.predicted_spent, 2) AS predicted_amount,
  ROUND(a.actual_spent, 2) AS actual_amount,
  ROUND(ABS(a.actual_spent - f.predicted_spent), 2) AS absolute_error,
  ROUND((ABS(a.actual_spent - f.predicted_spent) / a.actual_spent) * 100, 2) AS absolute_percentage_error_pct
FROM
  historical_forecasts f
JOIN
  actual_monthly_spends a ON f.student_id = a.student_id AND f.target_month_year = a.month_year
ORDER BY
  f.target_month_year DESC;
