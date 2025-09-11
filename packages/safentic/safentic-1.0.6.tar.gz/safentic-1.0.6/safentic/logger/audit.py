from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional


class AuditLogger:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Minimal, flexible audit logger with text + JSONL outputs.

        Precedence rules
        ----------------
        Enabled:
          1) config["enabled"] (bool)
          2) SAFENTIC_AUDIT_ENABLED env (truthy/falsey; "0","false","no" disable)
          3) SAFE_AUDIT_LOG env ("0" disables; legacy)
          4) default: True

        Paths:
          Text log (human-readable):
            1) config["destination"]
            2) SAFENTIC_LOG_PATH env (or SAFE_LOG_PATH legacy)
            3) default: safentic/logs/txt_logs/safentic_audit.log

          JSONL log (structured):
            1) config["jsonl"]
            2) SAFENTIC_JSON_LOG_PATH env (or SAFE_JSON_LOG_PATH legacy)
            3) default: safentic/logs/json_logs/safentic_audit.jsonl

        Level:
          1) config["level"]
          2) SAFENTIC_LOG_LEVEL env
          3) default: INFO
        """
        cfg: Dict[str, Any] = config or {}

        # --------------------
        # Enabled flag
        # --------------------
        enabled_cfg = cfg.get("enabled")
        enabled_env = os.getenv("SAFENTIC_AUDIT_ENABLED")

        def _is_truthy(v: str) -> bool:
            return str(v).strip().lower() not in {"0", "false", "no", "off", ""}

        if enabled_cfg is not None:
            self.enabled: bool = bool(enabled_cfg)
        elif enabled_env is not None:
            self.enabled = _is_truthy(enabled_env)
        else:
            # legacy disable switch
            self.enabled = os.getenv("SAFE_AUDIT_LOG") != "0"

        # default to True if unset by any path
        if (
            enabled_cfg is None
            and enabled_env is None
            and os.getenv("SAFE_AUDIT_LOG") is None
        ):
            self.enabled = True

        # --------------------
        # Paths (with env overrides)
        # --------------------
        txt_from_cfg = cfg.get("destination")
        txt_from_env = os.getenv("SAFENTIC_LOG_PATH") or os.getenv("SAFE_LOG_PATH")
        self.txt_log_path: str = (
            txt_from_cfg or txt_from_env or "safentic/logs/txt_logs/safentic_audit.log"
        )

        json_from_cfg = cfg.get("jsonl")
        json_from_env = os.getenv("SAFENTIC_JSON_LOG_PATH") or os.getenv(
            "SAFE_JSON_LOG_PATH"
        )
        self.jsonl_path: str = (
            json_from_cfg
            or json_from_env
            or "safentic/logs/json_logs/safentic_audit.jsonl"
        )

        # Ensure directories exist (handle bare filenames)
        txt_dir = os.path.dirname(self.txt_log_path) or "."
        json_dir = os.path.dirname(self.jsonl_path) or "."
        os.makedirs(txt_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)

        # --------------------
        # Logger setup
        # --------------------
        self.logger: logging.Logger = logging.getLogger("safentic.audit")

        # Level with env override
        level_str = (
            cfg.get("level") or os.getenv("SAFENTIC_LOG_LEVEL") or "INFO"
        ).upper()
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = level_map.get(level_str, logging.INFO)
        self.logger.setLevel(level)

        # Avoid duplicate handlers across multiple instantiations:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        # StreamHandler (only one; don't confuse with FileHandler which subclasses StreamHandler)
        if not any(
            isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.FileHandler)
            for h in self.logger.handlers
        ):
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        # FileHandler for the text log (ensure we don't add duplicates for same file)
        desired_file = os.path.abspath(self.txt_log_path)
        has_file_handler = any(
            isinstance(h, logging.FileHandler)
            and getattr(h, "baseFilename", None) == desired_file
            for h in self.logger.handlers
        )
        if not has_file_handler:
            file_handler = logging.FileHandler(self.txt_log_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log(
        self,
        agent_id: str,
        tool: str,
        allowed: bool,
        reason: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Write audit logs to console, file, and JSONL. Supports structured extra metadata."""
        if not self.enabled:
            return

        entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "tool": tool,
            "allowed": allowed,
            "reason": reason or "No violation",
        }

        if extra:
            entry["extra"] = extra  # structured metadata

        log_level = logging.INFO if allowed else logging.WARNING
        self.logger.log(log_level, f"[AUDIT] {entry}")

        try:
            with open(self.jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:  # pragma: no cover - logging fallback path
            # Only log this internal failure to the text logger; do not raise.
            self.logger.error(f"Failed to write structured audit log: {e}")

    def set_level(self, level: str) -> None:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        level_upper = level.upper()
        if level_upper in level_map:
            self.logger.setLevel(level_map[level_upper])
        else:
            raise ValueError(f"Unsupported log level: {level}")
