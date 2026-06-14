"""Skill Loader & Registry — Discovers, loads, and manages all skills."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

import yaml

from .config import SKILLS_DIR, SkillConfig
from .credit_manager import CreditManager
from .router import SmartRouter, RouteDecision


class SkillRegistry:
    """Central registry that loads skill definitions from YAML files."""

    def __init__(self, skills_dir: Optional[Path] = None):
        self._dir = skills_dir or SKILLS_DIR
        self._skills: dict[str, SkillConfig] = {}
        self._prompts: dict[str, str] = {}
        self._router = SmartRouter()

    # --- loading ---

    def load_all(self) -> int:
        """Discover and load every *.yaml skill file under skills_dir."""
        for yaml_path in sorted(self._dir.rglob("*.yaml")):
            try:
                self._load_one(yaml_path)
            except Exception as exc:
                print(f"[WARN] Skipping {yaml_path.name}: {exc}", file=sys.stderr)
        count = len(self._skills)
        # Register all in router
        for cfg in self._skills.values():
            self._router.register_skill(cfg)
        return count

    def _load_one(self, path: Path) -> None:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data or "skill" not in data:
            return
        s = data["skill"]
        cfg = SkillConfig(
            name=s["name"],
            category=s.get("category", path.parent.name),
            description=s.get("description", ""),
            version=s.get("version", "1.0.0"),
            min_model_tier=s.get("min_model_tier", "micro"),
            max_tokens=s.get("max_tokens", 4096),
            temperature=s.get("temperature", 0.3),
            credit_cost_estimate=s.get("credit_cost_estimate", 10),
            cacheable=s.get("cacheable", True),
            batch_compatible=s.get("batch_compatible", False),
            tags=s.get("tags", []),
            dependencies=s.get("dependencies", []),
        )
        self._skills[cfg.name] = cfg
        self._prompts[cfg.name] = s.get("system_prompt", "")

    # --- querying ---

    def get(self, name: str) -> Optional[SkillConfig]:
        return self._skills.get(name)

    def list_skills(self, category: Optional[str] = None) -> list[SkillConfig]:
        skills = list(self._skills.values())
        if category:
            skills = [s for s in skills if s.category == category]
        return sorted(skills, key=lambda s: (s.category, s.name))

    def categories(self) -> list[str]:
        return sorted({s.category for s in self._skills.values()})

    def get_prompt(self, name: str) -> str:
        return self._prompts.get(name, "")

    # --- execution ---

    def execute(
        self,
        skill_name: str,
        context: dict[str, Any],
        credit_manager: Optional[CreditManager] = None,
    ) -> dict[str, Any]:
        """Execute a skill with optional credit tracking.

        In a real integration this would call the LLM; here it returns
        the assembled prompt payload so callers can forward it.
        """
        cfg = self._skills.get(skill_name)
        if cfg is None:
            raise ValueError(f"Unknown skill: {skill_name}")

        # Route for optimal tier
        self._router._credit_mgr = credit_manager
        decision: RouteDecision = self._router.route(
            task=context.get("task", ""),
            context=context,
            preferred_skill=skill_name,
        )

        if decision.cached:
            result = credit_manager.cache.get(skill_name, context) if credit_manager else None
            if result is not None:
                if credit_manager:
                    credit_manager.record(
                        skill_name=skill_name,
                        tokens_used=0,
                        credit_spent=0,
                        credit_saved=cfg.credit_cost_estimate,
                        model_tier=decision.model_tier,
                        cached=True,
                    )
                return {"result": result, "cached": True, "credit_spent": 0}

        prompt = self._prompts.get(skill_name, "")
        payload = {
            "model_tier": decision.model_tier,
            "system_prompt": prompt,
            "context": context,
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
            "skill": skill_name,
            "estimated_credit": decision.estimated_credit,
        }

        if credit_manager:
            credit_manager.record(
                skill_name=skill_name,
                tokens_used=cfg.max_tokens,
                credit_spent=decision.estimated_credit,
                model_tier=decision.model_tier,
            )

        return payload

    # --- summary ---

    def summary(self) -> dict[str, Any]:
        by_cat: dict[str, int] = {}
        for s in self._skills.values():
            by_cat[s.category] = by_cat.get(s.category, 0) + 1
        return {
            "total_skills": len(self._skills),
            "categories": by_cat,
            "cacheable": sum(1 for s in self._skills.values() if s.cacheable),
            "batch_compatible": sum(1 for s in self._skills.values() if s.batch_compatible),
        }


def main() -> None:
    """CLI entry point."""
    registry = SkillRegistry()
    loaded = registry.load_all()
    info = registry.summary()
    print(f"Loaded {loaded} skills across {len(info['categories'])} categories")
    for cat, count in sorted(info["categories"].items()):
        print(f"  {cat}: {count} skills")
    print(f"Cacheable: {info['cacheable']} | Batch-compatible: {info['batch_compatible']}")


if __name__ == "__main__":
    main()
