# HostelWise AI - Central Cloud & Application Settings
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class CloudSettings(BaseSettings):
    PROJECT_NAME: str = "HostelWise AI - Smart Expense Intelligence"
    ENV: str = os.getenv("HOSTELWISE_ENV", "development")
    
    # AI Config
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # GCP Config
    GCP_PROJECT: str = os.getenv("GCP_PROJECT", "")
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "hostelwise-raw-expenses")
    BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "hostelwise_ai_dataset")
    
    # Local Fallback Config
    LOCAL_DATA_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "data"
    )
    SQLITE_DB_PATH: str = os.path.join(LOCAL_DATA_DIR, "hostelwise.db")
    UPLOAD_DIR: str = os.path.join(LOCAL_DATA_DIR, "uploads")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

cloud_settings = CloudSettings()

# Ensure local data and upload directories exist
os.makedirs(cloud_settings.LOCAL_DATA_DIR, exist_ok=True)
os.makedirs(cloud_settings.UPLOAD_DIR, exist_ok=True)
