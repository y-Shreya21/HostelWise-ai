# HostelWise AI - Performance Benchmarking API Routes
from fastapi import APIRouter, HTTPException
from backend.api.schemas.schemas import BenchmarkSummary
from benchmark.compare import execute_benchmark_comparison

router = APIRouter(tags=["benchmark"])

@router.get("/benchmark", response_model=BenchmarkSummary)
def run_benchmark():
    """Trigger the CPU vs. GPU (NVIDIA RAPIDS cuDF) performance benchmark."""
    try:
        summary = execute_benchmark_comparison()
        return BenchmarkSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {e}")
