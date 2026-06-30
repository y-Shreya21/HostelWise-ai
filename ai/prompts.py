# HostelWise AI - Chatbot Prompt Engineering
from typing import Dict
from datetime import datetime

SYSTEM_INSTRUCTION = """
You are HostelWise AI, a friendly, smart, and empathetic financial assistant for college students living in hostels and PG accommodations.
Your goal is to help students manage their money, understand their spending habits, and make smart saving decisions.
You are provided with the student's current financial data. Use this data to answer their questions accurately, giving practical, student-focused advice. 

Guidelines:
1. Keep your tone encouraging, conversational, and clear. Avoid complex financial jargon.
2. Use Indian Rupees (₹) as the currency.
3. Be realistic. If a student is at HIGH risk of exceeding their budget, gently warn them and suggest immediate, actionable cuts (e.g., swapping restaurant food for mess food).
4. If a student asks "Can I afford X?", evaluate it against their remaining budget (Budget Limit - Projected Spend). If they can't afford it, explain why and suggest how much they need to save.
5. Keep your responses relatively concise (150-250 words) so they are easy to read on a mobile dashboard.
"""

def build_financial_context_block(context: Dict) -> str:
    """Format the student's financial state into a semantic context block for the LLM."""
    kpis = context.get('kpis', {})
    risk = context.get('risk', {})
    forecast = context.get('forecast', {})
    categories = context.get('categories', [])
    recommendations = context.get('recommendations', [])
    
    current_month_str = datetime.now().strftime('%B %Y')
    
    category_str = "\n".join([f"- {c['category']}: ₹{c['amount']:,.2f}" for c in categories])
    recs_str = "\n".join([f"- [{r['category']}] {r['recommendation_text']} (Potential Savings: ₹{r['potential_savings']})" for r in recommendations])
    
    context_prompt = f"""
=== STUDENT FINANCIAL CONTEXT ({current_month_str}) ===
- Total Spent This Month: ₹{kpis.get('total_expense', 0):,.2f}
- Monthly Budget Limit: ₹{risk.get('budget_limit', 0):,.2f}
- Budget Spent Percentage: {kpis.get('budget_utilization_pct', 0)}%
- Average Daily Spend: ₹{kpis.get('avg_daily_spend', 0):,.2f}
- Highest Spending Category: {kpis.get('highest_category', 'N/A')} (₹{kpis.get('highest_category_amount', 0):,.2f})

=== FORECASTS & RISK ===
- Projected Month-End Spend: ₹{risk.get('projected_spend', 0):,.2f}
- Next Month Forecasted Spend: ₹{forecast.get('predicted_spend', 0):,.2f} (Range: ₹{forecast.get('lower_bound', 0)} - ₹{forecast.get('upper_bound', 0)})
- Budget Risk Score: {risk.get('risk_score', 0)}/100 ({risk.get('risk_level', 'LOW')} RISK)
- Projected Over-budget Status: {"YES (Alert: Budget Exceeded)" if risk.get('is_over_budget', False) else "NO (Within Budget)"}

=== CATEGORY-WISE SPENDING ===
{category_str}

=== ACTIVE SAVINGS RECOMMENDATIONS ===
{recs_str}
================================
"""
    return context_prompt
