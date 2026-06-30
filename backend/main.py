# HostelWise AI - FastAPI Application Main Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cloud.config import cloud_settings
from backend.api.routes.expenses import router as expenses_router
from backend.api.routes.forecasts import router as forecasts_router
from backend.api.routes.risk import router as risk_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.benchmarks import router as benchmarks_router

# Initialize FastAPI App
app = FastAPI(
    title=cloud_settings.PROJECT_NAME,
    description="AI-powered and GPU-accelerated student expense intelligence API.",
    version="1.1.0"
)

# CORS Middleware for Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(expenses_router)
app.include_router(forecasts_router)
app.include_router(risk_router)
app.include_router(recommendations_router)
app.include_router(chat_router)
app.include_router(benchmarks_router)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {cloud_settings.PROJECT_NAME}",
        "status": "online",
        "env": cloud_settings.ENV
    }
