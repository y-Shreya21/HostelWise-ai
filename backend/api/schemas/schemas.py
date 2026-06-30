# HostelWise AI - Pydantic Validation Schemas
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount in INR")
    category: str = Field(..., description="High-level category (e.g. Food, Snacks, Travel)")
    subcategory: Optional[str] = Field("General", description="Detailed subcategory")
    description: Optional[str] = Field("No description", description="User notes or comments")
    payment_mode: Optional[str] = Field("UPI", description="UPI, Cash, Debit Card, Credit Card")
    date: Optional[str] = Field(None, description="ISO format date string. Defaults to current time.")

class Expense(BaseModel):
    expense_id: str
    student_id: str
    date: datetime
    amount: float
    category: str
    subcategory: str
    description: str
    payment_mode: str

class BudgetCreate(BaseModel):
    month_year: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Format: YYYY-MM")
    category: str = Field("ALL", description="Category name or 'ALL' for overall budget")
    allocated_amount: float = Field(..., gt=0, description="Allocated budget limit")

class ForecastResponse(BaseModel):
    predicted_spend: float
    lower_bound: float
    upper_bound: float
    model_type: str

class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str
    current_spend: float
    projected_spend: float
    budget_limit: float
    is_over_budget: bool

class Recommendation(BaseModel):
    category: str
    potential_savings: float
    recommendation_text: str

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []
    budget_limit: Optional[float] = 10000.0

class ChatResponse(BaseModel):
    response: str

class BenchmarkPoint(BaseModel):
    data_volume_rows: int
    cleaned_rows: int
    cpu_time_seconds: float
    gpu_time_seconds: float
    speedup: float

class BenchmarkSummary(BaseModel):
    gpu_detected: bool
    gpu_device_name: str
    timestamp: str
    benchmarks: List[BenchmarkPoint]
    average_speedup: float
    total_cpu_time_seconds: float
    total_gpu_time_seconds: float
    total_time_saved_seconds: float

class DashboardKPIs(BaseModel):
    total_expense: float
    avg_daily_spend: float
    highest_category: str
    highest_category_amount: float
    budget_utilization_pct: float

class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    category_spending: List[Dict]
    weekly_spending: List[Dict]
    daily_spending: List[Dict]
    payment_distribution: List[Dict]
    risk: RiskResponse
    recommendations: List[Recommendation]
