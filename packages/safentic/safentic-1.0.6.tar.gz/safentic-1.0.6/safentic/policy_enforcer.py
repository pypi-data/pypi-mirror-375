import time
from typing import (
    Any,
    Dict,
    Optional,
)

from .policy_engine import PolicyEngine
from .logger.audit import AuditLogger
from ._internal.errors import EnforcementError
from .helper.helper import deny_response, is_tool_blocked


class PolicyEnforcer:
    """
    Runtime wrapper to evaluate and enforce tool usage policies.
    Tracks agent-specific violations, supports audit logging,
    and handles TTL-based tool blocks.

    Requires a PolicyEngine instance at construction (no implicit defaults).
    """

    TOOL_BLOCK_TTL = 60  # seconds

    def __init__(
        self, policy_engine: PolicyEngine, audit_logger: Optional[AuditLogger] = None
    ) -> None:
        if not isinstance(policy_engine, PolicyEngine):
            raise EnforcementError(
                "PolicyEnforcer requires a valid PolicyEngine instance"
            )

        self.policy_engine = policy_engine
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.audit_logger = audit_logger or AuditLogger()

    def enforce(
        self, agent_id: str, tool_name: str, tool_args: dict[Any, Any]
    ) -> dict[Any, Any]:
        """
        Evaluates a tool action for a given agent.
        Returns a dict[Any, Any] with 'allowed', 'reason', and agent state metadata.
        """
        try:
            state = self.agent_states.setdefault(
                agent_id,
                {
                    "blocked_tools": {},  # tool_name -> timestamp of block
                    "violation_count": 0,
                    "last_violation": None,
                },
            )

            # 1) TTL check
            if is_tool_blocked(tool_name, state, self.TOOL_BLOCK_TTL):
                reason = "Tool is temporarily blocked due to a prior violation."
                self.audit_logger.log(
                    agent_id=agent_id, tool=tool_name, allowed=False, reason=reason
                )
                return deny_response(tool_name, state, reason)

            # 2) Policy evaluation
            violation = self.policy_engine.evaluate_policy(
                tool_name, tool_args, agent_id=agent_id
            )
            if violation:
                level = violation.get("level", "block")
                reason = violation.get("reason", "Policy violation")

                # --- FIX: handle boolean violation reasons gracefully ---
                if isinstance(reason, bool):
                    reason = "Policy violation (boolean trigger)"

                if level == "warn":
                    self.audit_logger.log(
                        agent_id=agent_id,
                        tool=tool_name,
                        allowed=True,
                        reason=f"Warning: {reason}",
                    )
                    return {
                        "allowed": True,
                        "reason": f"Warning: {reason}",
                        "violation": violation,
                        "agent_state": state,
                    }

                # Block
                state["blocked_tools"][tool_name] = time.time()
                state["violation_count"] += 1
                state["last_violation"] = violation

                self.audit_logger.log(
                    agent_id=agent_id, tool=tool_name, allowed=False, reason=reason
                )
                return deny_response(tool_name, state, reason, violation)

            # 3) Allowed
            self.audit_logger.log(agent_id=agent_id, tool=tool_name, allowed=True)
            return {
                "allowed": True,
                "reason": "Action permitted",
                "agent_state": state,
            }

        except Exception as e:
            raise EnforcementError(
                f"Failed to enforce policy for {tool_name}: {e}"
            ) from e

    def reset(self, agent_id: Optional[str] = None) -> None:
        """Clears violation state for one or all agents."""
        if agent_id:
            self.agent_states.pop(agent_id, None)
        else:
            self.agent_states.clear()
