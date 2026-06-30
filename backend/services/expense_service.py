# HostelWise AI - Expense Management Service
import pandas as pd
import uuid
from datetime import datetime
from backend.database.models import sqlite_manager
from cloud.bigquery import bq_manager

class ExpenseService:
    def __init__(self):
        self.sqlite = sqlite_manager
        self.bq = bq_manager

    def add_single_expense(
        self, student_id: str, amount: float, category: str, 
        subcategory: str, description: str, payment_mode: str, 
        date_str: str = None
    ) -> dict:
        """Adds an expense to both local SQLite and BigQuery (if active)."""
        expense_id = str(uuid.uuid4())
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        record = {
            'expense_id': expense_id,
            'student_id': student_id,
            'date': date_str,
            'amount': amount,
            'category': category,
            'subcategory': subcategory,
            'description': description,
            'payment_mode': payment_mode
        }
        
        # 1. Save to local SQLite
        self.sqlite.add_expense(record)
        
        # 2. Save to BigQuery
        if self.bq.is_active:
            try:
                bq_record = record.copy()
                # BigQuery requires ISO timestamps
                bq_record['date'] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').isoformat()
                self.bq.insert_rows_json("expenses", [bq_record])
            except Exception as e:
                print(f"Failed to stream record to BigQuery: {e}")
                
        return record

    def load_bulk_data(self, student_id: str, df: pd.DataFrame) -> int:
        """Uploads a cleaned DataFrame into local SQLite and BigQuery."""
        records = []
        for _, row in df.iterrows():
            expense_id = str(uuid.uuid4())
            date_str = row['date'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row['date'], pd.Timestamp) else str(row['date'])
            records.append((
                expense_id,
                student_id,
                date_str,
                float(row['amount']),
                str(row['category']),
                str(row['subcategory']),
                str(row['description']),
                str(row['payment_mode'])
            ))
            
        # 1. Save to local SQLite
        inserted_count = self.sqlite.bulk_insert_expenses(records)
        
        # 2. Save to BigQuery
        if self.bq.is_active:
            try:
                bq_df = pd.DataFrame(records, columns=['expense_id', 'student_id', 'date', 'amount', 'category', 'subcategory', 'description', 'payment_mode'])
                bq_df['date'] = pd.to_datetime(bq_df['date'])
                self.bq.load_dataframe(bq_df, "expenses")
            except Exception as e:
                print(f"Failed to bulk load DataFrame to BigQuery: {e}")
                
        return inserted_count

    def get_student_expenses_df(self, student_id: str) -> pd.DataFrame:
        """Retrieve all expenses for a student."""
        return self.sqlite.get_expenses_dataframe(student_id)

    def set_student_budget(self, student_id: str, month_year: str, category: str, amount: float):
        """Set budget limit for a category."""
        self.sqlite.set_budget_limit(student_id, month_year, category, amount)
        
        if self.bq.is_active:
            try:
                record = {
                    'student_id': student_id,
                    'month_year': month_year,
                    'category': category,
                    'allocated_amount': amount,
                    'updated_at': datetime.now().isoformat()
                }
                self.bq.insert_rows_json("budgets", [record])
            except Exception as e:
                print(f"Failed to sync budget to BigQuery: {e}")

    def get_student_budget(self, student_id: str, month_year: str, category: str = 'ALL') -> float:
        """Retrieve budget limit."""
        return self.sqlite.get_budget_limit(student_id, month_year, category)

# Global service instance
expense_service = ExpenseService()
