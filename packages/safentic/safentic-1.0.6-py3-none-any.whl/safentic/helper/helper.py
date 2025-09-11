from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, Iterable, List, Optional, Union

import requests
from ..config import BASE_API_PATH, API_KEY_ENDPOINT

from .._internal.errors import PolicyValidationError, ReferenceFileError, VerifierError


def validate_api_key(key: str) -> Dict[str, Any]:
    try:
        response = requests.post(
            BASE_API_PATH + API_KEY_ENDPOINT, json={"api_key": key}
        )
        if response.status_code != 200:
            return {"valid": False}
        data = response.json()
        # Ensure dict shape for mypy; if backend returns non-dict, coerce to wrapped data
        if not isinstance(data, dict):
            return {"valid": True, "data": data}
        # Merge as before
        out: Dict[str, Any] = {"valid": True}
        out.update(data)
        return out
    except Exception:
        return {"valid": False}


def require(rule: Dict[str, Any], rid: str, key: str) -> None:
    """Ensure a rule has a required key, else raise PolicyValidationError."""
    if not rule.get(key):
        raise PolicyValidationError(f"{rid}: missing required '{key}'")


def get_text_fields(
    tool_input: Dict[str, Any],
    fields: List[str],
    rid: str,
    logger: Optional[Any] = None,
) -> str:
    """Extract text fields from tool input, log missing ones if logger provided."""
    texts: List[str] = []
    missing: List[str] = []
    for f in fields:
        val = tool_input.get(f)
        if isinstance(val, str):
            texts.append(val)
        else:
            missing.append(f)

    if missing and logger is not None:
        # keep original call signature; annotate logger as Any
        logger.log(
            agent_id="-",
            tool="-schema-",
            allowed=True,
            reason=f"Missing expected fields for {rid}: {missing}",
            extra={"event": "missing_fields", "rule": rid, "missing": missing},
        )
    return "\n".join(texts).strip()


def deny_response(
    tool_name: str,
    state: Dict[str, Any],
    reason: str,
    violation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a standard structured deny response."""
    return {
        "allowed": False,
        "reason": reason,
        "tool": tool_name,
        "agent_state": state,
        "violation": violation or {},
    }


def is_tool_blocked(tool_name: str, state: Dict[str, Any], ttl: int) -> bool:
    """Check if a tool is still blocked based on TTL. Cleans up expired entries."""
    # Expect state["blocked_tools"] to be a dict[str, float]
    blocked_tools = state.get("blocked_tools")
    if not isinstance(blocked_tools, dict):
        return False
    blocked_at = blocked_tools.get(tool_name)
    if not isinstance(blocked_at, (int, float)):
        return False
    if time.time() - float(blocked_at) > ttl:
        # TTL expired → unblock
        try:
            del blocked_tools[tool_name]
        except Exception:
            pass
        return False
    return True


def max_tokens_for_format(fmt: str) -> int:
    """Return max tokens allowed for given response format."""
    if fmt == "boolean":
        return 5
    elif fmt == "string":
        return 50
    elif fmt == "json":
        return 80
    return 40  # default fallback


def check_match(llm_output: str, trigger: str, mode: str) -> bool:
    """
    Determines if the LLM output matches the trigger value.
    Supports: exact, regex, jsonpath.
    """
    try:
        if mode == "exact":
            return llm_output.strip().lower() == trigger.strip().lower()
        elif mode == "regex":
            return re.search(trigger, llm_output, re.IGNORECASE) is not None
        elif mode == "jsonpath":
            from jsonpath_ng.ext import parse

            parsed = parse(trigger).find(json.loads(llm_output))
            return bool(parsed)
    except Exception as e:
        raise VerifierError(f"Failed during match check: {e}") from e

    return False  # unsupported mode


class ReferenceLoader:
    """
    Minimal, predictable reference file resolver with mtime caching.

    Resolution order for a given 'filename':
      1) absolute path -> use as-is
      2) policy_dir / filename
      3) SAFENTIC_REF_BASE / filename   (optional single base for monorepos/CI)

    This keeps v1 simple and transparent. You can extend later if needed.
    """

    def __init__(self, reference_dir: str):
        # Treat this as the policy directory (directory of policy.yaml)
        self.reference_dir: str = os.path.abspath(reference_dir)
        base_env = os.getenv("SAFENTIC_REF_BASE")  # optional single base
        self.ref_base_env: Optional[str] = (
            os.path.abspath(os.path.expanduser(base_env)) if base_env else None
        )

        # mtime cache keyed by absolute path
        self._ref_cache: Dict[str, Dict[str, Union[float, str]]] = {}

    # --------------- public API ---------------

    def load(self, filename: str) -> str:
        """
        Resolve and load the reference file, caching by mtime.
        Raises ReferenceFileError with attempted paths when not found or unreadable/empty.
        """
        candidates = list(self._candidate_paths(filename))

        resolved = next((p for p in candidates if os.path.isfile(p)), None)
        if not resolved:
            details: Dict[str, Any] = {
                "requested": filename,
                "attempted": candidates,
                "hint": "Use a path relative to your policy file, or set SAFENTIC_REF_BASE to a directory that contains your reference docs.",
            }
            raise ReferenceFileError(
                f"Reference file not found: {filename}. Details: {details}"
            )

        mtime = os.path.getmtime(resolved)
        cached = self._ref_cache.get(resolved)
        if cached and cached.get("mtime") == mtime:
            # cached["text"] is a str by construction; help mypy with a cast
            return str(cached.get("text"))

        try:
            with open(resolved, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            raise ReferenceFileError(f"Failed to read reference file {resolved}: {e}")

        if not text.strip():
            raise ReferenceFileError(f"Reference file is empty: {resolved}")

        self._ref_cache[resolved] = {"mtime": mtime, "text": text}
        return text

    def clear_cache(self) -> None:
        self._ref_cache.clear()

    # --------------- internals ---------------

    def _candidate_paths(self, filename: str) -> Iterable[str]:
        # 1) absolute path
        if os.path.isabs(filename):
            yield os.path.abspath(os.path.expanduser(filename))
            return

        # 2) policy_dir / filename
        yield os.path.abspath(os.path.join(self.reference_dir, filename))

        # 3) SAFENTIC_REF_BASE / filename (optional)
        if self.ref_base_env:
            yield os.path.abspath(os.path.join(self.ref_base_env, filename))
