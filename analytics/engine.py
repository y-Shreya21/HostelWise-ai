# HostelWise AI - Analytics & Aggregation Engine
import pandas as pd  # pyright: ignore[reportMissingImports]

def get_basic_kpis(df, budget_limit=10000.0):
    """
    Calculate high-level KPIs from the cleaned DataFrame.
    Returns a dictionary of metrics.
    """
    if len(df) == 0:
        return {
            'total_expense': 0.0,
            'avg_daily_spend': 0.0,
            'highest_category': 'None',
            'highest_category_amount': 0.0,
            'budget_utilization_pct': 0.0
        }
        
    # Convert to pandas if it is a cuDF DataFrame for scalar extractions
    is_cudf = False
    try:
        import cudf  # type: ignore
        if isinstance(df, cudf.DataFrame):
            is_cudf = True
    except ImportError:
        pass

    # 1. Total Expense
    total_expense = float(df['amount'].sum())
    
    # 2. Average Daily Spend
    # Group by date (day level) and get average
    # First extract the date portion
    if is_cudf:
        daily_sums = df.groupby(df['date'].dt.date)['amount'].sum()
        avg_daily_spend = float(daily_sums.mean())
    else:
        daily_sums = df.groupby(df['date'].dt.date)['amount'].sum()
        avg_daily_spend = float(daily_sums.mean())
        
    # 3. Highest Spending Category
    cat_sums = df.groupby('category')['amount'].sum()
    if len(cat_sums) > 0:
        # Get the category with max spending
        highest_cat = cat_sums.idxmax()
        highest_cat_val = float(cat_sums.max())
        # In cuDF, idxmax() returns a Series or scalar. Let's make sure it is a string.
        if hasattr(highest_cat, 'values'):
            highest_cat = highest_cat.values[0]
    else:
        highest_cat = 'None'
        highest_cat_val = 0.0
        
    # 4. Budget Utilization
    utilization = (total_expense / budget_limit) * 100 if budget_limit > 0 else 0.0
    
    return {
        'total_expense': round(total_expense, 2),
        'avg_daily_spend': round(avg_daily_spend, 2) if not pd.isna(avg_daily_spend) else 0.0,
        'highest_category': str(highest_cat),
        'highest_category_amount': round(highest_cat_val, 2),
        'budget_utilization_pct': round(utilization, 2)
    }

def get_category_spending(df):
    """Calculate spending grouped by category."""
    if len(df) == 0:
        return pd.DataFrame(columns=['category', 'amount'])
        
    cat_df = df.groupby('category')['amount'].sum().reset_index()
    cat_df = cat_df.sort_values(by='amount', ascending=False)
    
    # Return as pandas DataFrame for easier UI rendering
    try:
        import cudf  # type: ignore
        if isinstance(cat_df, cudf.DataFrame):
            return cat_df.to_pandas()
    except ImportError:
        pass
    return cat_df

def get_weekly_spending(df):
    """Calculate spending grouped by week of the year."""
    if len(df) == 0:
        return pd.DataFrame(columns=['week', 'amount'])
        
    # Extract week starting date or week number
    # We will use the week number for simplicity
    df_copy = df.copy()
    df_copy['week'] = df_copy['date'].dt.to_period('W').dt.start_time
    
    weekly_df = df_copy.groupby('week')['amount'].sum().reset_index()
    weekly_df = weekly_df.sort_values(by='week')
    
    try:
        import cudf  # type: ignore
        if isinstance(weekly_df, cudf.DataFrame):
            return weekly_df.to_pandas()
    except ImportError:
        pass
    return weekly_df

def get_daily_spending(df):
    """Calculate spending grouped by day."""
    if len(df) == 0:
        return pd.DataFrame(columns=['date', 'amount'])
        
    df_copy = df.copy()
    df_copy['day'] = df_copy['date'].dt.date
    
    daily_df = df_copy.groupby('day')['amount'].sum().reset_index()
    daily_df = daily_df.sort_values(by='day')
    
    # Convert 'day' column to string or datetime for plotting
    try:
        import cudf  # type: ignore
        if isinstance(daily_df, cudf.DataFrame):
            daily_df = daily_df.to_pandas()
    except ImportError:
        pass
        
    daily_df['day'] = pd.to_datetime(daily_df['day'])
    return daily_df

def get_subcategory_breakdown(df, category):
    """Get subcategory-wise breakdown for a specific category."""
    # Filter by category
    filtered_df = df[df['category'] == category]
    if len(filtered_df) == 0:
        return pd.DataFrame(columns=['subcategory', 'amount'])
        
    sub_df = filtered_df.groupby('subcategory')['amount'].sum().reset_index()
    sub_df = sub_df.sort_values(by='amount', ascending=False)
    
    try:
        import cudf  # type: ignore
        if isinstance(sub_df, cudf.DataFrame):
            return sub_df.to_pandas()
    except ImportError:
        pass
    return sub_df

def get_payment_mode_distribution(df):
    """Get spending distribution by payment mode."""
    if len(df) == 0:
        return pd.DataFrame(columns=['payment_mode', 'amount'])
        
    pay_df = df.groupby('payment_mode')['amount'].sum().reset_index()
    pay_df = pay_df.sort_values(by='amount', ascending=False)
    
    try:
        import cudf  # type: ignore
        if isinstance(pay_df, cudf.DataFrame):
            return pay_df.to_pandas()
    except ImportError:
        pass
    return pay_df
