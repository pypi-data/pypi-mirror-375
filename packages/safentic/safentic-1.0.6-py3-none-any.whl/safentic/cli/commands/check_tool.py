from typing import Any, Dict, Optional

from safentic.policy_engine import PolicyEngine
from safentic.policy_enforcer import PolicyEnforcer
from safentic.cli.utils import resolve_policy_path, load_json_arg, ok, error


def run(
    policy: Optional[str],
    tool_name: str,
    agent_id: str,
    input_json: Optional[str],
    input_file: Optional[str],
    dry_run: bool,
    allow_fail: bool,
    no_llm: bool = False,
) -> Dict[str, Any]:
    """
    Run a one-off policy enforcement for a tool + payload.
    Returns a JSON payload. Raises SystemExit(2) if blocked and allow_fail=False.
    """
    policy_path = resolve_policy_path(policy)

    try:
        engine = PolicyEngine(policy_path=policy_path, dry_run=dry_run, no_llm=no_llm)
        enforcer = PolicyEnforcer(policy_engine=engine)

        payload: Dict[str, Any] = load_json_arg(input_json, input_file)
        decision = enforcer.enforce(
            agent_id=agent_id, tool_name=tool_name, tool_args=payload
        )

        result = ok(
            f"Check completed for tool: {tool_name}",
            {"policy_path": policy_path, "decision": decision},
        )

        if not decision.get("allowed", False) and not allow_fail:
            # Signal to CI callers that this is a block
            raise SystemExit(2)

        return result

    except SystemExit:
        raise
    except Exception as e:
        return error("check-tool failed", {"details": str(e)})
