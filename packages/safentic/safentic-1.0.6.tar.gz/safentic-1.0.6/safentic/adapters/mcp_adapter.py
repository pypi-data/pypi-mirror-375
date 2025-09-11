from typing import Any, Dict, Mapping, cast
from safentic.policy_enforcer import PolicyEnforcer


def handle_mcp_action(
    action_request: Mapping[str, Any], enforcer: PolicyEnforcer
) -> Dict[str, Any]:
    """
    Accepts an MCP ActionRequest and returns a Safentic policy enforcement result.
    Requires a PolicyEnforcer instance to be passed in.

    Expected shape (minimal):
    {
        "tool": {
            "name": str,
            "input": dict[str, Any]
        },
        "agent": {
            "id": str
        }
    }
    """

    tool: Dict[str, Any] = cast(Dict[str, Any], action_request.get("tool", {}))
    agent: Dict[str, Any] = cast(Dict[str, Any], action_request.get("agent", {}))

    tool_name: str = cast(str, tool.get("name", "unknown_tool"))
    tool_args: Dict[str, Any] = cast(
        Dict[str, Any], tool.get("input", {})
    )  # Expected to include "body" or "note"
    agent_id: str = cast(str, agent.get("id", "unknown_agent"))

    result: Dict[str, Any] = enforcer.enforce(
        agent_id=agent_id,
        tool_name=tool_name,
        tool_args=tool_args,
    )

    return {
        "tool": tool_name,
        "agent_id": agent_id,
        "allowed": result["allowed"],
        "reason": result["reason"],
        "agent_state": result.get("agent_state", {}),
        "violation": result.get("violation"),  # Optional violation metadata
    }
