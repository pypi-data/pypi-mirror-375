import io
import os
import time
from typing import Dict, Any, Optional

from safentic.cli.utils import resolve_log_path, ok, error, print_json


def _stream_tail(path: str) -> None:
    """Follow a file until interrupted (like tail -f)."""
    with open(path, "r", encoding="utf-8") as f:
        f.seek(0, io.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.25)
                continue
            print(line.rstrip())


def run_tail(
    path: Optional[str] = None, follow: bool = False, prefer_json: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Tail logs (defaults to JSONL). If follow=True, stream and do not return a JSON envelope.
    If follow=False, return last 200 lines as a JSON payload.
    """
    resolved_path, source = resolve_log_path(user_path=path, prefer_json=prefer_json)

    if not os.path.exists(resolved_path):
        return error(
            "Log file not found",
            {
                "path": resolved_path,
                "resolved_from": source,
                "hint": "Generate logs via agent or check-tool first.",
            },
        )

    if follow:
        # Emit a one-time prelude so users know what is being tailed
        print_json(
            ok("Following log file", {"path": resolved_path, "resolved_from": source})
        )
        try:
            _stream_tail(resolved_path)
        except KeyboardInterrupt:
            return None
        return None

    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-200:]
        return ok(
            "Fetched recent logs",
            {
                "path": resolved_path,
                "resolved_from": source,
                "lines": [ln.rstrip() for ln in lines],
            },
        )
    except Exception as e:
        return error(
            "Failed to read log file",
            {"path": resolved_path, "resolved_from": source, "details": str(e)},
        )
