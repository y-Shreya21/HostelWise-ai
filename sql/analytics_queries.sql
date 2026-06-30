-- ============================================================================
-- HOSTELWISE AI - Advanced BigQuery Analytics Queries
-- ============================================================================

-- 1. IDENTIFY SPENDING OUTLIERS (ANOMALY DETECTION)
-- Find transactions that are 1.5x standard deviations higher than the category average
-- for a specific student, excluding fixed recharges and education fees.
WITH category_stats AS (
  SELECT
    student_id,
    category,
    AVG(amount) AS avg_amount,
    STDDEV(amount) AS stddev_amount,
    COUNT(*) AS transaction_count
  FROM
    `hostelwise_ai_dataset.expenses`
  GROUP BY
    student_id, category
)
SELECT
  e.expense_id,
  e.student_id,
  e.date,
  e.amount,
  e.category,
  e.subcategory,
  e.description,
  ROUND(s.avg_amount, 2) AS category_average,
  ROUND(s.stddev_amount, 2) AS category_stddev,
  ROUND(e.amount - s.avg_amount, 2) AS deviation_from_avg
FROM
  `hostelwise_ai_dataset.expenses` e
JOIN
  category_stats s ON e.student_id = s.student_id AND e.category = s.category
WHERE
  e.amount > (s.avg_amount + (1.5 * COALESCE(s.stddev_amount, 0)))
  AND s.transaction_count > 3
  AND e.category NOT IN ('Recharge', 'Education')
ORDER BY
  deviation_from_avg DESC;

-- 2. MONTH-OVER-MONTH SPENDING GROWTH RATE
-- Calculates the percentage growth in monthly expenses for each student.
WITH monthly_spend AS (
  SELECT
    student_id,
    FORMAT_TIMESTAMP('%Y-%m', date) AS month_year,
    SUM(amount) AS total_spent
  FROM
    `hostelwise_ai_dataset.expenses`
  GROUP BY
    student_id, month_year
),
prev_month_spend AS (
  SELECT
    student_id,
    month_year,
    total_spent,
    LAG(total_spent) OVER (PARTITION BY student_id ORDER BY month_year) AS prev_total_spent
  FROM
    monthly_spend
)
SELECT
  student_id,
  month_year,
  total_spent,
  COALESCE(prev_total_spent, 0) AS previous_month_spent,
  CASE
    WHEN prev_total_spent IS NULL THEN 0.0
    ELSE ROUND(((total_spent - prev_total_spent) / prev_total_spent) * 100, 2)
  END AS mom_growth_rate_pct
FROM
  prev_month_spend
ORDER BY
  student_id, month_year DESC;

-- 3. PEAK SPENDING HOURS (DIAL VELOCITY)
-- Identifies the hour of the day when the student makes the most purchases.
SELECT
  student_id,
  EXTRACT(HOUR FROM date) AS hour_of_day,
  COUNT(*) AS transaction_count,
  ROUND(SUM(amount), 2) AS total_spent
FROM
  `hostelwise_ai_dataset.expenses`
GROUP BY
  student_id, hour_of_day
ORDER BY
  total_spent DESC;
