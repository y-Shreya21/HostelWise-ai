# HostelWise AI - Savings Recommendations API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from backend.api.schemas.schemas import Recommendation
from backend.services.expense_service import expense_service
from backend.services.recommendation_service import recommendation_service

router = APIRouter(tags=["recommendations"])

DEFAULT_STUDENT = "default_student"

@router.post("/recommendations", response_model=List[Recommendation])
def get_recommendations(
    student_id: str = Query(DEFAULT_STUDENT),
    month_year: Optional[str] = None
):
    """Retrieve personalized savings recommendations based on spending aggregates."""
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
        
    df = expense_service.get_student_expenses_df(student_id)
    budget_limit = expense_service.get_student_budget(student_id, month_year, 'ALL')
    
    try:
        recs = recommendation_service.get_recommendations(df, budget_limit)
        return [Recommendation(**r) for r in recs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {e}")
