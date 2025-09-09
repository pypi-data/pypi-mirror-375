"""
Consolidated models for Clyrdia CLI MVP - all data classes in one place.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# ============================================================================
# Enums
# ============================================================================

class ModelProvider(Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class PlanTier(Enum):
    """Subscription plan tiers - simplified to two tiers for MVP"""
    DEVELOPER = "developer"  # Free tier
    BUSINESS = "business"     # $500/month

class UserRole(Enum):
    """User roles - simplified for MVP"""
    OWNER = "owner"          # Team owner with full access
    MEMBER = "member"        # Regular team member

# ============================================================================
# Core Models
# ============================================================================

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: ModelProvider
    input_cost: float  # per 1M tokens
    output_cost: float  # per 1M tokens
    max_tokens: int
    context_window: int
    capabilities: List[str] = field(default_factory=list)
    speed_tier: str = "standard"  # fast, standard, slow
    tier: str = "balanced"  # flagship, balanced, speed_cost

@dataclass
class BenchmarkResult:
    """Result from a single benchmark test"""
    model: str
    provider: str
    test_name: str
    prompt: str
    response: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    cost: float
    success: bool
    error: Optional[str] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestCase:
    """Definition of a benchmark test case"""
    name: str
    prompt: str
    expected_output: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    evaluation_criteria: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    weight: float = 1.0

@dataclass
class UserStatus:
    """User subscription and credit status"""
    user_name: str
    plan: PlanTier
    credits_remaining: int
    credits_monthly_limit: int
    resets_on: str
    api_key: str
    team_id: Optional[str] = None
    role: Optional[UserRole] = None
    team_name: Optional[str] = None
    max_team_members: Optional[int] = None
    has_cicd_access: bool = False

@dataclass
class CreditEstimate:
    """Credit cost estimation for a benchmark run"""
    total_tests: int
    cache_hits: int
    live_api_calls: int
    estimated_credits: int
    current_balance: int
    test_breakdown: Dict[str, int]

# ============================================================================
# Configuration
# ============================================================================

class ClyrdiaConfig:
    """Global configuration management - simplified for MVP"""
    
    # Model catalog with latest production-ready models
    # All prices are USD per 1M tokens (accurate as of latest pricing)
    MODELS = {
        # ---------- OpenAI ----------
        "gpt-5": ModelConfig(
            name="gpt-5",
            provider=ModelProvider.OPENAI,
            input_cost=1.25,
            output_cost=10.00,
            max_tokens=200000, context_window=200000,
            capabilities=["chat","code","vision","function_calling","multimodal","reasoning","advanced_math"], 
            speed_tier="fast", tier="flagship"
        ),
        "gpt-5-mini": ModelConfig(
            name="gpt-5-mini",
            provider=ModelProvider.OPENAI,
            input_cost=0.25,
            output_cost=2.00,
            max_tokens=200000, context_window=200000,
            capabilities=["chat","code","reasoning"], 
            speed_tier="fast", tier="balanced"
        ),
        "gpt-4o": ModelConfig(
            name="gpt-4o",
            provider=ModelProvider.OPENAI,
            input_cost=2.50,
            output_cost=10.00,
            max_tokens=128000, context_window=128000,
            capabilities=["chat","code","vision","function_calling","multimodal"], 
            speed_tier="fast", tier="flagship"
        ),
        "gpt-4o-mini": ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.OPENAI,
            input_cost=0.15,
            output_cost=0.60,
            max_tokens=128000, context_window=128000,
            capabilities=["chat","code"], 
            speed_tier="fastest", tier="speed_cost"
        ),

        # ---------- Anthropic (Claude) ----------
        "claude-opus-4-1-20250805": ModelConfig(
            name="claude-opus-4-1-20250805",
            provider=ModelProvider.ANTHROPIC,
            input_cost=15.00,
            output_cost=75.00,
            max_tokens=300000, context_window=300000,
            capabilities=["chat","code","analysis","creative","multimodal","reasoning","advanced_math"], 
            speed_tier="standard", tier="flagship"
        ),
        "claude-sonnet-4-20250514": ModelConfig(
            name="claude-sonnet-4-20250514",
            provider=ModelProvider.ANTHROPIC,
            input_cost=3.00,
            output_cost=15.00,
            max_tokens=250000, context_window=250000,
            capabilities=["chat","code","analysis","multimodal","reasoning"], 
            speed_tier="fast", tier="balanced"
        ),
        "claude-3-5-sonnet-20241022": ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider=ModelProvider.ANTHROPIC,
            input_cost=3.00,
            output_cost=15.00,
            max_tokens=200000, context_window=200000,
            capabilities=["chat","code","analysis","multimodal"], 
            speed_tier="fast", tier="balanced"
        ),
        "claude-3-5-haiku-20241022": ModelConfig(
            name="claude-3-5-haiku-20241022",
            provider=ModelProvider.ANTHROPIC,
            input_cost=0.80,
            output_cost=4.00,
            max_tokens=200000, context_window=200000,
            capabilities=["chat","code"], 
            speed_tier="fastest", tier="speed_cost"
        ),
    }
    
    @classmethod
    def get_model(cls, name: str) -> Optional[ModelConfig]:
        return cls.MODELS.get(name)
    
    @classmethod
    def list_models(cls) -> List[str]:
        return list(cls.MODELS.keys())
    
    @classmethod
    def list_openai_models(cls) -> List[str]:
        return [name for name, config in cls.MODELS.items() 
                if config.provider == ModelProvider.OPENAI]
    
    @classmethod
    def list_anthropic_models(cls) -> List[str]:
        return [name for name, config in cls.MODELS.items() 
                if config.provider == ModelProvider.ANTHROPIC]

def get_model_configs() -> Dict[str, ModelConfig]:
    """Get all model configurations (OpenAI and Anthropic only)"""
    return ClyrdiaConfig.MODELS
