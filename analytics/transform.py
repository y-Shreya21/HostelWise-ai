# HostelWise AI - Data Transformations
import pandas as pd
import numpy as np

def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal fields from the date column."""
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy['year'] = df_copy['date'].dt.year
    df_copy['month'] = df_copy['date'].dt.month
    df_copy['day'] = df_copy['date'].dt.day
    df_copy['day_of_week'] = df_copy['date'].dt.dayofweek
    df_copy['day_of_year'] = df_copy['date'].dt.dayofyear
    df_copy['is_weekend'] = df_copy['day_of_week'].isin([5, 6]).astype(int)
    return df_copy

def calculate_rolling_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate 7-day and 30-day rolling averages of daily spending."""
    if len(df) == 0:
        return pd.DataFrame(columns=['date', 'daily_amount', 'rolling_7', 'rolling_30'])
        
    # Group by date to get daily totals
    daily_df = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_df.columns = ['date', 'daily_amount']
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_df = daily_df.sort_values(by='date')
    
    # Calculate rolling metrics
    daily_df['rolling_7'] = daily_df['daily_amount'].rolling(window=7, min_periods=1).mean()
    daily_df['rolling_30'] = daily_df['daily_amount'].rolling(window=30, min_periods=1).mean()
    
    return daily_df

def get_spending_velocity_status(df: pd.DataFrame) -> dict:
    """
    Evaluate if spending velocity is accelerating, stable, or decelerating.
    Compares the 7-day rolling average to the 30-day rolling average.
    """
    rolling_df = calculate_rolling_averages(df)
    if len(rolling_df) < 7:
        return {"status": "STABLE", "ratio": 1.0, "message": "Not enough history to calculate velocity."}
        
    latest_row = rolling_df.iloc[-1]
    r7 = latest_row['rolling_7']
    r30 = latest_row['rolling_30']
    
    if r30 == 0:
        return {"status": "STABLE", "ratio": 1.0, "message": "No spending recorded."}
        
    ratio = r7 / r30
    
    if ratio > 1.15:
        status = "ACCELERATING"
        msg = f"Your weekly spending rate (₹{r7:.2f}/day) is {((ratio - 1) * 100):.0f}% higher than your monthly average (₹{r30:.2f}/day). Try to cut back on discretionary items."
    elif ratio < 0.85:
        status = "DECELERATING"
        msg = f"Great job! Your weekly spending rate (₹{r7:.2f}/day) is {((1 - ratio) * 100):.0f}% lower than your monthly average (₹{r30:.2f}/day). Keep it up!"
    else:
        status = "STABLE"
        msg = f"Your weekly spending rate (₹{r7:.2f}/day) is stable and in line with your monthly average (₹{r30:.2f}/day)."
        
    return {
        "status": status,
        "ratio": round(ratio, 2),
        "message": msg,
        "rolling_7": round(r7, 2),
        "rolling_30": round(r30, 2)
    }
