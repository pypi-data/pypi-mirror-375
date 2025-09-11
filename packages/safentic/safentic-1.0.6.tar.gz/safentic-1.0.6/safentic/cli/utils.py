import os
import json
from typing import Any, Dict, Optional, Tuple

# -------------------------------------------------
# Output formatting
# -------------------------------------------------

_OUTPUT_JSON = False  # default: pretty (plain) output


def set_output_mode(json_mode: bool) -> None:
    """Set global output mode for the CLI."""
    global _OUTPUT_JSON
    _OUTPUT_JSON = bool(json_mode)


def ok(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"ok": True, "message": message, "data": data or {}}


def error(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"ok": False, "message": message, "error": data or {}}


def _pretty(payload: Dict[str, Any]) -> str:
    if payload.get("ok", True):
        msg = f"{payload.get('message','OK')}"
        data = payload.get("data") or {}
        if data:
            parts = []
            for k, v in data.items():
                if isinstance(v, (list, tuple)):
                    if k == "lines":
                        parts.append(f"{k}:\n" + "\n".join(str(x) for x in v))
                    else:
                        parts.append(f"{k}: {len(v)} items")
                elif isinstance(v, dict):
                    # Show small dicts inline, otherwise key count
                    items = ", ".join(f"{ik}={iv}" for ik, iv in list(v.items())[:6])
                    suffix = "" if len(v) <= 6 else ", …"
                    parts.append(f"{k}: {items}{suffix}")
                else:
                    parts.append(f"{k}: {v}")
            if parts:
                return msg + "\n" + "\n".join(parts)
        return msg
    else:
        msg = f"{payload.get('message','Error')}"
        err = payload.get("error") or {}
        if err:
            try:
                return msg + "\n" + json.dumps(err, indent=2)
            except Exception:
                return msg + "\n" + str(err)
        return msg


def print_output(payload: Dict[str, Any]) -> None:
    if _OUTPUT_JSON:
        print(json.dumps(payload, indent=2))
    else:
        print(_pretty(payload))


def print_json(payload: Dict[str, Any]) -> None:
    """Sometimes needed for streaming prelude messages."""
    print(json.dumps(payload, indent=2))


# -------------------------------------------------
# Helpers: policy & logs path resolution, input loading
# -------------------------------------------------


def resolve_policy_path(arg_path: Optional[str]) -> str:
    """
    Precedence:
      1) --policy (arg)
      2) SAFENTIC_POLICY_PATH (env)
      3) repo default: config/policy.yaml
    """
    if arg_path:
        return os.path.abspath(arg_path)
    env_path = os.getenv("SAFENTIC_POLICY_PATH")
    if env_path:
        return os.path.abspath(env_path)
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "config", "policy.yaml")
    )


def load_json_arg(
    input_json: Optional[str], input_file: Optional[str]
) -> Dict[str, Any]:
    """Load JSON from either a raw string or a file path (mutually exclusive).
    Ensures the top-level value is a JSON object (dict).
    """
    if input_json and input_file:
        raise ValueError("Provide either --input-json OR --input-file, not both.")

    parsed: Any = None
    if input_json:
        try:
            parsed = json.loads(input_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in --input-json: {e}") from e
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(
            'Expected a JSON object for --input-json (e.g., {"key": "value"}).'
        )

    if input_file:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            try:
                parsed = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in --input-file: {e}") from e
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(
            "Expected a JSON object in --input-file (top-level must be an object)."
        )

    return {}


def resolve_log_path(
    user_path: Optional[str] = None, prefer_json: bool = True
) -> Tuple[str, str]:
    """
    Resolve log path dynamically with precedence:
      1) explicit --path (user_path)
      2) environment variables (SAFENTIC_JSON_LOG_PATH / SAFENTIC_LOG_PATH / SAFE_JSON_LOG_PATH / SAFE_LOG_PATH)
      3) AuditLogger config (jsonl_path / txt_log_path)
      4) repo default fallback under safentic/logs/...
    Returns (resolved_path, source_hint).
    """
    if user_path:
        return os.path.abspath(user_path), "cli_arg"

    env_keys_json = ["SAFENTIC_JSON_LOG_PATH", "SAFE_JSON_LOG_PATH"]
    env_keys_txt = ["SAFENTIC_LOG_PATH", "SAFE_LOG_PATH"]
    for key in env_keys_json if prefer_json else env_keys_txt:
        val = os.getenv(key)
        if val:
            return os.path.abspath(val), f"env:{key}"

    # Try AuditLogger configuration (lazy import)
    try:
        from safentic.logger.audit import AuditLogger

        logger = AuditLogger()
        resolved = logger.jsonl_path if prefer_json else logger.txt_log_path
        if resolved:
            return os.path.abspath(resolved), "audit_logger"
    except Exception:
        pass

    # Fallback
    fallback = (
        os.path.join("safentic", "logs", "json_logs", "safentic_audit.jsonl")
        if prefer_json
        else os.path.join("safentic", "logs", "txt_logs", "safentic_audit.log")
    )
    return os.path.abspath(fallback), "fallback"
