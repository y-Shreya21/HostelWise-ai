# HostelWise AI - GPU cuDF Benchmark Pipeline
import time

def run_cudf_pipeline(file_path: str) -> tuple:
    """Runs the cleaning and aggregation pipeline using NVIDIA cuDF on GPU."""
    # Dynamic import to prevent crash on non-GPU systems
    import cudf  # type: ignore
    from analytics.clean import clean_expense_data
    from analytics.engine import (
        get_basic_kpis, get_category_spending, get_weekly_spending, 
        get_daily_spending, get_payment_mode_distribution
    )
    
    start_time = time.perf_counter()
    
    # 1. Load & Clean Data
    df = cudf.read_csv(file_path)
    cleaned_df = clean_expense_data(df, use_gpu=True)
    
    # 2. Run Aggregations
    # cuDF operations will execute directly on GPU cores
    _ = get_basic_kpis(cleaned_df)
    _ = get_category_spending(cleaned_df)
    _ = get_weekly_spending(cleaned_df)
    _ = get_daily_spending(cleaned_df)
    _ = get_payment_mode_distribution(cleaned_df)
    
    duration = time.perf_counter() - start_time
    return duration, len(cleaned_df)
