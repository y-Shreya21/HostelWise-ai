-- ============================================================================
-- HOSTELWISE AI - Google BigQuery Table Schemas (DDL)
-- ============================================================================

-- 1. Transactional Expenses Table
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.expenses` (
  expense_id STRING NOT NULL OPTIONS(description="UUID of the expense record"),
  student_id STRING NOT NULL OPTIONS(description="Identifier for the student"),
  date TIMESTAMP NOT NULL OPTIONS(description="Date and time of transaction"),
  amount NUMERIC NOT NULL OPTIONS(description="Amount in INR (₹)"),
  category STRING NOT NULL OPTIONS(description="High-level category (e.g. Food, Travel)"),
  subcategory STRING OPTIONS(description="Detailed subcategory (e.g. Canteen, Cab)"),
  description STRING OPTIONS(description="User notes or merchant description"),
  payment_mode STRING OPTIONS(description="UPI, Cash, Debit Card, Credit Card"),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(date)
CLUSTER BY student_id, category;

-- 2. Monthly Budgets Configuration Table
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.budgets` (
  student_id STRING NOT NULL,
  month_year STRING NOT NULL OPTIONS(description="Format: YYYY-MM"),
  category STRING NOT NULL OPTIONS(description="Category name or 'ALL' for overall budget"),
  allocated_amount NUMERIC NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PRIMARY KEY (student_id, month_year, category) NOT ENFORCED;

-- 3. Spending Forecast Predictions Table
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.forecasts` (
  student_id STRING NOT NULL,
  forecast_date DATE NOT NULL,
  target_period STRING NOT NULL OPTIONS(description="CURRENT_MONTH_END or NEXT_MONTH"),
  predicted_amount NUMERIC NOT NULL,
  lower_bound NUMERIC,
  upper_bound NUMERIC,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 4. Budget Risk Scores Table
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.risk_scores` (
  student_id STRING NOT NULL,
  month_year STRING NOT NULL,
  current_spend NUMERIC NOT NULL,
  projected_spend NUMERIC NOT NULL,
  budget_limit NUMERIC NOT NULL,
  risk_score INT64 NOT NULL OPTIONS(description="Range 0 - 100"),
  risk_level STRING NOT NULL OPTIONS(description="LOW, MEDIUM, HIGH"),
  calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 5. Savings Recommendations Table
CREATE TABLE IF NOT EXISTS `hostelwise_ai_dataset.recommendations` (
  recommendation_id STRING NOT NULL,
  student_id STRING NOT NULL,
  category STRING NOT NULL,
  potential_savings NUMERIC NOT NULL,
  recommendation_text STRING NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
