# HostelWise AI - Local SQLite Storage Engine
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
from cloud.config import cloud_settings

class SQLiteDBManager:
    def __init__(self):
        self.db_path = cloud_settings.SQLITE_DB_PATH
        self.init_schema()

    def get_connection(self):
        """Create a new database connection."""
        return sqlite3.connect(self.db_path)

    def init_schema(self):
        """Initializes SQLite tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Expenses Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                description TEXT,
                payment_mode TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Budgets Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                student_id TEXT NOT NULL,
                month_year TEXT NOT NULL,
                category TEXT NOT NULL,
                allocated_amount REAL NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_id, month_year, category)
            )
            """)
            
            # Insert a default budget if empty
            cursor.execute("SELECT COUNT(*) FROM budgets WHERE student_id = 'default_student'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO budgets (student_id, month_year, category, allocated_amount) 
                VALUES ('default_student', ?, 'ALL', 10000.0)
                """, (datetime.now().strftime('%Y-%m'),))
                
            conn.commit()

    def add_expense(self, record: dict) -> bool:
        """Insert a single expense record into SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO expenses (expense_id, student_id, date, amount, category, subcategory, description, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record['expense_id'], record['student_id'], record['date'], 
                    record['amount'], record['category'], record['subcategory'], 
                    record['description'], record['payment_mode']
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"SQLite insertion error: {e}")
                return False

    def bulk_insert_expenses(self, records: list) -> int:
        """Insert multiple expense records in a single transaction."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany("""
                INSERT INTO expenses (expense_id, student_id, date, amount, category, subcategory, description, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, records)
                conn.commit()
                return len(records)
            except Exception as e:
                print(f"SQLite bulk insertion error: {e}")
                return 0

    def get_expenses_dataframe(self, student_id: str) -> pd.DataFrame:
        """Retrieve all expenses for a student as a Pandas DataFrame."""
        with self.get_connection() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM expenses WHERE student_id = ? ORDER BY date DESC", 
                conn, 
                params=(student_id,)
            )
            # Standardize date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            return df

    def set_budget_limit(self, student_id: str, month_year: str, category: str, amount: float):
        """Insert or update a budget limit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO budgets (student_id, month_year, category, allocated_amount, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(student_id, month_year, category) 
            DO UPDATE SET allocated_amount = excluded.allocated_amount, updated_at = CURRENT_TIMESTAMP
            """, (student_id, month_year, category, amount))
            conn.commit()

    def get_budget_limit(self, student_id: str, month_year: str, category: str = 'ALL') -> float:
        """Retrieve the budget limit for a category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT allocated_amount FROM budgets WHERE student_id = ? AND month_year = ? AND category = ?",
                (student_id, month_year, category)
            )
            row = cursor.fetchone()
            if row:
                return float(row[0])
            return 10000.0  # Default fallback

# Global SQLite manager instance
sqlite_manager = SQLiteDBManager()
