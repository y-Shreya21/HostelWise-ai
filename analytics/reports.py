# HostelWise AI - Spending Report Generator
import pandas as pd
from datetime import datetime
from .engine import get_basic_kpis, get_category_spending

def generate_monthly_markdown_report(df: pd.DataFrame, budget_limit: float = 10000.0) -> str:
    """Generate a clean, markdown-formatted financial report for the student."""
    if len(df) == 0:
        return "### HostelWise AI Financial Report\nNo transactions recorded for the current period."

    kpis = get_basic_kpis(df, budget_limit)
    cat_df = get_category_spending(df)
    
    report = []
    report.append(f"# HostelWise Financial Report - {datetime.now().strftime('%B %Y')}")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report.append("## Executive Summary")
    report.append(f"- **Total Spending**: ₹{kpis['total_expense']:,.2f}")
    report.append(f"- **Monthly Budget Limit**: ₹{budget_limit:,.2f}")
    report.append(f"- **Budget Utilization**: {kpis['budget_utilization_pct']}%")
    report.append(f"- **Average Daily Spend**: ₹{kpis['avg_daily_spend']:,.2f}")
    report.append(f"- **Primary Expense Category**: **{kpis['highest_category']}** (₹{kpis['highest_category_amount']:,.2f})\n")
    
    report.append("## Category Breakdown")
    report.append("| Category | Amount Spent (₹) | % of Total |")
    report.append("| :--- | :--- | :--- |")
    
    total_amt = kpis['total_expense']
    for _, row in cat_df.iterrows():
        pct = (row['amount'] / total_amt) * 100 if total_amt > 0 else 0
        report.append(f"| {row['category']} | ₹{row['amount']:,.2f} | {pct:.1f}% |")
        
    report.append("\n## Key Insights")
    # Check for specific overspending patterns
    if kpis['budget_utilization_pct'] > 90:
        report.append("> [!WARNING]\n> **Critical Budget Alert**: You have utilized over 90% of your budget. Immediate cost-cutting on discretionary items is highly recommended.")
    elif kpis['budget_utilization_pct'] > 70:
        report.append("> [!NOTE]\n> **Budget Warning**: You have crossed 70% of your budget limit. Keep an eye on non-essential purchases.")
    else:
        report.append("> [!TIP]\n> **Healthy Status**: Your spending rate is healthy. You are on track to save money this month.")
        
    return "\n".join(report)
