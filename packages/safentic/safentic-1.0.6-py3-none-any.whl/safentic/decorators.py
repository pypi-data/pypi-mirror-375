# safentic/decorators.py

from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

from safentic.adapters.mcp_adapter import handle_mcp_action
from safentic.policy_engine import PolicyEngine
from safentic.policy_enforcer import PolicyEnforcer

engine = PolicyEngine(policy_path="config/policy.yaml")
enforcer = PolicyEnforcer(policy_engine=engine)

P = ParamSpec("P")
R = TypeVar("R")


def enforce(
    tool_name: str, agent_id: str = "default-agent"
) -> Callable[[Callable[P, R]], Callable[P, R | str]]:
    """
    Decorator that routes tool calls through Safentic via MCP.

    Note: The wrapped function may return its original type R, or a str when blocked.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R | str]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | str:
            tool_input: dict[str, Any] = kwargs or {"note": args[0]} if args else {}

            action_request: dict[str, Any] = {
                "tool": {"name": tool_name, "input": tool_input},
                "agent": {"id": agent_id},
            }

            # 🔹 Always pass the enforcer
            result: dict[str, Any] = handle_mcp_action(action_request, enforcer)

            if not result["allowed"]:
                print(
                    f"\n[BLOCKED by Safentic] {tool_name.upper()} — {result['reason']}"
                )
                return f"[BLOCKED] {result['reason']}"

            return func(*args, **kwargs)

        return wrapper

    return decorator
