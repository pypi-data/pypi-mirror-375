from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Optional, Union

from openai import OpenAI
from ..logger.audit import AuditLogger


JSONDict = Dict[str, Any]
LLMOut = Union[str, bool, JSONDict]


class LLMVerifier:
    """
    Evaluates agent tool output using an LLM to determine policy compliance.
    Controlled entirely by developer-authored rules in policy.yaml.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set and no api_key provided.")
        self.client: OpenAI = OpenAI(api_key=self.api_key)
        self.logger: AuditLogger = AuditLogger()

    def set_api_key(self, api_key: str) -> None:
        """Allows runtime injection of the API key (e.g., from SafetyLayer)."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    # -------------------------
    # Formatting helpers
    # -------------------------

    def max_tokens_for_format(self, fmt: str) -> int:
        fmt_l = (fmt or "").lower()
        if fmt_l == "boolean":
            return 5
        if fmt_l == "string":
            return 50
        if fmt_l == "json":
            return 80
        return 40  # default fallback

    def _to_bool(self, value: Union[str, bool]) -> bool:
        """Normalize a string/bool into a boolean."""
        if isinstance(value, bool):
            return value
        v = value.strip().lower()
        return v in ("yes", "true", "1")

    def _normalize_output(self, raw: str, response_format: str) -> LLMOut:
        """
        Coerce the model output into the expected response_format.

        - boolean: returns True/False
        - string: returns a trimmed string
        - json:   returns a dict (if parseable), else raises
        """
        fmt = (response_format or "string").lower()

        if fmt == "boolean":
            # accept "yes"/"true"/"1" as True; "no"/"false"/"0" as False
            return self._to_bool(raw)

        if fmt == "json":
            try:
                parsed = json.loads(raw)
            except Exception as e:
                raise ValueError(f"Expected JSON from model but failed to parse: {e}")
            if not isinstance(parsed, dict):
                raise ValueError("Expected a JSON object (dict) from model.")
            return parsed

        # default string
        return raw.strip()

    # -------------------------
    # Matching helpers
    # -------------------------

    def _check_match(
        self,
        llm_output: LLMOut,
        trigger: str,
        mode: str,
        response_format: str,
    ) -> bool:
        """
        Determine if the normalized model output matches the trigger using the chosen mode.
        - For boolean response_format, we compare booleans directly.
        - For string, we support exact/contains/regex.
        - For json, you can use 'jsonpath' (optional) or fallback to string contains on the canonicalized JSON.
        """
        fmt = (response_format or "string").lower()
        mode_l = (mode or "exact").lower()

        if fmt == "boolean":
            # Map trigger -> boolean and compare directly.
            out_bool = (
                llm_output
                if isinstance(llm_output, bool)
                else self._to_bool(str(llm_output))
            )
            trig_bool = self._to_bool(str(trigger))
            return out_bool is trig_bool

        if fmt == "json":
            if mode_l == "jsonpath":
                try:
                    from jsonpath_ng.ext import parse

                    results = parse(trigger).find(
                        llm_output if isinstance(llm_output, dict) else {}
                    )
                    return bool(results)
                except Exception:
                    return False
            # fallback: contains over a stable string form of the json
            s = (
                json.dumps(llm_output, separators=(",", ":"), ensure_ascii=False)
                if isinstance(llm_output, dict)
                else str(llm_output)
            )
            return str(trigger).lower() in s.lower()

        # string-like matching
        s = str(llm_output).strip()
        trig = str(trigger).strip()
        if mode_l == "exact":
            return s.lower() == trig.lower()
        if mode_l == "contains":
            return trig.lower() in s.lower()
        if mode_l == "regex":
            try:
                return re.search(trig, s, re.IGNORECASE) is not None
            except re.error:
                return False
        # default conservative
        return False

    # -------------------------
    # Public API
    # -------------------------

    def evaluate(
        self,
        instruction: str,
        agent_output: str,
        reference_text: str,
        rule: Dict[str, Any],
        tool: str,
        agent_id: str,
    ) -> Dict[str, Any]:
        """
        Performs LLM evaluation and returns structured result.
        Never raises for trigger mismatches; only raises for fatal formatting errors.
        """
        response_format: str = rule.get("response_format", "boolean")
        match_mode: str = rule.get("match_mode", "exact")
        response_trigger: str = rule.get("response_trigger", "yes")
        level: str = rule.get("level", "block")
        severity: str = rule.get("severity", "medium")
        reference_filename: Optional[str] = rule.get("reference_file")
        model_name: str = rule.get("model", "gpt-4")

        prompt = f"""{instruction}

Agent Response:
{agent_output}

Company Policy:
{reference_text}

Respond only with: {response_format}"""

        try:
            res = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compliance checker for internal company policy.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens_for_format(response_format),
                temperature=0,
            )

            raw_text = (res.choices[0].message.content or "").strip()

            # Normalize into the declared format
            normalized = self._normalize_output(raw_text, response_format)

            # Perform trigger check safely for str/bool/json
            matched = self._check_match(
                llm_output=normalized,
                trigger=response_trigger,
                mode=match_mode,
                response_format=response_format,
            )

        except Exception as e:
            # Surface a clear, single-line reason to upstream callers
            raise RuntimeError(f"LLM evaluation failed: {e}") from e

        if matched:
            reason = (
                f"LLM rule triggered (trigger='{response_trigger}', "
                f"mode='{match_mode}', fmt='{response_format}')"
            )
            self.logger.log(
                agent_id=agent_id, tool=tool, allowed=(level != "block"), reason=reason
            )
            return {
                "level": level,
                "severity": severity,
                "matched_value": (
                    normalized if not isinstance(normalized, dict) else "[json]"
                ),
                "reference_file": reference_filename,
                "description": rule.get("description", ""),
                "tags": rule.get("tags", []),
                "reason": reason,
            }

        # No match → allow
        self.logger.log(
            agent_id=agent_id,
            tool=tool,
            allowed=True,
            reason="No match",
        )
        return {}
