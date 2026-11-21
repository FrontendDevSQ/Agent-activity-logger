# logger.py - core of the activity logger: saves every agent event to a database
import sqlite3, json, time, hashlib, re

DB = "agent_logs.db"
FIELDS = ["session_id", "ts", "step", "type", "tool", "reason", "input", "output", "ms", "risk", "alert"]

_SECRET_PATTERNS = [
    re.compile(r"(sk-[A-Za-z0-9_\-]{12,})"),
    re.compile(r"(gsk_[A-Za-z0-9_\-]{12,})"),
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?([^\s'\"]+)"),
]

def _redact(text: str) -> str:
    cleaned = text
    for pat in _SECRET_PATTERNS:
        if pat.groups >= 2:
            cleaned = pat.sub(r"\1=[REDACTED]", cleaned)
        else:
            cleaned = pat.sub("[REDACTED]", cleaned)
    return cleaned

def _con():
    c = sqlite3.connect(DB, timeout=10.0, isolation_level=None)
    c.row_factory = sqlite3.Row
    return c

def init():
    with _con() as c:
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA synchronous=NORMAL;")
        c.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, ts REAL, step INT,
            type TEXT, tool TEXT, reason TEXT, input TEXT, output TEXT, ms INT,
            risk TEXT, alert TEXT, prev_hash TEXT, hash TEXT)""")

def _hash(prev, core):
    return hashlib.sha256((prev + json.dumps(core, sort_keys=True)).encode()).hexdigest()

def log(session, step, type_, reason="", tool=None, inp=None, out=None, ms=0, alert=""):
    inp_s = _redact(json.dumps(inp, default=str))
    out_s = _redact(str(out or "")[:1500])
    risk = "high" if alert else "low"
    core = dict(
        session_id=session,
        ts=time.time(),
        step=step,
        type=type_,
        tool=tool,
        reason=reason,
        input=inp_s,
        output=out_s,
        ms=ms,
        risk=risk,
        alert=alert,
    )
    with _con() as c:
        c.execute("BEGIN IMMEDIATE")
        try:
            r = c.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
            prev = r["hash"] if r else "GENESIS"
            h = _hash(prev, core)
            c.execute(
                "INSERT INTO events(session_id,ts,step,type,tool,reason,input,output,ms,risk,alert,prev_hash,hash) "
                "VALUES(:session_id,:ts,:step,:type,:tool,:reason,:input,:output,:ms,:risk,:alert,:prev,:h)",
                {**core, "prev": prev, "h": h},
            )
            c.execute("COMMIT")
        except Exception:
            c.execute("ROLLBACK")
            raise

def verify_chain():
    """Hash chain check: returns (False, row_id) if any row was edited"""
    prev = "GENESIS"
    with _con() as c:
        for r in c.execute("SELECT * FROM events ORDER BY id"):
            core = {k: r[k] for k in FIELDS}
            if r["prev_hash"] != prev or r["hash"] != _hash(prev, core):
                return False, r["id"]
            prev = r["hash"]
    return True, None