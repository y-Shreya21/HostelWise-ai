# HostelWise AI - Unit Tests for Risk & Recommendation Engines
import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.risk_service import risk_scoring_service
from backend.services.recommendation_service import recommendation_service

@pytest.fixture
def base_expense_df():
    """Create a baseline expense dataframe for current month."""
    current_date = datetime.now()
    dates = [current_date - timedelta(days=i) for i in range(15)]
    
    # Base spends: 15 transactions of ₹100 each
    df = pd.DataFrame({
        'date': dates,
        'amount': [100.0] * 15,
        'category': ['Food'] * 15,
        'subcategory': ['Mess'] * 15,
        'description': ['Dinner'] * 15,
        'payment_mode': ['UPI'] * 15
    })
    return df

def test_risk_scoring_low_risk(base_expense_df):
    """Verify that low spending relative to budget yields a LOW risk score."""
    # Total spent: ₹1500, Budget: ₹10000 -> 15% spent
    risk = risk_scoring_service.calculate_multi_factor_risk(base_expense_df, budget_limit=10000.0)
    
    assert risk['risk_level'] == 'LOW'
    assert risk['risk_score'] <= 30
    assert not risk['is_over_budget']

def test_risk_scoring_high_risk(base_expense_df):
    """Verify that high spending relative to budget yields a HIGH risk score."""
    # Add a massive transaction to spike the spend
    high_spend_df = base_expense_df.copy()
    high_spend_df.loc[0, 'amount'] = 9500.0  # Spikes total spend to ₹10,900 (Budget is 10,000)
    
    risk = risk_scoring_service.calculate_multi_factor_risk(high_spend_df, budget_limit=10000.0)
    
    assert risk['risk_level'] == 'HIGH'
    assert risk['risk_score'] > 70
    assert risk['is_over_budget']

def test_recommendations_generation(base_expense_df):
    """Verify that exceeding category thresholds generates specific recommendations."""
    # Total spent on Food is ₹1500. Let's make the budget ₹2000.
    # Food threshold is 35% of budget = ₹700. So we are exceeding it!
    recs = recommendation_service.get_recommendations(base_expense_df, budget_limit=2000.0)
    
    assert len(recs) > 0
    # Check that a Food recommendation is generated
    food_recs = [r for r in recs if r['category'] == 'Food']
    assert len(food_recs) == 1
    assert food_recs[0]['potential_savings'] > 0
    assert "Hostel mess" in food_recs[0]['recommendation_text'] or "mess meals" in food_recs[0]['recommendation_text']
