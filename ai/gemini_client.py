# HostelWise AI - Gemini API Connection Client
import os
import google.generativeai as genai
from cloud.config import cloud_settings

class GeminiAPIClient:
    def __init__(self):
        self.api_key = cloud_settings.GEMINI_API_KEY
        self.is_active = False
        self.model_name = "gemini-1.5-flash"
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.is_active = True
                print("Gemini API Client successfully configured.")
            except Exception as e:
                print(f"Gemini configuration failed: {e}")
        else:
            print("GEMINI_API_KEY environment variable not set. Gemini API Client running in inactive/demo mode.")

    def get_model(self, system_instruction: str = None):
        """Returns a GenerativeModel instance with optional system instructions."""
        if not self.is_active:
            raise RuntimeError("Gemini API Client is not active due to missing API key.")
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )

# Global Gemini client instance
gemini_client = GeminiAPIClient()
