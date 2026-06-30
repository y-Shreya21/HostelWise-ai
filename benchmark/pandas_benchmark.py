# HostelWise AI - CPU Pandas Benchmark Pipeline
import time
import pandas as pd
from analytics.clean import clean_expense_data
from analytics.engine import (
    get_basic_kpis, get_category_spending, get_weekly_spending, 
    get_daily_spending, get_payment_mode_distribution
)

def run_pandas_pipeline(file_path: str) -> tuple:
    """Runs the cleaning and aggregation pipeline using CPU Pandas and returns duration and count."""
    start_time = time.perf_counter()
    
    # 1. Load & Clean Data
    df = pd.read_csv(file_path)
    cleaned_df = clean_expense_data(df, use_gpu=False)
    
    # 2. Run Aggregations
    _ = get_basic_kpis(cleaned_df)
    _ = get_category_spending(cleaned_df)
    _ = get_weekly_spending(cleaned_df)
    _ = get_daily_spending(cleaned_df)
    _ = get_payment_mode_distribution(cleaned_df)
    
    duration = time.perf_counter() - start_time
    return duration, len(cleaned_df)
