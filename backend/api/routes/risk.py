# HostelWise AI - Budget Risk API Routes
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from backend.api.schemas.schemas import RiskResponse
from backend.services.expense_service import expense_service
from backend.services.risk_service import risk_scoring_service

router = APIRouter(tags=["risk"])

DEFAULT_STUDENT = "default_student"

@router.post("/risk", response_model=RiskResponse)
def calculate_risk(
    student_id: str = Query(DEFAULT_STUDENT),
    month_year: Optional[str] = None
):
    """Calculate the multi-factor budget risk score (0-100) and risk level."""
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
        
    df = expense_service.get_student_expenses_df(student_id)
    budget_limit = expense_service.get_student_budget(student_id, month_year, 'ALL')
    
    try:
        risk = risk_scoring_service.calculate_multi_factor_risk(df, budget_limit)
        return RiskResponse(**risk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk scoring calculation failed: {e}")
