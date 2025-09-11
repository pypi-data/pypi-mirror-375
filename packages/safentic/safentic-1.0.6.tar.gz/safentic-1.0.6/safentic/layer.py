from typing import Any, Protocol
import os
from dotenv import load_dotenv

from .policy_enforcer import PolicyEnforcer
from .logger.audit import AuditLogger
from .helper.helper import validate_api_key
from .policy_engine import PolicyEngine
from ._internal.errors import (
    SafenticError,
    InvalidAPIKeyError,
    InvalidAgentInterfaceError,
)

load_dotenv()


class AgentProtocol(Protocol):
    """Minimal interface expected from a wrapped agent."""

    def call_tool(self, tool_name: str, **kwargs: Any) -> dict[str, Any]: ...


class SafetyLayer:
    """
    Developer-facing wrapper that enforces Safentic policies around an agent.
    All tool calls must go through `call_tool()`.
    """

    def __init__(
        self,
        agent: AgentProtocol,
        api_key: str,
        agent_id: str = "",
        raise_on_block: bool = True,
    ) -> None:
        if not api_key:
            raise InvalidAPIKeyError("Missing API key")

        validation_response = validate_api_key(api_key)
        if not validation_response or validation_response.get("status") != "valid":
            raise InvalidAPIKeyError("Invalid or unauthorized API key")

        if not hasattr(agent, "call_tool") or not callable(getattr(agent, "call_tool")):
            raise InvalidAgentInterfaceError(
                "Wrapped agent must implement `call_tool(tool_name: str, **kwargs)`"
            )

        self.agent: AgentProtocol = agent
        self.api_key: str = api_key
        self.agent_id: str = agent_id
        self.raise_on_block: bool = raise_on_block
        self.logger: AuditLogger = AuditLogger()

        # Decide where policy.yaml lives (env var > default repo path)
        policy_path = os.getenv(
            "SAFENTIC_POLICY_PATH",
            os.path.join(
                os.path.dirname(__file__), "..", "policy_file_docs", "policy.yaml"
            ),
        )

        # Build engine and inject API key to verifier
        engine = PolicyEngine(policy_path=policy_path)
        engine.llm.set_api_key(api_key)

        # Strict enforcer injection
        self.enforcer = PolicyEnforcer(policy_engine=engine)
        self.enforcer.reset(agent_id)

    def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """
        Intercepts a tool call and enforces policies before execution.
        If blocked, raises `SafenticError` or returns an error response (configurable).
        """
        result: dict[str, Any] = self.enforcer.enforce(
            self.agent_id, tool_name, tool_args
        )

        self.logger.log(
            agent_id=self.agent_id,
            tool=tool_name,
            allowed=result["allowed"],
            reason=result["reason"] if not result["allowed"] else None,
        )

        if not result["allowed"]:
            if self.raise_on_block:
                raise SafenticError(result["reason"])
            return {
                "error": result["reason"],
                "tool": tool_name,
                "violation": result.get("violation"),
            }

        return self.agent.call_tool(tool_name, **tool_args)
