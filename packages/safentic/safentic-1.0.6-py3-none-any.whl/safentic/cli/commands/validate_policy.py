import os
from typing import Any, Dict, Optional

from safentic.policy_engine import PolicyEngine
from safentic.cli.utils import resolve_policy_path, ok, error
import yaml


def run(
    policy: Optional[str] = None,
    dry_run: bool = False,
    strict: bool = False,
    no_llm: bool = False,
) -> Dict[str, Any]:
    """Validate a policy file using the SDK loader/validator."""
    policy_path = resolve_policy_path(policy)

    if not os.path.exists(policy_path):
        return error(
            f"Policy validation failed for {policy_path}",
            {"details": f"Policy file not found: {policy_path}"},
        )

    try:
        engine = PolicyEngine(policy_path=policy_path, dry_run=dry_run, no_llm=no_llm)
        tools_cfg: Dict[str, Any] = engine.policy_cfg.get("tools", {}) or {}
        tool_count = len(tools_cfg)
        rule_count = sum(
            len((cfg or {}).get("rules", [])) for cfg in tools_cfg.values()
        )

        missing_refs: list[str] = []
        if strict:
            with open(policy_path, "r") as f:
                policy_yaml = yaml.safe_load(f)
            for tool in policy_yaml.get("tools", {}).values():
                for rule in tool.get("rules", []):
                    ref_file = rule.get("reference_file")
                    if ref_file and not os.path.exists(ref_file):
                        missing_refs.append(ref_file)
            if missing_refs:
                return error(
                    "Policy validation failed: missing reference files.",
                    {"missing_files": missing_refs},
                )

        return ok(
            "Policy validated successfully.",
            {
                "policy_path": os.path.abspath(policy_path),
                "tools": tool_count,
                "rules": rule_count,
                "dry_run": engine.dry_run,
                "no_llm": no_llm,
                "strict": strict,
            },
        )
    except Exception as e:
        return error(f"Policy validation failed for {policy_path}", {"details": str(e)})
