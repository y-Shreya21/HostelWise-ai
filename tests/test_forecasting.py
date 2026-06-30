# HostelWise AI - Unit Tests for Forecasting Module
import unittest
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

class TestForecastingPipeline(unittest.TestCase):
    def setUp(self):
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
            
        self.sample_df = pd.DataFrame({
            'date': dates,
            'amount': amounts,
            'category': ['Food'] * 40,
            'subcategory': ['General'] * 40,
            'description': ['Test'] * 40,
            'payment_mode': ['UPI'] * 40
        })

    def test_model_training(self):
        """Test that the Ridge regression model fits and returns coefficients."""
        model, feature_names, std_error = train_forecasting_model(self.sample_df)
        
        self.assertIsNotNone(model)
        self.assertTrue(len(feature_names) > 0)
        self.assertTrue(std_error >= 0.0)
        self.assertTrue(hasattr(model, 'coef_'))

    def test_model_prediction(self):
        """Test that the prediction returns values within a reasonable range."""
        model, _, std_error = train_forecasting_model(self.sample_df)
        predictions = predict_next_month_spending(self.sample_df, model, std_error)
        
        self.assertIn('predicted_spend', predictions)
        self.assertIn('lower_bound', predictions)
        self.assertIn('upper_bound', predictions)
        self.assertTrue(predictions['predicted_spend'] > 0)
        self.assertTrue(predictions['lower_bound'] <= predictions['predicted_spend'] <= predictions['upper_bound'])

    def test_month_end_projection(self):
        """Test cumulative spending polynomial projection."""
        projection = predict_current_month_end(self.sample_df, budget_limit=15000.0)
        
        self.assertIn('current_spend', projection)
        self.assertIn('projected_spend', projection)
        self.assertTrue(projection['projected_spend'] >= projection['current_spend'])

    def test_model_evaluation(self):
        """Test backtesting and metrics evaluation."""
        eval_results = evaluate_forecasting_model(self.sample_df, test_size_days=10)
        
        self.assertEqual(eval_results['status'], 'SUCCESS')
        self.assertIn('metrics', eval_results)
        metrics = eval_results['metrics']
        self.assertIn('mean_absolute_error_inr', metrics)
        self.assertIn('root_mean_squared_error_inr', metrics)

if __name__ == '__main__':
    unittest.main()
