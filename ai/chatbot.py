# HostelWise AI - Chatbot Session Handler
from typing import List, Dict
import re
from .gemini_client import gemini_client
from .prompts import SYSTEM_INSTRUCTION, build_financial_context_block

class HostelWiseChatbot:
    def __init__(self):
        self.client = gemini_client

    def get_chat_response(self, query: str, chat_history: List[Dict], financial_context: Dict) -> str:
        """
        Runs a chat turn.
        Prepend the financial context block, formats the conversation history,
        and queries Gemini (or falls back to mock responses if inactive).
        """
        context_block = build_financial_context_block(financial_context)
        
        if not self.client.is_active:
            return self._generate_mock_response(query, financial_context)

        try:
            # Get model with system instructions
            model = self.client.get_model(system_instruction=SYSTEM_INSTRUCTION)
            
            # Format history for Gemini API
            formatted_history = []
            for msg in chat_history:
                role = "user" if msg['role'] == "user" else "model"
                formatted_history.append({
                    "role": role,
                    "parts": [msg['content']]
                })
                
            # Start chat session
            chat = model.start_chat(history=formatted_history)
            
            # Prepend context to the user's query
            full_query = f"{context_block}\n\nUser Question: {query}"
            response = chat.send_message(full_query)
            return response.text
            
        except Exception as e:
            print(f"Error in Gemini Chatbot: {e}")
            return f"Hi! I had trouble reaching my AI brain ({e}). However, based on your data: you have spent ₹{financial_context.get('kpis', {}).get('total_expense', 0):,.2f} out of your ₹{financial_context.get('risk', {}).get('budget_limit', 0):,.2f} budget. Let me know if you want to discuss your budget risk!"

    def _generate_mock_response(self, query: str, context: Dict) -> str:
        """Fallback rule-based response generator when Gemini API is not configured."""
        q = query.lower()
        kpis = context.get('kpis', {})
        risk = context.get('risk', {})
        recs = context.get('recommendations', [])
        
        spent = kpis.get('total_expense', 0)
        budget = risk.get('budget_limit', 10000.0)
        remaining = max(budget - spent, 0)
        risk_level = risk.get('risk_level', 'LOW')
        projected = risk.get('projected_spend', 0)
        
        welcome_msg = "*(Demo Mode - Configure GEMINI_API_KEY to enable full AI responses)*\n\n"
        
        if "overspend" in q or "where is my money" in q or "habits" in q:
            highest_cat = kpis.get('highest_category', 'Food')
            highest_amt = kpis.get('highest_category_amount', 0)
            return welcome_msg + f"Looking at your expenses, your highest spending category is **{highest_cat}** where you've spent **₹{highest_amt:,.2f}** so far. Your overall budget risk is **{risk_level}** (Score: {risk.get('risk_score', 0)}/100). You are projected to finish the month at **₹{projected:,.2f}**."
            
        elif "afford" in q or "buy" in q:
            numbers = re.findall(r'\d+', q)
            cost = int(numbers[0]) if numbers else 1000
            
            if cost <= remaining:
                return welcome_msg + f"Yes, you can afford a purchase of **₹{cost:,.2f}**. You have **₹{remaining:,.2f}** remaining in your budget for this month. However, since your projected month-end spend is **₹{projected:,.2f}**, make sure this purchase is necessary!"
            else:
                deficit = cost - remaining
                return welcome_msg + f"No, a purchase of **₹{cost:,.2f}** would exceed your remaining budget by **₹{deficit:,.2f}**. I recommend postponing this purchase until next month, or cutting down on Snacks/Shopping to accommodate it."
                
        elif "save" in q or "recommendation" in q:
            if recs:
                best_rec = recs[0]['recommendation_text']
                return welcome_msg + f"To save money, my top recommendation is: \n\n{best_rec}\n\nImplementing this can save you around **₹{recs[0]['potential_savings']}**!"
            return welcome_msg + "Your budget is in excellent shape! I recommend setting aside 10% of your allowance at the beginning of next month to build an emergency fund."
            
        else:
            return welcome_msg + f"Hello! I am your HostelWise AI assistant. I see that you've spent **₹{spent:,.2f}** of your **₹{budget:,.2f}** budget. Your risk level is **{risk_level}**. Ask me questions like 'Where am I overspending?' or 'Can I afford a ₹1000 purchase?' and I will help you out!"

# Instantiated chatbot
chatbot = HostelWiseChatbot()
