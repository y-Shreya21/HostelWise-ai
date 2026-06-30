# HostelWise AI - Forecasting API Routes
from fastapi import APIRouter, HTTPException, Query
from backend.api.schemas.schemas import ForecastResponse
from backend.services.expense_service import expense_service
from backend.services.forecast_service import forecast_service

router = APIRouter(tags=["forecasts"])

DEFAULT_STUDENT = "default_student"

@router.post("/forecast", response_model=ForecastResponse)
def predict_spending(
    student_id: str = Query(DEFAULT_STUDENT)
):
    """Generate next month's spending forecast using Ridge Regression."""
    df = expense_service.get_student_expenses_df(student_id)
    if len(df) == 0:
        raise HTTPException(status_code=404, detail="No expense history found to train forecasting model.")
        
    try:
        forecast = forecast_service.get_spending_predictions(df)
        return ForecastResponse(**forecast)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting calculation failed: {e}")
