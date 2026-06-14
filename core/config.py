"""Global configuration for Manus AI Skill Framework."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Model tiers — ordered cheapest to most expensive
MODEL_TIERS = {
    "nano": {"max_tokens": 2048, "cost_per_1k": 0.1, "models": ["gpt-3.5-turbo"]},
    "micro": {"max_tokens": 4096, "cost_per_1k": 0.3, "models": ["gpt-4o-mini"]},
    "standard": {"max_tokens": 8192, "cost_per_1k": 1.0, "models": ["gpt-4o"]},
    "pro": {"max_tokens": 16384, "cost_per_1k": 3.0, "models": ["gpt-4-turbo"]},
    "ultra": {"max_tokens": 32768, "cost_per_1k": 6.0, "models": ["o1", "o3"]},
}

# Complexity thresholds for smart routing
COMPLEXITY_THRESHOLDS = {
    "trivial": 0.2,    # Use nano model
    "simple": 0.4,     # Use micro model
    "moderate": 0.6,   # Use standard model
    "complex": 0.8,    # Use pro model
    "extreme": 1.0,    # Use ultra model
}

DEFAULT_DAILY_CREDIT_LIMIT = 1500
CACHE_TTL_SECONDS = 3600  # 1 hour default cache


@dataclass
class SkillConfig:
    """Configuration for a single skill."""
    name: str
    category: str
    description: str
    version: str = "1.0.0"
    min_model_tier: str = "micro"
    max_tokens: int = 4096
    temperature: float = 0.3
    credit_cost_estimate: int = 10
    cacheable: bool = True
    batch_compatible: bool = False
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class CreditConfig:
    """Credit management configuration."""
    daily_limit: int = DEFAULT_DAILY_CREDIT_LIMIT
    warning_threshold: float = 0.2  # Warn at 20% remaining
    auto_downgrade: bool = True  # Auto-downgrade model when low on credit
    track_savings: bool = True
    cache_enabled: bool = True
    batch_enabled: bool = True
