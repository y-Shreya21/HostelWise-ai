# HostelWise AI - Forecasting Business Service
import pandas as pd
from forecasting.train import train_forecasting_model
from forecasting.predict import predict_next_month_spending, predict_current_month_end

class ForecastService:
    def get_spending_predictions(self, df: pd.DataFrame) -> dict:
        """Run ML training and generate next month's spending forecast."""
        # Train model on the fly
        model, _, std_error = train_forecasting_model(df)
        
        # Run inference
        return predict_next_month_spending(df, model, std_error)

    def get_month_end_projection(self, df: pd.DataFrame, budget_limit: float, current_date=None) -> dict:
        """Run polynomial extrapolation on current month's cumulative spending."""
        return predict_current_month_end(df, budget_limit, current_date)

# Global forecast service instance
forecast_service = ForecastService()
