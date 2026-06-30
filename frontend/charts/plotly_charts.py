# HostelWise AI - Plotly Visualization Module
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_category_donut_chart(cat_df: pd.DataFrame):
    """Render a donut chart of spending by category."""
    if cat_df.empty:
        return None
    fig = px.pie(
        cat_df, values='amount', names='category',
        title="Expenses by Category",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6')
    )
    return fig

def create_payment_mode_bar_chart(pay_df: pd.DataFrame):
    """Render a bar chart of spending by payment mode."""
    if pay_df.empty:
        return None
    fig = px.bar(
        pay_df, x='payment_mode', y='amount',
        title="Spending by Payment Mode",
        labels={'payment_mode': 'Method', 'amount': 'Total (₹)'},
        color='payment_mode',
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6'),
        showlegend=False
    )
    return fig

def create_weekly_trend_chart(weekly_df: pd.DataFrame):
    """Render a bar chart showing weekly spending trends."""
    if weekly_df.empty:
        return None
    weekly_df['week'] = pd.to_datetime(weekly_df['week'])
    fig = px.bar(
        weekly_df, x='week', y='amount',
        title="Weekly Spending Velocity",
        labels={'week': 'Week Starting', 'amount': 'Amount (₹)'},
        template="plotly_dark"
    )
    fig.update_traces(marker_color='#00b0ff')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6')
    )
    return fig

def create_forecast_projection_chart(daily_cum: pd.DataFrame, current_budget: float, days_in_month: int, projected_line: list, projection_days: list):
    """Render the cumulative spending projection vs. budget limit."""
    fig = go.Figure()
    
    # Historical cumulative spend
    fig.add_trace(go.Scatter(
        x=daily_cum['day'], y=daily_cum['cumulative'],
        mode='lines+markers', name='Actual Cumulative Spend',
        line=dict(color='#00b0ff', width=3),
        marker=dict(size=6)
    ))
    
    # Projected path
    fig.add_trace(go.Scatter(
        x=projection_days, y=projected_line,
        mode='lines', name='Linear Projection',
        line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dash')
    ))
    
    # Budget Limit Line
    fig.add_trace(go.Scatter(
        x=[1, days_in_month], y=[current_budget, current_budget],
        mode='lines', name='Budget Limit',
        line=dict(color='#ff1744', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title="Month-End Budget Tracking",
        xaxis_title="Day of Month",
        yaxis_title="Cumulative Spent (₹)",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6')
    )
    return fig

def create_benchmark_comparison_chart(bench_df: pd.DataFrame):
    """Render a bar chart comparing CPU Pandas vs. GPU cuDF performance."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bench_df['data_volume_rows'].apply(lambda x: f"{x//1000}K"),
        y=bench_df['cpu_time_seconds'],
        name='CPU (Pandas)',
        marker_color='rgba(148, 163, 184, 0.6)'
    ))
    fig.add_trace(go.Bar(
        x=bench_df['data_volume_rows'].apply(lambda x: f"{x//1000}K"),
        y=bench_df['gpu_time_seconds'],
        name='GPU (cuDF RAPIDS)',
        marker_color='#76b900'
    ))
    fig.update_layout(
        title="Execution Time (Seconds) - Lower is Better",
        xaxis_title="Data Scale (Number of Rows)",
        yaxis_title="Processing Time (Seconds)",
        barmode='group',
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6')
    )
    return fig

def create_daily_spend_trend_chart(daily_df: pd.DataFrame):
    """Render a line chart of daily transaction velocity."""
    if daily_df.empty:
        return None
    daily_df['day'] = pd.to_datetime(daily_df['day'])
    fig = px.line(
        daily_df, x='day', y='amount', 
        title="Daily Transactions Velocity",
        labels={'day': 'Date', 'amount': 'Spent (₹)'},
        template="plotly_dark"
    )
    fig.update_traces(line_color='#76b900', line_width=2.5)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#f3f4f6')
    )
    return fig
