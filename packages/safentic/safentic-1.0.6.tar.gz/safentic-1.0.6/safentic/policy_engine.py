import os
import yaml
from typing import Optional, Dict, Any

from .verifiers.llm_verifier import LLMVerifier
from .logger.audit import AuditLogger
from ._internal.errors import PolicyValidationError
from .helper.helper import require, get_text_fields, ReferenceLoader


class PolicyEngine:
    """
    Loads and evaluates policies defined in YAML.
    Orchestrates verifiers and returns unified decision objects.
    """

    VALID_RULE_TYPES = {"llm_verifier"}
    VALID_LEVELS = {"block", "warn"}  # enforcement levels
    VALID_RESP_FORMAT = {"boolean"}
    VALID_MATCH_MODE = {"exact", "contains"}

    def __init__(
        self,
        policy_path: str,
        logger: Optional[AuditLogger] = None,
        dry_run: bool = False,
        no_llm: bool = False,  # <-- Added flag
    ):
        if not policy_path:
            raise PolicyValidationError("Policy path must be provided to PolicyEngine")

        self.policy_path = policy_path
        self.logger = logger or AuditLogger()
        self.dry_run = dry_run
        self.no_llm = no_llm  # <-- Store flag

        self.policy_cfg = self._load_policy()
        self._validate_policy_cfg()

        reference_dir = os.path.dirname(os.path.abspath(self.policy_path)) or "."
        self.ref_loader = ReferenceLoader(reference_dir)
        self.llm = LLMVerifier()

    def _load_policy(self) -> Dict[str, Any]:
        try:
            with open(self.policy_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise PolicyValidationError(f"Policy file not found: {self.policy_path}")
        except yaml.YAMLError as e:
            raise PolicyValidationError(f"Invalid YAML in {self.policy_path}: {e}")

    def _validate_policy_cfg(self) -> None:
        tools = self.policy_cfg.get("tools")
        if not isinstance(tools, dict):
            raise PolicyValidationError(
                "policy.tools must be a mapping of tool names to configs"
            )

        for tool_name, cfg in tools.items():
            rules = cfg.get("rules", [])
            if not isinstance(rules, list):
                raise PolicyValidationError(f"{tool_name}.rules must be a list")

            for idx, rule in enumerate(rules):
                rid = f"{tool_name}[{idx}]"
                rtype = rule.get("type")
                if rtype not in self.VALID_RULE_TYPES:
                    raise PolicyValidationError(f"{rid}: unknown type '{rtype}'")

                if rtype == "llm_verifier":
                    require(rule, rid, "instruction")
                    require(rule, rid, "fields")
                    require(rule, rid, "reference_file")

                    fields = rule["fields"]
                    if not isinstance(fields, list) or not all(
                        isinstance(x, str) for x in fields
                    ):
                        raise PolicyValidationError(
                            f"{rid}: 'fields' must be a list[str]"
                        )

                    if (
                        rule.get("response_format", "boolean")
                        not in self.VALID_RESP_FORMAT
                    ):
                        raise PolicyValidationError(f"{rid}: invalid response_format")

                    if rule.get("match_mode", "exact") not in self.VALID_MATCH_MODE:
                        raise PolicyValidationError(f"{rid}: invalid match_mode")

                    if rule.get("level", "block") not in self.VALID_LEVELS:
                        raise PolicyValidationError(f"{rid}: invalid level")

    def evaluate_policy(
        self, tool_name: str, tool_input: Dict[str, Any], agent_id: str
    ) -> Optional[Dict[str, Any]]:
        tools_cfg = self.policy_cfg.get("tools", {})
        tool_cfg = tools_cfg.get(tool_name, {})
        rules = tool_cfg.get("rules", [])

        for rule in rules:
            rtype = rule.get("type")
            if rtype not in self.VALID_RULE_TYPES:
                continue

            if rtype == "llm_verifier":
                if self.no_llm:
                    continue  # <-- Skip LLM checks if flag is set

                fields = rule.get("fields", [])
                rid = f"{tool_name}:{rule.get('description','llm_verifier')}"
                text = get_text_fields(tool_input, fields, rid=rid, logger=self.logger)
                if not text:
                    continue

                reference = self.ref_loader.load(rule["reference_file"])
                result = self.llm.evaluate(
                    instruction=rule["instruction"],
                    agent_output=text,
                    reference_text=reference,
                    rule=rule,
                    tool=tool_name,
                    agent_id=agent_id,
                )

                if result:
                    if self.dry_run:
                        result["reason"] = "[DRY_RUN] " + result["reason"]
                        self.logger.log(
                            agent_id,
                            tool_name,
                            allowed=True,
                            reason=result["reason"],
                            extra=result,
                        )
                        return None
                    return result

        return None
