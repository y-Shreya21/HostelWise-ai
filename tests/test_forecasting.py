# HostelWise AI - Unit Tests for Forecasting Module
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import forecasting modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from forecasting.train import train_forecasting_model
from forecasting.predict import predict_next_month_spending, predict_current_month_end
from forecasting.evaluate import evaluate_forecasting_model

@pytest.fixture
def sample_spending_history():
    """Generate 40 days of synthetic spending history for testing."""
    start_date = datetime.now() - timedelta(days=40)
    dates = [start_date + timedelta(days=i) for i in range(40)]
    
    # Base spend of ₹200/day + weekend spikes of ₹300 + random noise
    amounts = []
    for dt in dates:
        base = 200.0
        weekend_spike = 300.0 if dt.weekday() >= 5 else 0.0
        noise = np.random.uniform(-50, 50)
        amounts.append(base + weekend_spike + noise)
        
    df = pd.DataFrame({
        'date': dates,
        'amount': amounts,
        'category': ['Food'] * 40,
        'subcategory': ['General'] * 40,
        'description': ['Test'] * 40,
        'payment_mode': ['UPI'] * 40
    })
    return df

def test_model_training(sample_spending_history):
    """Test that the Ridge regression model fits and returns coefficients."""
    model, feature_names, std_error = train_forecasting_model(sample_spending_history)
    
    assert model is not None
    assert len(feature_names) > 0
    assert std_error >= 0.0
    assert hasattr(model, 'coef_')

def test_model_prediction(sample_spending_history):
    """Test that the prediction returns values within a reasonable range."""
    model, _, std_error = train_forecasting_model(sample_spending_history)
    predictions = predict_next_month_spending(sample_spending_history, model, std_error)
    
    assert 'predicted_spend' in predictions
    assert 'lower_bound' in predictions
    assert 'upper_bound' in predictions
    assert predictions['predicted_spend'] > 0
    assert predictions['lower_bound'] <= predictions['predicted_spend'] <= predictions['upper_bound']

def test_month_end_projection(sample_spending_history):
    """Test cumulative spending polynomial projection."""
    projection = predict_current_month_end(sample_spending_history, budget_limit=15000.0)
    
    assert 'current_spend' in projection
    assert 'projected_spend' in projection
    assert projection['projected_spend'] >= projection['current_spend']

def test_model_evaluation(sample_spending_history):
    """Test backtesting and metrics evaluation."""
    eval_results = evaluate_forecasting_model(sample_spending_history, test_size_days=10)
    
    assert eval_results['status'] == 'SUCCESS'
    assert 'metrics' in eval_results
    metrics = eval_results['metrics']
    assert 'mean_absolute_error_inr' in metrics
    assert 'root_mean_squared_error_inr' in metrics
