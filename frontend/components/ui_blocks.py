# HostelWise AI - UI Component Layout Blocks
import streamlit as st
from typing import List, Dict

def render_kpi_metrics(kpis: Dict, risk: Dict):
    """Render the top metric card row in the Overview tab."""
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        label="Total Spending (Month)", 
        value=f"₹{kpis['total_expense']:,.2f}", 
        help="Total amount spent in the current month."
    )
    col2.metric(
        label="Daily Average", 
        value=f"₹{kpis['avg_daily_spend']:,.2f}", 
        help="Average daily spending velocity."
    )
    
    util_pct = kpis['budget_utilization_pct']
    if util_pct > 100:
        status_text = "OVER BUDGET"
    elif util_pct > 75:
        status_text = "WARNING"
    else:
        status_text = "SAFE"
        
    col3.metric(
        label="Budget Utilization", 
        value=f"{util_pct}%", 
        delta=status_text, 
        delta_color="inverse"
    )
    
    col4.metric(
        label="Top Category", 
        value=kpis['highest_category'], 
        delta=f"₹{kpis['highest_category_amount']:,.2f}"
    )

def render_risk_card(risk: Dict):
    """Render a styled risk score card with visual alerts."""
    score = risk['risk_score']
    level = risk['risk_level']
    
    color_map = {
        'LOW': '#00e676',
        'MEDIUM': '#ffb300',
        'HIGH': '#ff1744'
    }
    border_color = color_map.get(level, '#fff')
    
    st.markdown(f"""
    <div style="text-align: center; background: rgba(20, 30, 55, 0.65); border: 2px solid {border_color}; border-radius: 12px; padding: 30px; margin-top: 16px;">
        <h4 style="margin: 0; color: #9ca3af; font-size: 0.9rem; text-transform: uppercase;">Risk Level</h4>
        <h2 style="margin: 5px 0; color: {border_color}; font-size: 28px; font-weight: 800;">{level} RISK</h2>
        <div style="font-size: 56px; font-weight: 900; color: #fff; margin: 15px 0; font-family: monospace;">
            {score}<span style="font-size: 20px; color: #64748b;">/100</span>
        </div>
        <p style="color: #9ca3af; font-size: 0.85rem; margin: 0; line-height: 1.4;">
            Projected Month-End Spend: <b>₹{risk['projected_spend']:,.2f}</b><br/>
            Budget Limit: <b>₹{risk['budget_limit']:,.2f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if level == 'HIGH':
        st.error("🚨 ALERT: You are projected to exceed your monthly budget limit. Please review the recommendations on the right to reduce spending.")
    elif level == 'MEDIUM':
        st.warning("⚠️ WARNING: You are approaching your budget limit. Swapping a few luxury spends for cheaper alternatives is recommended.")
    else:
        st.success("✅ SAFE: Your current spending rate is well within your monthly budget limits.")

def render_recommendations_list(recs: List[Dict]):
    """Render savings recommendation cards."""
    if not recs:
        st.info("No specific recommendations. Your spending habits are highly optimized!")
        return
        
    for rec in recs:
        cat = rec['category']
        savings_amt = rec['potential_savings']
        text = rec['recommendation_text']
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid #76b900; border-radius: 8px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1; padding-right: 20px;">
                <span style="font-weight: 800; color: #76b900; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">{cat} Savings Option</span>
                <p style="margin: 6px 0 0 0; color: #f3f4f6; font-size: 0.9rem; line-height: 1.4;">{text}</p>
            </div>
            <div style="text-align: right; min-width: 110px;">
                <span style="font-size: 0.7rem; color: #9ca3af; text-transform: uppercase;">Save Up To</span>
                <div style="font-size: 1.25rem; font-weight: 800; color: #00e676;">₹{savings_amt:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
