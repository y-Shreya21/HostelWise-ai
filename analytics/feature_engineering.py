# HostelWise AI - Machine Learning Feature Engineering
import pandas as pd
import numpy as np

def create_cyclical_features(df: pd.DataFrame, col: str, max_val: int) -> pd.DataFrame:
    """Create sine and cosine transformations of a cyclical column."""
    df_copy = df.copy()
    df_copy[f'{col}_sin'] = np.sin(2 * np.pi * df_copy[col] / max_val)
    df_copy[f'{col}_cos'] = np.cos(2 * np.pi * df_copy[col] / max_val)
    return df_copy

def build_features_for_forecasting(df: pd.DataFrame) -> tuple:
    """
    Constructs the feature matrix X and target vector y for training the forecasting model.
    Groups raw transactions into a daily time-series, then engineers features:
    - Time Trend (day index)
    - Weekday / Weekend indicator
    - Cyclical Day of Week
    - Cyclical Day of Month
    - First week of month indicator (payday/subscription bills)
    """
    if len(df) == 0:
        return np.array([]), np.array([]), []
        
    # 1. Aggregate to daily spend
    daily_df = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_df.columns = ['date', 'amount']
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_df = daily_df.sort_values(by='date')
    
    # 2. Add base features
    daily_df['day_index'] = (daily_df['date'] - daily_df['date'].min()).dt.days
    daily_df['day_of_week'] = daily_df['date'].dt.dayofweek
    daily_df['day_of_month'] = daily_df['date'].dt.day
    daily_df['first_week'] = (daily_df['day_of_month'] <= 7).astype(int)
    
    # 3. Add cyclical features
    daily_df = create_cyclical_features(daily_df, 'day_of_week', 7)
    daily_df = create_cyclical_features(daily_df, 'day_of_month', 31)
    
    # 4. Compile feature list
    feature_cols = [
        'day_index', 
        'first_week',
        'day_of_week_sin', 'day_of_week_cos',
        'day_of_month_sin', 'day_of_month_cos'
    ]
    
    X = daily_df[feature_cols].values
    y = daily_df['amount'].values
    
    return X, y, feature_cols
