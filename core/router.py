"""Smart Router — Routes tasks to the most cost-effective skill and model tier."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from .config import COMPLEXITY_THRESHOLDS, MODEL_TIERS, SkillConfig
from .credit_manager import CreditManager


@dataclass
class RouteDecision:
    """Result of routing a task."""
    skill_name: str
    model_tier: str
    estimated_credit: float
    reason: str
    cached: bool = False


class ComplexityAnalyzer:
    """Estimates task complexity from text signals."""

    # Indicators that raise complexity
    COMPLEX_SIGNALS = [
        r"\b(architect|design pattern|microservice|distributed)\b",
        r"\b(security|vulnerability|exploit|penetration)\b",
        r"\b(optimize|performance|scalab\w*|concurrent)\b",
        r"\b(refactor|migration|legacy|rewrite)\b",
        r"\b(machine learning|neural|deep learning|training)\b",
    ]

    # Indicators for simple tasks
    SIMPLE_SIGNALS = [
        r"\b(typo|rename|comment|format|lint)\b",
        r"\b(hello world|example|demo|tutorial)\b",
        r"\b(translate|summarize|list|count)\b",
        r"\b(fix (the )?bug|small change|minor)\b",
    ]

    @classmethod
    def estimate(cls, task: str, context: Optional[dict[str, Any]] = None) -> float:
        task_lower = task.lower()
        score = 0.5  # baseline

        for pattern in cls.COMPLEX_SIGNALS:
            if re.search(pattern, task_lower):
                score += 0.1

        for pattern in cls.SIMPLE_SIGNALS:
            if re.search(pattern, task_lower):
                score -= 0.1

        # Context size contributes to complexity
        if context:
            ctx_len = len(str(context))
            if ctx_len > 10000:
                score += 0.15
            elif ctx_len > 5000:
                score += 0.1
            elif ctx_len < 500:
                score -= 0.05

        return max(0.0, min(1.0, score))


class SmartRouter:
    """Routes tasks to optimal skill + model tier combination."""

    def __init__(
        self,
        skills: Optional[dict[str, SkillConfig]] = None,
        credit_manager: Optional[CreditManager] = None,
    ):
        self._skills = skills or {}
        self._credit_mgr = credit_manager

    def register_skill(self, config: SkillConfig) -> None:
        self._skills[config.name] = config

    def route(
        self,
        task: str,
        context: Optional[dict[str, Any]] = None,
        preferred_skill: Optional[str] = None,
        max_credit: Optional[float] = None,
    ) -> RouteDecision:
        complexity = ComplexityAnalyzer.estimate(task, context)
        tier = self._select_tier(complexity)

        # Pick skill
        if preferred_skill and preferred_skill in self._skills:
            skill_cfg = self._skills[preferred_skill]
        else:
            skill_cfg = self._match_skill(task)

        if skill_cfg is None:
            return RouteDecision(
                skill_name="generic",
                model_tier=tier,
                estimated_credit=MODEL_TIERS.get(tier, {}).get("cost_per_1k", 1.0) * 4,
                reason=f"No matching skill; using generic {tier} model",
            )

        # Credit-aware downgrade
        estimated = skill_cfg.credit_cost_estimate
        if self._credit_mgr:
            tier = self._credit_mgr.suggest_model_tier(tier, estimated)
            # Check cache
            cached = self._credit_mgr.cache.get(skill_cfg.name, context or {})
            if cached is not None:
                return RouteDecision(
                    skill_name=skill_cfg.name,
                    model_tier=tier,
                    estimated_credit=0,
                    reason="Cache hit — zero credit cost",
                    cached=True,
                )

        if max_credit and estimated > max_credit:
            tier = self._cheapest_viable_tier(max_credit)
            estimated = min(estimated, max_credit)

        return RouteDecision(
            skill_name=skill_cfg.name,
            model_tier=tier,
            estimated_credit=estimated,
            reason=f"Complexity {complexity:.2f} → tier={tier}",
        )

    def _select_tier(self, complexity: float) -> str:
        for label, threshold in sorted(
            COMPLEXITY_THRESHOLDS.items(), key=lambda x: x[1]
        ):
            if complexity <= threshold:
                tier_map = {
                    "trivial": "nano",
                    "simple": "micro",
                    "moderate": "standard",
                    "complex": "pro",
                    "extreme": "ultra",
                }
                return tier_map.get(label, "standard")
        return "standard"

    def _match_skill(self, task: str) -> Optional[SkillConfig]:
        task_lower = task.lower()
        best_score = 0
        best_skill = None
        for cfg in self._skills.values():
            score = 0
            for tag in cfg.tags:
                if tag.lower() in task_lower:
                    score += 2
            if cfg.name.replace("-", " ") in task_lower:
                score += 3
            if cfg.category.lower() in task_lower:
                score += 1
            if score > best_score:
                best_score = score
                best_skill = cfg
        return best_skill

    @staticmethod
    def _cheapest_viable_tier(max_credit: float) -> str:
        for tier_name, info in sorted(MODEL_TIERS.items(), key=lambda x: x[1]["cost_per_1k"]):
            if info["cost_per_1k"] * 4 <= max_credit:
                return tier_name
        return "nano"
