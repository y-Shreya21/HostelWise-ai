# HostelWise AI - Expense Management API Routes
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
import pandas as pd
import io
from datetime import datetime
from typing import Optional

from backend.api.schemas.schemas import ExpenseCreate, BudgetCreate, DashboardResponse, DashboardKPIs, RiskResponse, Recommendation
from backend.services.expense_service import expense_service
from backend.services.risk_service import risk_scoring_service
from backend.services.recommendation_service import recommendation_service
from backend.services.forecast_service import forecast_service
from cloud.storage import gcs_manager
from analytics.clean import clean_expense_data
from analytics.engine import (
    get_basic_kpis, get_category_spending, get_weekly_spending, 
    get_daily_spending, get_payment_mode_distribution
)

router = APIRouter(tags=["expenses"])

DEFAULT_STUDENT = "default_student"

@router.post("/upload", response_model=dict)
async def upload_expenses_file(
    file: UploadFile = File(...),
    student_id: str = Form(DEFAULT_STUDENT)
):
    """Upload a raw CSV expense file, clean it, and load it into SQLite + BigQuery."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    try:
        contents = await file.read()
        
        # 1. Archive raw file in GCS / Local Uploads
        _ = gcs_manager.upload_file(
            contents, 
            f"raw/{student_id}_{int(datetime.now().timestamp())}_{file.filename}"
        )
        
        # 2. Ingest and Clean Data (ETL)
        df_raw = pd.read_csv(io.BytesIO(contents))
        cleaned_df = clean_expense_data(df_raw, use_gpu=False)
        
        if len(cleaned_df) == 0:
            raise HTTPException(status_code=400, detail="No valid transactions found in CSV.")
            
        # 3. Save to databases
        inserted_count = expense_service.load_bulk_data(student_id, cleaned_df)
        
        return {
            "message": "File processed and imported successfully.",
            "records_imported": inserted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {e}")

@router.post("/expense", response_model=dict)
def add_manual_expense(
    expense: ExpenseCreate,
    student_id: str = Query(DEFAULT_STUDENT)
):
    """Manually record a single student transaction."""
    try:
        record = expense_service.add_single_expense(
            student_id=student_id,
            amount=expense.amount,
            category=expense.category,
            subcategory=expense.subcategory,
            description=expense.description,
            payment_mode=expense.payment_mode,
            date_str=expense.date
        )
        return {"message": "Expense recorded successfully.", "expense": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget", response_model=dict)
def set_budget(
    budget: BudgetCreate,
    student_id: str = Query(DEFAULT_STUDENT)
):
    """Configure or update a monthly budget limit."""
    try:
        expense_service.set_student_budget(
            student_id=student_id,
            month_year=budget.month_year,
            category=budget.category,
            amount=budget.allocated_amount
        )
        return {"message": "Budget configured successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_summary(
    student_id: str = Query(DEFAULT_STUDENT),
    month_year: Optional[str] = None
):
    """Fetch all aggregated stats and predictions for the frontend dashboard in a single call."""
    if not month_year:
        month_year = datetime.now().strftime('%Y-%m')
        
    try:
        df = expense_service.get_student_expenses_df(student_id)
        budget_limit = expense_service.get_student_budget(student_id, month_year, 'ALL')
        
        # Aggregations
        kpis = get_basic_kpis(df, budget_limit)
        cat_df = get_category_spending(df)
        weekly_df = get_weekly_spending(df)
        daily_df = get_daily_spending(df)
        pay_df = get_payment_mode_distribution(df)
        
        # Predictions
        risk = risk_scoring_service.calculate_multi_factor_risk(df, budget_limit)
        recs = recommendation_service.get_recommendations(df, budget_limit)
        
        # Date formatting for JSON compatibility
        if 'week' in weekly_df.columns:
            weekly_df['week'] = pd.to_datetime(weekly_df['week']).dt.strftime('%Y-%m-%d')
        if 'day' in daily_df.columns:
            daily_df['day'] = pd.to_datetime(daily_df['day']).dt.strftime('%Y-%m-%d')
            
        return DashboardResponse(
            kpis=DashboardKPIs(**kpis),
            category_spending=cat_df.to_dict(orient='records'),
            weekly_spending=weekly_df.to_dict(orient='records'),
            daily_spending=daily_df.to_dict(orient='records'),
            payment_distribution=pay_df.to_dict(orient='records'),
            risk=RiskResponse(**risk),
            recommendations=[Recommendation(**r) for r in recs]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard aggregation failed: {e}")
