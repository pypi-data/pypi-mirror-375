from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Optional, List
import os, json
from time import perf_counter
from pathlib import Path
from dotenv import load_dotenv  # make sure python-dotenv is installed

# Internal SDK imports (OK for first-party POC)
from safentic.policy_engine import PolicyEngine
from safentic.policy_enforcer import PolicyEnforcer
from safentic.logger.audit import AuditLogger
from safentic._internal.errors import SafenticError

# -------- Load .env --------
# backend/api/main.py → go up 2 levels to reach safentic_poc/backend/.env
BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_ROOT / ".env")

def resolve_path(env_var: str, default_rel: str) -> str:
    """
    Resolve a path from an env var or fall back to a repo-relative default.
    If env var is absolute, return as-is.
    """
    val = os.getenv(env_var)
    if val:
        return str((REPO_ROOT / val).resolve()) if not os.path.isabs(val) else val
    return str((REPO_ROOT / default_rel).resolve())

# -------- Config --------
FE_ORIGIN = os.getenv("FE_ORIGIN", "http://localhost:3000")
POLICY_PATH = resolve_path("SAFENTIC_POLICY_PATH", "config/policy.yaml")

# Default: use JSON logs under safentic_poc/safentic/logs/json_logs
AUDIT_LOG_PATH = resolve_path(
    "SAFENTIC_AUDIT_LOG",
    "safentic_poc/backend/safentic/logs/json_logs/safentic_audit.jsonl",
)

print("ENV says:", os.getenv("SAFENTIC_AUDIT_LOG"))
print("Resolved AUDIT_LOG_PATH:", AUDIT_LOG_PATH)

# -------- App & CORS --------
app = FastAPI(title="Safentic POC API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FE_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Instantiate engine/enforcer/logger --------
engine = PolicyEngine(policy_path=POLICY_PATH)
enforcer = PolicyEnforcer(policy_engine=engine)
logger = AuditLogger()

# -------- Schemas --------
class Options(BaseModel):
    dry_run: bool = False
    no_llm: bool = False

class EnforceRequest(BaseModel):
    tool_name: str
    agent_id: str = Field(default="fe-demo")
    input: dict[str, Any] = Field(default_factory=dict)
    options: Options = Options()

class EnforceResponse(BaseModel):
    allowed: bool
    reason: str
    violation: Optional[dict] = None
    agent_state: Optional[dict] = None
    rule_id: Optional[str] = None
    took_ms: int

class LogEntry(BaseModel):
    ts: str
    agent_id: str
    tool: str
    allowed: bool
    reason: Optional[str] = None
    rule_id: Optional[str] = None

class LogTailResponse(BaseModel):
    items: List[LogEntry]

# -------- Routes --------
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/enforce", response_model=EnforceResponse)
def enforce(req: EnforceRequest):
    if hasattr(enforcer, "reset"):
        try:
            enforcer.reset(req.agent_id)
        except Exception:
            pass

    t0 = perf_counter()
    try:
        result = enforcer.enforce(req.agent_id, req.tool_name, req.input)
    except SafenticError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    took_ms = int((perf_counter() - t0) * 1000)

    try:
        logger.log(
            agent_id=req.agent_id,
            tool=req.tool_name,
            allowed=bool(result.get("allowed", False)),
            reason=result.get("reason"),
            rule_id=result.get("rule_id"),
        )
    except Exception:
        pass

    return {
        "allowed": bool(result.get("allowed")),
        "reason": result.get("reason", ""),
        "violation": result.get("violation"),
        "agent_state": result.get("agent_state"),
        "rule_id": result.get("rule_id"),
        "took_ms": took_ms,
    }

@app.get("/api/logs/tail", response_model=LogTailResponse)
def logs_tail(limit: int = 100):
    items: List[LogEntry] = []
    try:
        print(f"Audit log path: {AUDIT_LOG_PATH}")
        if os.path.exists(AUDIT_LOG_PATH):
            with open(AUDIT_LOG_PATH, "r") as f:
                lines = f.readlines()[-limit:]
            print(f"Read {len(lines)} lines from {AUDIT_LOG_PATH}")
            for ln in lines:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    j = json.loads(ln)
                    items.append(LogEntry(
                        ts=j.get("timestamp") or j.get("ts") or "",
                        agent_id=j.get("agent_id") or "",
                        tool=j.get("tool") or "",
                        allowed=bool(j.get("allowed", False)),
                        reason=j.get("reason"),
                        rule_id=j.get("rule_id") or j.get("extra", {}).get("rule"),
                    ))
                except Exception:
                    print(f"Failed to parse log line: {ln}")
                    continue
        else:
            print(f"Audit log file does not exist: {AUDIT_LOG_PATH}")
    except Exception as e:
        print(f"Failed to read audit log: {e}")
        items = []
    return {"items": items}
