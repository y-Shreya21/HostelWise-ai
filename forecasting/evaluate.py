# HostelWise AI - Model Evaluation Pipeline
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from analytics.feature_engineering import build_features_for_forecasting
from sklearn.linear_model import Ridge

def evaluate_forecasting_model(df: pd.DataFrame, test_size_days: int = 30) -> dict:
    """
    Evaluates the model by training on historical data (minus test_size_days)
    and testing on the most recent test_size_days.
    Calculates MAE, MSE, RMSE, and R2 score.
    """
    X, y, _ = build_features_for_forecasting(df)
    
    if len(X) < (test_size_days + 10):
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"Requires at least {test_size_days + 10} days of history to evaluate. Current history: {len(X)} days."
        }
        
    # Split into train/test (chronological split for time-series)
    X_train, X_test = X[:-test_size_days], X[-test_size_days:]
    y_train, y_test = y[:-test_size_days], y[-test_size_days:]
    
    # Train model
    model = Ridge(alpha=10.0)
    model.fit(X_train, y_train)
    
    # Predict on test set
    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)  # No negative spending predictions
    
    # Calculate metrics
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    
    # R2 score can be negative if the model is worse than the baseline mean
    r2 = float(r2_score(y_test, y_pred))
    
    # Mean spending in test set (for percentage error calculation)
    mean_actual = float(np.mean(y_test))
    mape = float(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1.0)))) * 100
    
    return {
        "status": "SUCCESS",
        "metrics": {
            "mean_absolute_error_inr": round(mae, 2),
            "mean_squared_error": round(mse, 2),
            "root_mean_squared_error_inr": round(rmse, 2),
            "r2_score": round(r2, 4),
            "mean_actual_daily_spend_inr": round(mean_actual, 2),
            "mean_absolute_percentage_error_pct": round(mape, 2)
        },
        "test_days": test_size_days,
        "training_days": len(X_train)
    }
