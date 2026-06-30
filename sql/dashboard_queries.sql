-- ============================================================================
-- HOSTELWISE AI - Looker Studio Dashboard Views (DML / DDL)
-- ============================================================================

-- 1. VIEW: MONTHLY SUMMARY VIEW
-- Aggregates overall monthly spending and compares it against overall budgets.
CREATE OR REPLACE VIEW `hostelwise_ai_dataset.view_monthly_summary` AS
WITH spent AS (
  SELECT
    student_id,
    FORMAT_TIMESTAMP('%Y-%m', date) AS month_year,
    SUM(amount) AS total_spent,
    AVG(amount) AS avg_transaction_amount,
    COUNT(*) AS total_transactions
  FROM
    `hostelwise_ai_dataset.expenses`
  GROUP BY
    student_id, month_year
),
budget AS (
  SELECT
    student_id,
    month_year,
    allocated_amount AS budget_amount
  FROM
    `hostelwise_ai_dataset.budgets`
  WHERE
    category = 'ALL'
)
SELECT
  s.student_id,
  s.month_year,
  s.total_spent,
  COALESCE(b.budget_amount, 0) AS budget_amount,
  CASE 
    WHEN b.budget_amount IS NULL THEN 0
    ELSE ROUND((s.total_spent / b.budget_amount) * 100, 2)
  END AS budget_utilization_pct,
  s.avg_transaction_amount,
  s.total_transactions
FROM
  spent s
LEFT JOIN
  budget b ON s.student_id = b.student_id AND s.month_year = b.month_year;

-- 2. VIEW: CATEGORY SUMMARY VIEW
-- Detail-level spending compared to category-specific budgets.
CREATE OR REPLACE VIEW `hostelwise_ai_dataset.view_category_summary` AS
WITH spent AS (
  SELECT
    student_id,
    FORMAT_TIMESTAMP('%Y-%m', date) AS month_year,
    category,
    SUM(amount) AS category_spent,
    COUNT(*) AS transaction_count
  FROM
    `hostelwise_ai_dataset.expenses`
  GROUP BY
    student_id, month_year, category
),
budget AS (
  SELECT
    student_id,
    month_year,
    category,
    allocated_amount AS category_budget
  FROM
    `hostelwise_ai_dataset.budgets`
  WHERE
    category != 'ALL'
)
SELECT
  s.student_id,
  s.month_year,
  s.category,
  s.category_spent,
  COALESCE(b.category_budget, 0) AS category_budget,
  CASE
    WHEN b.category_budget IS NULL THEN 0
    ELSE ROUND((s.category_spent / b.category_budget) * 100, 2)
  END AS category_utilization_pct,
  s.transaction_count
FROM
  spent s
LEFT JOIN
  budget b ON s.student_id = b.student_id AND s.month_year = b.month_year AND s.category = b.category;
