-- ============================================================================
-- HOSTELWISE AI - Google BigQuery Schema and Analytical Queries
-- ============================================================================

-- CREATE SCHEMA (DATASET) IN BIGQUERY
-- CREATE SCHEMA IF NOT EXISTS `hostelwise_ai_dataset` OPTIONS(location="us");

-- ----------------------------------------------------------------------------
-- 1. TRANSACTIONAL EXPENSES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.expenses` (
  expense_id STRING NOT NULL OPTIONS(description="UUID of the expense record"),
  student_id STRING NOT NULL OPTIONS(description="Identifier for the student"),
  date TIMESTAMP NOT NULL OPTIONS(description="Date and time of transaction"),
  amount NUMERIC NOT NULL OPTIONS(description="Amount in INR (₹)"),
  category STRING NOT NULL OPTIONS(description="High-level category"),
  subcategory STRING OPTIONS(description="Detailed subcategory"),
  description STRING OPTIONS(description="User notes or merchant description"),
  payment_mode STRING OPTIONS(description="UPI, Cash, Debit Card, Credit Card"),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(date)
CLUSTER BY student_id, category;

-- ----------------------------------------------------------------------------
-- 2. MONTHLY BUDGETS CONFIGURATION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.budgets` (
  student_id STRING NOT NULL,
  month_year STRING NOT NULL OPTIONS(description="Format: YYYY-MM"),
  category STRING NOT NULL OPTIONS(description="Category name or 'ALL' for overall budget"),
  allocated_amount NUMERIC NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PRIMARY KEY (student_id, month_year, category) NOT ENFORCED;

-- ----------------------------------------------------------------------------
-- 3. FORECAST PREDICTIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.forecasts` (
  student_id STRING NOT NULL,
  forecast_date DATE NOT NULL,
  target_period STRING NOT NULL OPTIONS(description="CURRENT_MONTH_END or NEXT_MONTH"),
  predicted_amount NUMERIC NOT NULL,
  lower_bound NUMERIC,
  upper_bound NUMERIC,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ----------------------------------------------------------------------------
-- 4. BUDGET RISK ASSESSMENTS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.risk_scores` (
  student_id STRING NOT NULL,
  month_year STRING NOT NULL,
  current_spend NUMERIC NOT NULL,
  projected_spend NUMERIC NOT NULL,
  budget_limit NUMERIC NOT NULL,
  risk_score INT64 NOT NULL OPTIONS(description="Range 0 - 100"),
  risk_level STRING NOT NULL OPTIONS(description="LOW, MODERATE, HIGH"),
  calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ----------------------------------------------------------------------------
-- 5. SAVINGS RECOMMENDATIONS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.recommendations` (
  recommendation_id STRING NOT NULL,
  student_id STRING NOT NULL,
  category STRING NOT NULL,
  potential_savings NUMERIC NOT NULL,
  recommendation_text STRING NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);


-- ============================================================================
-- ANALYTICAL QUERIES (LOOKER STUDIO COMPATIBLE VIEWS)
-- ============================================================================

-- A. VIEW: MONTHLY SUMMARY (Looker Studio View)
-- Compares total monthly spending against overall budget and calculates progress
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

-- B. VIEW: CATEGORY WISE UTILIZATION
-- Detail-level spending compared to category-specific budgets
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

-- C. QUERY: SPENDING VELOCITY & OUTLIERS
-- Identifies transactions that are 2x higher than the average for that student/category
CREATE OR REPLACE VIEW `hostelwise_ai_dataset.view_spending_outliers` AS
WITH stats AS (
  SELECT
    student_id,
    category,
    AVG(amount) AS avg_amount,
    STDDEV(amount) AS stddev_amount
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
  s.avg_amount AS category_average,
  ROUND(e.amount - s.avg_amount, 2) AS deviation_from_avg
FROM
  `hostelwise_ai_dataset.expenses` e
JOIN
  stats s ON e.student_id = s.student_id AND e.category = s.category
WHERE
  e.amount > (s.avg_amount + (1.5 * COALESCE(s.stddev_amount, 0)))
  AND e.category NOT IN ('Recharge', 'Education'); -- Exclude standard large periodic bills
