"""
Empirical Evaluation and Ablation Benchmark API Endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional

from backend.app.core.security import get_current_user
from experiments.run_5seeds import run_5seed_reproducibility
from experiments.ablation import run_ablation_study
from datasets.synthetic import generate_synthetic_dataset

router = APIRouter(prefix="/experiments", tags=["Experiments & Benchmarks"])

# Cache benchmark results in memory for instant API queries
_CACHED_5SEEDS = None
_CACHED_ABLATION = None


@router.get("/5seeds")
def get_5seeds_benchmark(
    force_rerun: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    global _CACHED_5SEEDS
    if _CACHED_5SEEDS is None or force_rerun:
        _CACHED_5SEEDS = run_5seed_reproducibility(num_samples=2500)
    return _CACHED_5SEEDS


@router.get("/ablation")
def get_ablation_benchmark(
    force_rerun: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    global _CACHED_ABLATION
    if _CACHED_ABLATION is None or force_rerun:
        txs = generate_synthetic_dataset(num_transactions=2500, seed=42)
        _CACHED_ABLATION = run_ablation_study(txs, seed=42)
    return _CACHED_ABLATION
