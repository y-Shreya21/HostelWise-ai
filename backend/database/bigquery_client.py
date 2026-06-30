# HostelWise AI - Backend BigQuery Database Client
import pandas as pd
from typing import Optional
from cloud.bigquery import bq_manager

class BigQueryDBClient:
    def __init__(self):
        self.manager = bq_manager
        self.is_active = bq_manager.is_active

    def get_expenses(self, student_id: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch all raw expense records for a student."""
        if not self.is_active:
            return None
            
        query = f"""
        SELECT expense_id, student_id, date, amount, category, subcategory, description, payment_mode
        FROM `{self.manager.dataset_name}.expenses`
        WHERE student_id = '{student_id}'
        ORDER BY date DESC
        LIMIT {limit}
        """
        try:
            return self.manager.query_to_dataframe(query)
        except Exception:
            return None

    def get_monthly_summary(self, student_id: str) -> Optional[pd.DataFrame]:
        """Query the monthly summary analytical view."""
        if not self.is_active:
            return None
            
        query = f"""
        SELECT month_year, total_spent, budget_amount, budget_utilization_pct, avg_transaction_amount, total_transactions
        FROM `{self.manager.dataset_name}.view_monthly_summary`
        WHERE student_id = '{student_id}'
        ORDER BY month_year DESC
        """
        try:
            return self.manager.query_to_dataframe(query)
        except Exception:
            return None

    def get_category_summary(self, student_id: str, month_year: str) -> Optional[pd.DataFrame]:
        """Query the category summary analytical view."""
        if not self.is_active:
            return None
            
        query = f"""
        SELECT category, category_spent, category_budget, category_utilization_pct, transaction_count
        FROM `{self.manager.dataset_name}.view_category_summary`
        WHERE student_id = '{student_id}' AND month_year = '{month_year}'
        ORDER BY category_spent DESC
        """
        try:
            return self.manager.query_to_dataframe(query)
        except Exception:
            return None

# Instantiated database client
bq_db_client = BigQueryDBClient()
