"""
Clyrdia Core - Consolidated core functionality for MVP
"""

from .licensing import LicensingManager
from .benchmarking import BenchmarkEngine
from .providers import ModelInterface
from .evaluator import QualityEvaluator
from .caching import CacheManager
from .database import LocalDatabase
from .models import (
    BenchmarkResult, TestCase, UserStatus, CreditEstimate,
    PlanTier, UserRole, ModelProvider, ModelConfig, ClyrdiaConfig
)
from .console import console

__all__ = [
    "LicensingManager",
    "BenchmarkEngine", 
    "ModelInterface",
    "QualityEvaluator",
    "CacheManager",
    "LocalDatabase",
    "BenchmarkResult",
    "TestCase", 
    "UserStatus",
    "CreditEstimate",
    "PlanTier",
    "UserRole",
    "ModelProvider",
    "ModelConfig",
    "ClyrdiaConfig",
    "console"
]