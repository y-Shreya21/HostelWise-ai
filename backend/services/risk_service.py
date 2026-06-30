# HostelWise AI - Multi-Factor Budget Risk Scoring Engine
import pandas as pd
from datetime import datetime
from analytics.transform import get_spending_velocity_status
from forecasting.predict import predict_current_month_end

class RiskScoringService:
    def calculate_multi_factor_risk(self, df: pd.DataFrame, budget_limit: float, current_date=None) -> dict:
        """
        Calculate a multi-factor budget risk score (0-100) and risk level.
        
        Factors:
        1. Budget Utilization (30% weight)
        2. Spending Growth / Velocity (20% weight)
        3. Category Spikes (20% weight)
        4. Historical Trend / Run Rate (30% weight)
        """
        if len(df) == 0:
            return {
                'risk_score': 0,
                'risk_level': 'LOW',
                'current_spend': 0.0,
                'projected_spend': 0.0,
                'budget_limit': budget_limit,
                'is_over_budget': False
            }

        if current_date is None:
            current_date = datetime.now()
        else:
            current_date = pd.to_datetime(current_date)

        # 1. Budget Utilization Factor (F_util)
        # Ratio of current spend to total budget
        start_of_month = pd.Timestamp(current_date.year, current_date.month, 1)
        end_of_day = pd.Timestamp(current_date.year, current_date.month, current_date.day, 23, 59, 59)
        month_df = df[(df['date'] >= start_of_month) & (df['date'] <= end_of_day)]
        
        current_spend = float(month_df['amount'].sum()) if len(month_df) > 0 else 0.0
        days_elapsed = (current_date - start_of_month).days + 1
        days_in_month = pd.Period(current_date.strftime('%Y-%m')).days_in_month
        
        # Expected utilization based on time elapsed
        expected_util = (days_elapsed / days_in_month)
        actual_util = (current_spend / budget_limit) if budget_limit > 0 else 0.0
        
        if expected_util > 0:
            util_ratio = actual_util / expected_util
            f_util = min(util_ratio * 50, 100)  # Caps at 100
        else:
            f_util = 0.0

        # 2. Spending Growth / Velocity Factor (F_growth)
        # Based on 7-day vs 30-day rolling average
        velocity = get_spending_velocity_status(df)
        ratio = velocity.get('ratio', 1.0)
        # If ratio is 1.5 (spending 50% faster than monthly average), risk is high
        f_growth = min(max((ratio - 0.8) / 0.7 * 100, 0), 100)

        # 3. Category Spikes Factor (F_spikes)
        # Check if any category has spiked beyond its healthy threshold
        cat_sums = month_df.groupby('category')['amount'].sum()
        f_spikes = 0.0
        thresholds = {
            'Food': 0.35, 'Snacks': 0.15, 'Travel': 0.15, 
            'Shopping': 0.15, 'Entertainment': 0.10, 'Recharge': 0.08
        }
        
        for cat, spent in cat_sums.items():
            limit_pct = thresholds.get(cat, 0.10)
            allocated_limit = limit_pct * budget_limit
            if spent > allocated_limit:
                # Calculate how much it exceeded the limit
                excess_ratio = (spent - allocated_limit) / allocated_limit
                f_spikes = max(f_spikes, min(excess_ratio * 100, 100))

        # 4. Historical Trend / Run Rate (F_trend)
        # Based on polynomial month-end projection compared to budget
        projection = predict_current_month_end(df, budget_limit, current_date)
        projected_spend = projection['projected_spend']
        
        if budget_limit > 0:
            trend_ratio = projected_spend / budget_limit
            if trend_ratio <= 1.0:
                f_trend = trend_ratio * 70  # Maxes out at 70 if within budget
            else:
                f_trend = 70 + min((trend_ratio - 1.0) / 0.5 * 30, 30)  # Scales to 100
        else:
            f_trend = 0.0

        # Weighted Average Calculation
        # 30% Util, 20% Growth, 20% Spikes, 30% Trend
        raw_score = (0.30 * f_util) + (0.20 * f_growth) + (0.20 * f_spikes) + (0.30 * f_trend)
        risk_score = int(round(raw_score))
        
        # Ensure score is within [0, 100]
        risk_score = min(max(risk_score, 0), 100)

        # Map to Risk Levels (LOW: 0-30, MEDIUM: 31-70, HIGH: 71-100)
        if risk_score <= 30:
            level = 'LOW'
        elif risk_score <= 70:
            level = 'MEDIUM'
        else:
            level = 'HIGH'

        return {
            'risk_score': risk_score,
            'risk_level': level,
            'current_spend': round(current_spend, 2),
            'projected_spend': round(projected_spend, 2),
            'budget_limit': budget_limit,
            'is_over_budget': projected_spend > budget_limit
        }

# Global risk scoring service instance
risk_scoring_service = RiskScoringService()
