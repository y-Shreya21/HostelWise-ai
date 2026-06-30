# HostelWise AI - Streamlit Dashboard
import sys
import os
# Add parent directory to path to allow importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import requests
import io
import json
from datetime import datetime

# Import modular visualizations and UI blocks
from charts.plotly_charts import (
    create_category_donut_chart, create_payment_mode_bar_chart,
    create_weekly_trend_chart, create_forecast_projection_chart,
    create_benchmark_comparison_chart, create_daily_spend_trend_chart
)
from components.ui_blocks import (
    render_kpi_metrics, render_risk_card, render_recommendations_list
)

# Configure Page
st.set_page_config(
    page_title="HostelWise AI - Student Expense Intelligence",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Custom CSS for Premium Dark Theme and Glassmorphism
st.markdown("""
<style>
    .stApp {
        background-color: #080c16;
        color: #f3f4f6;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0b1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    div[data-testid="metric-container"] {
        background: rgba(20, 30, 55, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        background: rgba(28, 41, 75, 0.8);
        border-color: rgba(118, 185, 0, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: #9ca3af;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #f3f4f6;
        background-color: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(118, 185, 0, 0.15) !important;
        color: #76b900 !important;
        border-color: rgba(118, 185, 0, 0.3) !important;
        font-weight: bold;
    }
    
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        max-width: 80%;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    
    .chat-user {
        background-color: rgba(0, 176, 255, 0.12);
        border: 1px solid rgba(0, 176, 255, 0.2);
        color: #e0f2fe;
        margin-left: auto;
    }
    
    .chat-assistant {
        background-color: rgba(118, 185, 0, 0.12);
        border: 1px solid rgba(118, 185, 0, 0.2);
        color: #f0fdf4;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
<div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
    <div style="font-size: 40px;">💸</div>
    <div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 30%, #76b900 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            HOSTELWISE AI
        </h1>
        <p style="margin: 4px 0 0 0; color: #9ca3af; font-size: 0.95rem;">Smart Expense Intelligence System for Students</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper: Fetch data
@st.cache_data(ttl=5)
def get_dashboard_data():
    """Retrieve all aggregated metrics from backend, or fall back to local module execution."""
    try:
        response = requests.get(f"{BACKEND_URL}/dashboard?student_id=default_student", timeout=2)
        if response.status_code == 200:
            return response.json(), "API"
    except Exception:
        pass
        
    # LOCAL FALLBACK MODE
    try:
        from backend.services.expense_service import expense_service
        from backend.services.risk_service import risk_scoring_service
        from backend.services.recommendation_service import recommendation_service
        from analytics.engine import (
            get_basic_kpis, get_category_spending, get_weekly_spending, 
            get_daily_spending, get_payment_mode_distribution
        )
        
        df = expense_service.get_student_expenses_df("default_student")
        current_month = datetime.now().strftime('%Y-%m')
        budget = expense_service.get_student_budget("default_student", current_month)
        
        kpis = get_basic_kpis(df, budget)
        cat_df = get_category_spending(df)
        weekly_df = get_weekly_spending(df)
        daily_df = get_daily_spending(df)
        pay_df = get_payment_mode_distribution(df)
        risk = risk_scoring_service.calculate_multi_factor_risk(df, budget)
        recs = recommendation_service.get_recommendations(df, budget)
        
        if 'week' in weekly_df.columns:
            weekly_df['week'] = weekly_df['week'].dt.strftime('%Y-%m-%d')
        if 'day' in daily_df.columns:
            daily_df['day'] = daily_df['day'].dt.strftime('%Y-%m-%d')
            
        data = {
            "kpis": kpis,
            "category_spending": cat_df.to_dict(orient='records'),
            "weekly_spending": weekly_df.to_dict(orient='records'),
            "daily_spending": daily_df.to_dict(orient='records'),
            "payment_distribution": pay_df.to_dict(orient='records'),
            "risk": risk,
            "recommendations": recs
        }
        return data, "Local"
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, "Error"

data, mode = get_dashboard_data()

# Sidebar Integration Info
st.sidebar.markdown("### System Integration")
if mode == "API":
    st.sidebar.success("🔗 Connected to FastAPI Server")
elif mode == "Local":
    st.sidebar.warning("⚠️ Local Integration Active")
else:
    st.sidebar.error("❌ Connection Failed")
st.sidebar.markdown("---")

# Quick Expense Entry
st.sidebar.markdown("### Quick Expense Entry")
with st.sidebar.form("quick_expense"):
    amount = st.number_input("Amount (₹)", min_value=1.0, step=50.0)
    category = st.selectbox("Category", ['Food', 'Snacks', 'Travel', 'Shopping', 'Recharge', 'Entertainment', 'Medical', 'Education', 'Other'])
    subcategory = st.text_input("Subcategory", "General")
    description = st.text_input("Description", "Spent at canteen")
    payment_mode = st.selectbox("Payment Mode", ['UPI', 'Cash', 'Debit Card', 'Credit Card'])
    
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        success = False
        if mode == "API":
            try:
                res = requests.post(f"{BACKEND_URL}/expense?student_id=default_student", json={
                    "amount": amount,
                    "category": category,
                    "subcategory": subcategory,
                    "description": description,
                    "payment_mode": payment_mode
                })
                if res.status_code == 200:
                    success = True
            except Exception:
                pass
        if not success:
            try:
                from backend.services.expense_service import expense_service
                expense_service.add_single_expense("default_student", amount, category, subcategory, description, payment_mode)
                success = True
            except Exception as e:
                st.sidebar.error(f"Failed to add: {e}")
                
        if success:
            st.sidebar.success("Expense added! Reloading...")
            st.cache_data.clear()
            st.rerun()

# Upload Expense CSV
st.sidebar.markdown("### Upload Expense CSV")
uploaded_file = st.sidebar.file_uploader("Choose CSV File", type=['csv'])
if uploaded_file is not None:
    if st.sidebar.button("Process Upload"):
        success = False
        file_bytes = uploaded_file.getvalue()
        if mode == "API":
            try:
                files = {"file": (uploaded_file.name, file_bytes, "text/csv")}
                data_form = {"student_id": "default_student"}
                res = requests.post(f"{BACKEND_URL}/upload", files=files, data=data_form)
                if res.status_code == 200:
                    st.sidebar.success(f"Processed: {res.json()['records_imported']} records imported.")
                    success = True
            except Exception as e:
                st.sidebar.error(f"API upload failed: {e}")
        if not success:
            try:
                from backend.services.expense_service import expense_service
                from analytics.clean import clean_expense_data
                df_raw = pd.read_csv(io.BytesIO(file_bytes))
                cleaned_df = clean_expense_data(df_raw, use_gpu=False)
                expense_service.load_bulk_data("default_student", cleaned_df)
                st.sidebar.success(f"Processed locally: {len(cleaned_df)} records imported.")
                success = True
            except Exception as e:
                st.sidebar.error(f"Local upload failed: {e}")
                
        if success:
            st.cache_data.clear()
            st.rerun()

if data:
    kpis = data['kpis']
    risk = data['risk']
    recs = data['recommendations']
    
    # Define tabs
    tab_overview, tab_analytics, tab_forecasting, tab_risk, tab_chat, tab_benchmarks = st.tabs([
        "📊 Overview", 
        "📈 Expense Analytics", 
        "🔮 ML Spending Forecast", 
        "🛡️ Risk & Recommendations", 
        "🤖 Gemini AI Advisor", 
        "⚡ RAPIDS Performance"
    ])
    
    # ------------------------------------------------------------------------
    # TAB 1: OVERVIEW
    # ------------------------------------------------------------------------
    with tab_overview:
        # Render top KPI metrics
        render_kpi_metrics(kpis, risk)
        
        # Budget Progress
        st.markdown("### Budget Progress")
        util_pct = kpis['budget_utilization_pct']
        progress_val = min(util_pct / 100.0, 1.0)
        st.progress(progress_val)
        
        gcol1, gcol2 = st.columns([3, 2])
        
        with gcol1:
            st.markdown("### Daily Spend Trend")
            daily_df = pd.DataFrame(data['daily_spending'])
            if not daily_df.empty:
                fig = create_daily_spend_trend_chart(daily_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No transaction data available yet.")
                
        with gcol2:
            st.markdown("### Adjust Budget Limit")
            current_budget = risk['budget_limit']
            new_budget = st.number_input("Set Monthly Limit (₹)", min_value=1000.0, max_value=100000.0, value=float(current_budget), step=1000.0)
            if st.button("Update Budget"):
                success = False
                month_str = datetime.now().strftime('%Y-%m')
                if mode == "API":
                    try:
                        res = requests.post(f"{BACKEND_URL}/budget?student_id=default_student", json={
                            "month_year": month_str,
                            "category": "ALL",
                            "allocated_amount": new_budget
                        })
                        if res.status_code == 200:
                            success = True
                    except Exception:
                        pass
                if not success:
                    try:
                        from backend.services.expense_service import expense_service
                        expense_service.set_student_budget("default_student", month_str, "ALL", new_budget)
                        success = True
                    except Exception as e:
                        st.error(f"Failed to update budget: {e}")
                        
                if success:
                    st.success("Budget updated!")
                    st.cache_data.clear()
                    st.rerun()

            # Recent transactions list
            st.markdown("### Recent Transactions")
            try:
                from backend.services.expense_service import expense_service
                df_raw = expense_service.get_student_expenses_df("default_student")
                if not df_raw.empty:
                    st.dataframe(
                        df_raw[['date', 'amount', 'category', 'subcategory', 'description', 'payment_mode']].head(5),
                        use_container_width=True
                    )
            except Exception:
                st.text("Could not load transactions.")

    # ------------------------------------------------------------------------
    # TAB 2: EXPENSE ANALYTICS
    # ------------------------------------------------------------------------
    with tab_analytics:
        st.markdown("## Multi-dimensional Spending Insights")
        acol1, acol2 = st.columns(2)
        
        with acol1:
            cat_df = pd.DataFrame(data['category_spending'])
            fig_pie = create_category_donut_chart(cat_df)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No category data.")
                
        with acol2:
            pay_df = pd.DataFrame(data['payment_distribution'])
            fig_bar = create_payment_mode_bar_chart(pay_df)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No payment data.")
                
        st.markdown("### Weekly Aggregates")
        weekly_df = pd.DataFrame(data['weekly_spending'])
        fig_week = create_weekly_trend_chart(weekly_df)
        if fig_week:
            st.plotly_chart(fig_week, use_container_width=True)
        else:
            st.info("No weekly data.")

    # ------------------------------------------------------------------------
    # TAB 3: ML SPENDING FORECAST
    # ------------------------------------------------------------------------
    with tab_forecasting:
        st.markdown("## Spending Forecasts & Predictive Modeling")
        fcol1, fcol2 = st.columns([1, 2])
        
        forecast = None
        if mode == "API":
            try:
                res = requests.post(f"{BACKEND_URL}/forecast?student_id=default_student")
                if res.status_code == 200:
                    forecast = res.json()
            except Exception:
                pass
        if not forecast:
            try:
                from backend.services.expense_service import expense_service
                from backend.services.forecast_service import forecast_service
                df_history = expense_service.get_student_expenses_df("default_student")
                forecast = forecast_service.get_spending_predictions(df_history)
            except Exception as e:
                st.error(f"Could not run forecast: {e}")
                
        with fcol1:
            st.markdown("### Next Month Forecast")
            if forecast:
                st.markdown(f"""
                <div style="background: rgba(118, 185, 0, 0.08); border: 1px solid rgba(118, 185, 0, 0.3); border-radius: 12px; padding: 20px; margin-top: 16px;">
                    <h4 style="margin: 0; color: var(--nvidia-green); font-size: 1.1rem;">Predicted Total Spend</h4>
                    <div style="font-size: 36px; font-weight: 800; margin: 10px 0; color: #fff;">
                        ₹{forecast['predicted_spend']:,.2f}
                    </div>
                    <p style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0;">
                        Confidence Range (95%):<br/>
                        <b>₹{forecast['lower_bound']:,.2f} - ₹{forecast['upper_bound']:,.2f}</b>
                    </p>
                    <p style="font-size: 0.75rem; color: #64748b; margin-top: 12px; font-family: monospace;">
                        Model: {forecast['model_type']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Forecasting requires at least 15 days of historical transactions.")
                
        with fcol2:
            st.markdown("### Cumulative Spending Projection")
            try:
                from backend.services.expense_service import expense_service
                df_exp = expense_service.get_student_expenses_df("default_student")
                current_budget = risk['budget_limit']
                
                current_date = datetime.now()
                start_of_month = pd.Timestamp(current_date.year, current_date.month, 1)
                end_of_day = pd.Timestamp(current_date.year, current_date.month, current_date.day, 23, 59, 59)
                month_df = df_exp[(df_exp['date'] >= start_of_month) & (df_exp['date'] <= end_of_day)]
                
                if len(month_df) > 0:
                    month_df['day'] = month_df['date'].dt.day
                    daily_cum = month_df.groupby('day')['amount'].sum().reset_index()
                    days_in_month = pd.Period(datetime.now().strftime('%Y-%m')).days_in_month
                    
                    full_days = pd.DataFrame({'day': range(1, datetime.now().day + 1)})
                    daily_cum = pd.merge(full_days, daily_cum, on='day', how='left').fillna(0)
                    daily_cum['cumulative'] = daily_cum['amount'].cumsum()
                    
                    days_elapsed = len(daily_cum)
                    current_spent = daily_cum['cumulative'].iloc[-1]
                    daily_rate = current_spent / days_elapsed
                    
                    projection_days = list(range(1, days_in_month + 1))
                    projected_line = [daily_rate * d for d in projection_days]
                    
                    # Use modular Plotly projection chart
                    fig_forecast = create_forecast_projection_chart(
                        daily_cum, current_budget, days_in_month, 
                        projected_line, projection_days
                    )
                    st.plotly_chart(fig_forecast, use_container_width=True)
                else:
                    st.info("No spending recorded in the current month.")
            except Exception as e:
                st.error(f"Could not generate cumulative plot: {e}")

    # ------------------------------------------------------------------------
    # TAB 4: RISK & RECOMMENDATIONS
    # ------------------------------------------------------------------------
    with tab_risk:
        st.markdown("## Budget Safety & Savings Recommendations")
        rcol1, rcol2 = st.columns([1, 2])
        
        with rcol1:
            # Render styled risk card
            render_risk_card(risk)
            
        with rcol2:
            st.markdown("### Actionable Savings Recommendations")
            # Render savings recommendations list
            render_recommendations_list(recs)

    # ------------------------------------------------------------------------
    # TAB 5: GEMINI AI ADVISOR
    # ------------------------------------------------------------------------
    with tab_chat:
        st.markdown("## Gemini AI Financial Assistant")
        st.markdown("Ask Gemini questions about your spending habits, budget forecasts, or purchase decisions.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Quick Inquiries
        st.markdown("**Quick Inquiries:**")
        chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
        quick_query = None
        
        if chip_col1.button("Where am I overspending?"):
            quick_query = "Where am I overspending?"
        if chip_col2.button("Can I afford a ₹1500 purchase?"):
            quick_query = "Can I afford a ₹1500 purchase this month?"
        if chip_col3.button("Summarize my spending habits"):
            quick_query = "Summarize my spending habits."
        if chip_col4.button("How much should I save next month?"):
            quick_query = "How much should I save next month?"

        # Chat history container
        chat_container = st.container(border=True, height=350)
        with chat_container:
            for message in st.session_state.messages:
                bubble_class = "chat-user" if message["role"] == "user" else "chat-assistant"
                formatted_content = message["content"].replace('\n', '<br/>')
                st.markdown(f"""
                <div class="chat-bubble {bubble_class}">
                    <b>{"You" if message["role"] == "user" else "Gemini Advisor"}:</b><br/>
                    {formatted_content}
                </div>
                """, unsafe_allow_html=True)

        user_input = st.chat_input("Ask a financial question...")
        if quick_query:
            user_input = quick_query

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with chat_container:
                st.markdown(f"""
                <div class="chat-bubble chat-user">
                    <b>You:</b><br/>
                    {user_input}
                </div>
                """, unsafe_allow_html=True)
                
            api_success = False
            ai_response = ""
            if mode == "API":
                try:
                    history_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    res = requests.post(f"{BACKEND_URL}/chat?student_id=default_student", json={
                        "query": user_input,
                        "history": history_payload,
                        "budget_limit": float(risk['budget_limit'])
                    })
                    if res.status_code == 200:
                        ai_response = res.json()["response"]
                        api_success = True
                except Exception as e:
                    st.error(f"API chat error: {e}")
                    
            if not api_success:
                try:
                    from ai.chatbot import chatbot
                    from backend.services.expense_service import expense_service
                    from backend.services.risk_service import risk_scoring_service
                    from backend.services.recommendation_service import recommendation_service
                    from backend.services.forecast_service import forecast_service
                    from analytics.engine import get_basic_kpis, get_category_spending
                    
                    df_exp = expense_service.get_student_expenses_df("default_student")
                    curr_budget = risk['budget_limit']
                    
                    financial_context = {
                        'kpis': get_basic_kpis(df_exp, curr_budget),
                        'risk': risk_scoring_service.calculate_multi_factor_risk(df_exp, curr_budget),
                        'forecast': forecast_service.get_spending_predictions(df_exp),
                        'categories': get_category_spending(df_exp).to_dict(orient='records'),
                        'recommendations': recommendation_service.get_recommendations(df_exp, curr_budget)
                    }
                    
                    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                    ai_response = chatbot.get_chat_response(user_input, hist, financial_context)
                except Exception as ex:
                    ai_response = f"Sorry, I encountered an error running locally: {ex}"
                    
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
            
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # ------------------------------------------------------------------------
    # TAB 6: RAPIDS PERFORMANCE BENCHMARKS
    # ------------------------------------------------------------------------
    with tab_benchmarks:
        st.markdown("## NVIDIA RAPIDS cuDF vs. CPU Pandas Acceleration")
        st.markdown("Measure the execution speedup when processing large student expense datasets on GPU cores using NVIDIA cuDF compared to traditional CPU-bound Pandas.")
        
        bcol1, bcol2 = st.columns([1, 2])
        
        benchmark_data = None
        benchmark_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'benchmark', 'performance_summary.json')
        
        if os.path.exists(benchmark_json_path):
            with open(benchmark_json_path, 'r') as f:
                benchmark_data = json.load(f)
                
        with bcol1:
            st.markdown("### Run New Benchmark")
            st.info("Warning: Generating 1.6 million rows and running both pipelines takes approximately 10-15 seconds on CPU.")
            
            if st.button("🚀 Run RAPIDS Benchmark Suite"):
                with st.spinner("Running benchmarks on 100K, 500K, and 1M rows..."):
                    success = False
                    if mode == "API":
                        try:
                            res = requests.get(f"{BACKEND_URL}/benchmark")
                            if res.status_code == 200:
                                benchmark_data = res.json()
                                success = True
                        except Exception:
                            pass
                    if not success:
                        try:
                            from benchmark.compare import execute_benchmark_comparison
                            benchmark_data = execute_benchmark_comparison()
                            success = True
                        except Exception as e:
                            st.error(f"Failed to run benchmark: {e}")
                            
                    if success:
                        st.success("Benchmark completed successfully!")
                        st.rerun()
            
            if benchmark_data:
                gpu_tag = "ACTIVE" if benchmark_data['gpu_detected'] else "SIMULATED (No GPU)"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 16px; margin-top: 16px;">
                    <h5 style="margin: 0; color: var(--nvidia-green);">Benchmark System Specs</h5>
                    <p style="margin: 8px 0 0 0; font-size: 0.85rem; color: #9ca3af;">
                        GPU: <b>{benchmark_data['gpu_device_name']}</b><br/>
                        Status: <b>{gpu_tag}</b><br/>
                        Average Speedup: <b style="color: #76b900; font-size: 1.1rem;">{benchmark_data['average_speedup']}x Faster</b><br/>
                        Total Time Saved: <b>{benchmark_data['total_time_saved_seconds']:.2f} seconds</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
        with bcol2:
            st.markdown("### Performance Comparison")
            if benchmark_data:
                bench_df = pd.DataFrame(benchmark_data['benchmarks'])
                # Use modular Plotly chart
                fig_bench = create_benchmark_comparison_chart(bench_df)
                st.plotly_chart(fig_bench, use_container_width=True)
                
                st.dataframe(
                    bench_df[['data_volume_rows', 'cpu_time_seconds', 'gpu_time_seconds', 'speedup']],
                    use_container_width=True
                )
            else:
                st.info("No benchmark results found. Click the button on the left to execute the benchmark.")
else:
    st.error("No data could be retrieved.")
