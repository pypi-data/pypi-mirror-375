import argparse
import sys
from typing import Any, Optional, Dict

from safentic.cli.commands.validate_policy import run as run_validate
from safentic.cli.commands.check_tool import run as run_check
from safentic.cli.commands.logs import run_tail as run_logs_tail
from safentic.cli.utils import print_output, set_output_mode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="safentic",
        description="Safentic CLI — validate policies, simulate tool checks, and tail audit logs.",
    )
    parser.add_argument("--version", action="version", version="safentic-cli 0.1.0")

    # Common flags available on each subcommand
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--policy", help="Path to policy.yaml (overrides SAFENTIC_POLICY_PATH)"
    )
    common.add_argument(
        "--dry-run", action="store_true", help="Simulate enforcement (never block)"
    )
    common.add_argument(
        "--json", action="store_true", help="Output machine-readable JSON"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # validate-policy
    p_val = sub.add_parser(
        "validate-policy",
        help="Validate a policy file and references",
        parents=[common],
        add_help=True,
    )
    p_val.add_argument(
        "--strict",
        action="store_true",
        help="Fail if reference_file paths do not exist",
    )
    p_val.add_argument(
        "--no-llm", action="store_true", help="Skip LLM-based checks for speed"
    )
    p_val.set_defaults(cmd="validate-policy")

    # check-tool
    p_chk = sub.add_parser(
        "check-tool",
        help="Run a one-off enforcement for a tool + JSON input",
        parents=[common],
        add_help=True,
    )
    p_chk.add_argument(
        "--tool", required=True, help="Tool name to check (e.g., issue_refund)"
    )
    p_chk.add_argument(
        "--agent-id", default="cli-agent", help="Agent ID (default: cli-agent)"
    )
    g = p_chk.add_mutually_exclusive_group()
    g.add_argument("--input-json", help="Raw JSON string for tool input")
    g.add_argument("--input-file", help="Path to JSON file for tool input")
    p_chk.add_argument(
        "--allow-fail",
        action="store_true",
        help="Exit code 0 even if blocked (local dev)",
    )
    p_chk.add_argument(
        "--no-llm", action="store_true", help="Skip LLM-based checks for speed"
    )
    p_chk.set_defaults(cmd="check-tool")

    # logs (tail)
    p_logs = sub.add_parser("logs", help="Work with audit logs")
    sub_logs = p_logs.add_subparsers(dest="logs_cmd", required=True)

    p_tail = sub_logs.add_parser(
        "tail",
        help="Tail the audit log (JSONL by default)",
        parents=[common],
        add_help=True,
    )
    p_tail.add_argument("--path", help="Path to the log file (overrides env/config)")
    p_tail.add_argument(
        "-f",
        "--follow",
        action="store_true",
        help="Follow appended lines (like tail -f)",
    )
    p_tail.set_defaults(cmd="logs:tail")

    return parser


def _maybe_exit_on_error(payload: Optional[Dict[str, Any]]) -> None:
    """Exit with code 1 if payload indicates an error."""
    if payload is not None and not payload.get("ok", False):
        sys.exit(1)


def main(argv: Optional[list[Any]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload: Dict[str, Any] = {}
    # Set global output mode
    set_output_mode(getattr(args, "json", False))

    if args.command == "validate-policy":
        payload = run_validate(
            policy=args.policy,
            dry_run=getattr(args, "dry_run", False),
            strict=getattr(args, "strict", False),
            no_llm=getattr(args, "no_llm", False),
        )
        print_output(payload)
        _maybe_exit_on_error(payload)
        return

    if args.command == "check-tool":
        try:
            payload = run_check(
                policy=args.policy,
                tool_name=args.tool,
                agent_id=args.agent_id,
                input_json=getattr(args, "input_json", None),
                input_file=getattr(args, "input_file", None),
                dry_run=getattr(args, "dry_run", False),
                allow_fail=getattr(args, "allow_fail", False),
                no_llm=getattr(args, "no_llm", False),
            )
            print_output(payload)
            _maybe_exit_on_error(payload)
        except SystemExit:
            # allow exit code 2 (blocked) to propagate for CI
            raise
        return

    if args.command == "logs" and args.logs_cmd == "tail":
        log_payload: Optional[Dict[str, Any]] = run_logs_tail(
            path=getattr(args, "path", None),
            follow=getattr(args, "follow", False),
            prefer_json=True,
        )
        if log_payload is not None:
            print_output(log_payload)
        _maybe_exit_on_error(log_payload)
        return


if __name__ == "__main__":
    main()
