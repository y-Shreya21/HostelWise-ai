# HostelWise AI - Inference and Projections
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from .train import train_forecasting_model

def predict_next_month_spending(df: pd.DataFrame, model=None, std_error=0.0) -> dict:
    """
    Predict next month's spending. If no model is passed, it trains one on the fly.
    """
    if len(df) < 15:
        # Fallback to simple historical daily average if history is too short
        df_daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
        avg_daily = float(df_daily['amount'].mean()) if len(df_daily) > 0 else 300.0
        predicted = avg_daily * 30
        return {
            'predicted_spend': round(predicted, 2),
            'lower_bound': round(predicted * 0.85, 2),
            'upper_bound': round(predicted * 1.15, 2),
            'model_type': 'Daily Average Baseline'
        }
        
    if model is None:
        model, _, std_error = train_forecasting_model(df)
        
    # Group by date to get the last date
    df_daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    last_date = df_daily['date'].max()
    min_date = df_daily['date'].min()
    
    # Generate dates for the next 30 days
    next_month_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    
    # Recreate features for the future dates
    future_features = []
    for i, dt in enumerate(next_month_dates):
        day_idx = (dt - min_date).days
        day_of_week = dt.dayofweek
        day_of_month = dt.day
        first_week = 1 if day_of_month <= 7 else 0
        
        # Cyclical features
        dow_sin = np.sin(2 * np.pi * day_of_week / 7)
        dow_cos = np.cos(2 * np.pi * day_of_week / 7)
        dom_sin = np.sin(2 * np.pi * day_of_month / 31)
        dom_cos = np.cos(2 * np.pi * day_of_month / 31)
        
        future_features.append([
            day_idx, first_week,
            dow_sin, dow_cos,
            dom_sin, dom_cos
        ])
        
    predictions = model.predict(np.array(future_features))
    # Ensure no negative daily spends
    predictions = np.maximum(predictions, 0)
    
    predicted_sum = float(np.sum(predictions))
    margin = 1.96 * std_error * np.sqrt(30)
    
    return {
        'predicted_spend': round(predicted_sum, 2),
        'lower_bound': round(max(predicted_sum - margin, 0), 2),
        'upper_bound': round(predicted_sum + margin, 2),
        'model_type': 'Ridge Regression Time-Series'
    }

def predict_current_month_end(df: pd.DataFrame, budget_limit: float = 10000.0, current_date=None) -> dict:
    """
    Predict total spending at the end of the current month.
    Uses Polynomial Ridge Regression on cumulative daily spending.
    """
    if current_date is None:
        current_date = datetime.now()
    else:
        current_date = pd.to_datetime(current_date)
        
    df['date'] = pd.to_datetime(df['date'])
    start_of_month = pd.Timestamp(current_date.year, current_date.month, 1)
    end_of_day = pd.Timestamp(current_date.year, current_date.month, current_date.day, 23, 59, 59)
    
    month_df = df[(df['date'] >= start_of_month) & (df['date'] <= end_of_day)]
    
    days_in_month = pd.Period(current_date.strftime('%Y-%m')).days_in_month
    days_elapsed = (current_date - start_of_month).days + 1
    
    if len(month_df) < 5 or days_elapsed < 3:
        current_spend = float(month_df['amount'].sum()) if len(month_df) > 0 else 0.0
        daily_rate = current_spend / max(days_elapsed, 1)
        projected = daily_rate * days_in_month
        return {
            'current_spend': round(current_spend, 2),
            'projected_spend': round(projected, 2),
            'lower_bound': round(projected * 0.9, 2),
            'upper_bound': round(projected * 1.1, 2),
            'days_elapsed': days_elapsed,
            'days_in_month': days_in_month
        }

    # Cumulative daily spend calculation
    month_df_copy = month_df.copy()
    month_df_copy['day'] = month_df_copy['date'].dt.day
    daily_spend = month_df_copy.groupby('day')['amount'].sum().reset_index()
    
    all_days = pd.DataFrame({'day': range(1, days_elapsed + 1)})
    daily_spend = pd.merge(all_days, daily_spend, on='day', how='left').fillna(0)
    daily_spend['cumulative_spend'] = daily_spend['amount'].cumsum()
    
    X = daily_spend['day'].values.reshape(-1, 1)
    y = daily_spend['cumulative_spend'].values
    
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)
    
    model = Ridge(alpha=1.0)
    model.fit(X_poly, y)
    
    X_future = np.array([[days_in_month]])
    X_future_poly = poly.transform(X_future)
    
    projected = float(model.predict(X_future_poly)[0])
    current_spend = float(daily_spend['cumulative_spend'].iloc[-1])
    
    # Projection cannot be less than actual spend
    projected = max(projected, current_spend)
    
    residuals = y - model.predict(X_poly)
    std_error = np.std(residuals) if len(residuals) > 1 else current_spend * 0.05
    margin = 1.96 * std_error * (days_in_month / days_elapsed)**0.5
    
    return {
        'current_spend': round(current_spend, 2),
        'projected_spend': round(projected, 2),
        'lower_bound': round(max(projected - margin, current_spend), 2),
        'upper_bound': round(projected + margin, 2),
        'days_elapsed': days_elapsed,
        'days_in_month': days_in_month
    }
