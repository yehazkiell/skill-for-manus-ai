"""Credit Manager — Tracks, optimizes, and reports credit usage."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from .config import CreditConfig, DEFAULT_DAILY_CREDIT_LIMIT, CACHE_TTL_SECONDS


@dataclass
class CreditUsage:
    """Record of a single credit transaction."""
    skill_name: str
    tokens_used: int
    credit_spent: float
    credit_saved: float
    model_tier: str
    cached: bool
    timestamp: float = field(default_factory=time.time)


class CreditCache:
    """In-memory cache to avoid redundant API calls."""

    def __init__(self, ttl: int = CACHE_TTL_SECONDS):
        self._store: dict[str, tuple[Any, float]] = {}
        self._skill_keys: dict[str, set[str]] = {}
        self._ttl = ttl
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_key(skill_name: str, context: dict[str, Any]) -> str:
        raw = json.dumps({"skill": skill_name, "ctx": context}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, skill_name: str, context: dict[str, Any]) -> Optional[Any]:
        key = self._hash_key(skill_name, context)
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, ts = entry
        if time.time() - ts > self._ttl:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return value

    def put(self, skill_name: str, context: dict[str, Any], value: Any) -> None:
        key = self._hash_key(skill_name, context)
        self._store[key] = (value, time.time())
        self._skill_keys.setdefault(skill_name, set()).add(key)

    def invalidate(self, skill_name: Optional[str] = None) -> None:
        if skill_name is None:
            self._store.clear()
            self._skill_keys.clear()
        else:
            for k in self._skill_keys.pop(skill_name, set()):
                self._store.pop(k, None)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "entries": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }


class CreditManager:
    """Manages credit budget, tracks usage, and maximizes savings."""

    def __init__(
        self,
        daily_limit: int = DEFAULT_DAILY_CREDIT_LIMIT,
        config: Optional[CreditConfig] = None,
    ):
        self._config = config or CreditConfig(daily_limit=daily_limit)
        self._used: float = 0.0
        self._saved: float = 0.0
        self._history: list[CreditUsage] = []
        self._cache = CreditCache()
        self._day_start = time.time()

    # --- budget helpers ---

    @property
    def remaining(self) -> float:
        return max(0.0, self._config.daily_limit - self._used)

    @property
    def total_saved(self) -> float:
        return self._saved

    @property
    def usage_pct(self) -> float:
        return self._used / self._config.daily_limit if self._config.daily_limit else 0

    @property
    def is_low(self) -> bool:
        return (self.remaining / self._config.daily_limit) < self._config.warning_threshold if self._config.daily_limit else True

    # --- recording ---

    def record(
        self,
        skill_name: str,
        tokens_used: int,
        credit_spent: float,
        credit_saved: float = 0.0,
        model_tier: str = "standard",
        cached: bool = False,
    ) -> CreditUsage:
        usage = CreditUsage(
            skill_name=skill_name,
            tokens_used=tokens_used,
            credit_spent=credit_spent,
            credit_saved=credit_saved,
            model_tier=model_tier,
            cached=cached,
        )
        self._used += credit_spent
        self._saved += credit_saved
        self._history.append(usage)
        return usage

    # --- cache delegation ---

    @property
    def cache(self) -> CreditCache:
        return self._cache

    # --- optimization suggestions ---

    def suggest_model_tier(self, base_tier: str, credit_cost: float) -> str:
        """Suggest a cheaper tier when credit is running low."""
        if not self._config.auto_downgrade:
            return base_tier
        tier_order = ["nano", "micro", "standard", "pro", "ultra"]
        idx = tier_order.index(base_tier) if base_tier in tier_order else 2
        if self.remaining < credit_cost * 2:
            idx = max(0, idx - 2)
        elif self.is_low:
            idx = max(0, idx - 1)
        return tier_order[idx]

    # --- reporting ---

    def report(self) -> dict[str, Any]:
        return {
            "daily_limit": self._config.daily_limit,
            "used": round(self._used, 2),
            "remaining": round(self.remaining, 2),
            "saved": round(self._saved, 2),
            "usage_pct": f"{self.usage_pct:.1%}",
            "transactions": len(self._history),
            "cache_stats": self._cache.stats,
            "top_skills": self._top_skills(5),
        }

    def _top_skills(self, n: int) -> list[dict[str, Any]]:
        per_skill: dict[str, float] = {}
        for h in self._history:
            per_skill[h.skill_name] = per_skill.get(h.skill_name, 0) + h.credit_spent
        sorted_skills = sorted(per_skill.items(), key=lambda x: x[1], reverse=True)
        return [{"skill": s, "credit": round(c, 2)} for s, c in sorted_skills[:n]]

    def reset_daily(self) -> None:
        """Reset for a new day."""
        self._used = 0.0
        self._saved = 0.0
        self._history.clear()
        self._cache.invalidate()
        self._day_start = time.time()
