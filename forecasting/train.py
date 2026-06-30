# HostelWise AI - Model Training Pipeline
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from analytics.feature_engineering import build_features_for_forecasting

def train_forecasting_model(df: pd.DataFrame, alpha: float = 10.0) -> tuple:
    """
    Trains a Ridge Regression model on the historical spending data.
    Returns: (trained_model, feature_names, training_error_std)
    """
    # 1. Engineer features
    X, y, feature_names = build_features_for_forecasting(df)
    
    if len(X) == 0:
        return None, [], 0.0
        
    # 2. Fit Ridge Regression
    # We use Ridge (L2 regularization) to prevent overfitting on noisy daily student spend
    model = Ridge(alpha=alpha)
    model.fit(X, y)
    
    # 3. Calculate residuals and standard error
    predictions = model.predict(X)
    residuals = y - predictions
    std_error = float(np.std(residuals))
    
    print(f"Model trained successfully. Features: {feature_names}")
    print(f"Intercept: {model.intercept_:.2f} | Coefficients: {model.coef_}")
    print(f"Residual Std Error: {std_error:.2f} INR")
    
    return model, feature_names, std_error
