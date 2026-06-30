# HostelWise AI - Gemini Chatbot API Routes
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from backend.api.schemas.schemas import ChatRequest, ChatResponse
from backend.services.expense_service import expense_service
from backend.services.risk_service import risk_scoring_service
from backend.services.recommendation_service import recommendation_service
from backend.services.forecast_service import forecast_service
from analytics.engine import get_basic_kpis, get_category_spending
from ai.chatbot import chatbot

router = APIRouter(tags=["chat"])

DEFAULT_STUDENT = "default_student"

@router.post("/chat", response_model=ChatResponse)
def chat_with_advisor(
    request: ChatRequest,
    student_id: str = Query(DEFAULT_STUDENT)
):
    """Chat with the Gemini AI Financial Assistant using student context."""
    df = expense_service.get_student_expenses_df(student_id)
    
    # Gather financial context
    current_month_str = datetime.now().strftime('%Y-%m')
    budget_limit = expense_service.get_student_budget(student_id, current_month_str, 'ALL')
    
    kpis = get_basic_kpis(df, budget_limit)
    categories = get_category_spending(df).to_dict(orient='records')
    risk = risk_scoring_service.calculate_multi_factor_risk(df, budget_limit)
    forecast = forecast_service.get_spending_predictions(df)
    recs = recommendation_service.get_recommendations(df, budget_limit)
    
    financial_context = {
        'kpis': kpis,
        'risk': risk,
        'forecast': forecast,
        'categories': categories,
        'recommendations': recs
    }
    
    # Convert history models to dicts
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    try:
        response_text = chatbot.get_chat_response(
            query=request.query,
            chat_history=history_dicts,
            financial_context=financial_context
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Chat failed: {e}")
