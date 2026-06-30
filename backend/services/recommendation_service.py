# HostelWise AI - Savings Recommendation Service
import pandas as pd

class SavingsRecommendationService:
    def get_recommendations(self, df: pd.DataFrame, budget_limit: float = 10000.0) -> list:
        """
        Analyze spending habits and generate data-driven savings recommendations.
        """
        if len(df) == 0:
            return []
            
        # Group by category
        cat_spend = df.groupby('category')['amount'].sum().to_dict()
        
        # Category thresholds as a percentage of the overall budget
        thresholds = {
            'Food': 0.35,          # 35% of budget
            'Snacks': 0.15,        # 15%
            'Travel': 0.15,        # 15%
            'Shopping': 0.15,      # 15%
            'Entertainment': 0.10, # 10%
            'Recharge': 0.08,      # 8%
            'Medical': 0.05,       # 5%
            'Education': 0.10,     # 10%
            'Other': 0.05          # 5%
        }
        
        recommendations = []
        
        for cat, spent in cat_spend.items():
            limit_pct = thresholds.get(cat, 0.10)
            allocated_limit = limit_pct * budget_limit
            
            if spent > allocated_limit:
                excess = spent - allocated_limit
                pct_over = (excess / allocated_limit) * 100
                
                if cat == 'Food':
                    recommendations.append({
                        'category': 'Food',
                        'potential_savings': round(excess * 0.4, 2),
                        'recommendation_text': f"Food spending is ₹{spent:,.2f} (exceeding target by {pct_over:.0f}%). Cook more or opt for hostel mess meals instead of restaurant delivery to save around ₹{excess * 0.4:.0f}/month."
                    })
                elif cat == 'Snacks':
                    recommendations.append({
                        'category': 'Snacks',
                        'potential_savings': round(excess * 0.5, 2),
                        'recommendation_text': f"Snack purchases (tea, coffee, noodles) total ₹{spent:,.2f}. Reducing canteen visits and buying snacks in bulk can save you ₹{excess * 0.5:.0f}/month."
                    })
                elif cat == 'Shopping':
                    recommendations.append({
                        'category': 'Shopping',
                        'potential_savings': round(excess * 0.6, 2),
                        'recommendation_text': f"Shopping expenses are high at ₹{spent:,.2f}. Postponing non-essential clothes or electronics purchases by 2 weeks could save ₹{excess * 0.6:.0f} this month."
                    })
                elif cat == 'Travel':
                    recommendations.append({
                        'category': 'Travel',
                        'potential_savings': round(excess * 0.3, 2),
                        'recommendation_text': f"Travel cost is ₹{spent:,.2f}. Substituting individual cab rides (Uber/Ola) with shared autos or metro transit can save you ₹{excess * 0.3:.0f}/month."
                    })
                elif cat == 'Entertainment':
                    recommendations.append({
                        'category': 'Entertainment',
                        'potential_savings': round(excess * 0.4, 2),
                        'recommendation_text': f"Entertainment & Outing costs are ₹{spent:,.2f}. Consider sharing subscriptions (Netflix/Spotify) with roommates to easily save ₹{excess * 0.4:.0f}."
                    })

        # General fallback if spending is very clean
        if len(recommendations) == 0:
            recommendations.append({
                'category': 'General',
                'potential_savings': round(budget_limit * 0.05, 2),
                'recommendation_text': f"Great job! Your spending is well-distributed. Saving a flat 5% of your allowance at the start of the month can build a safety net of ₹{budget_limit * 0.05:.0f}."
            })
            
        return recommendations

# Global service instance
recommendation_service = SavingsRecommendationService()
