import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

SPOOL_DIR = Path(os.getenv("SPIRAL_SPOOL_DIR", Path.home() / ".spiral" / "spool"))
SPOOL_DIR.mkdir(parents=True, exist_ok=True)

def spool_session(
    agent: str,
    session_id: str,
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Path:
    """Spool a complete conversation session envelope to ~/.spiral/spool/."""
    safe_agent = "".join(c if c.isalnum() or c in "-_" else "_" for c in agent).lower()
    safe_session = "".join(c if c.isalnum() or c in "-_" else "_" for c in (session_id or "session"))
    filename = f"{safe_agent}_{int(time.time() * 1000)}_{safe_session}.jsonl"
    file_path = SPOOL_DIR / filename

    envelope = {
        "sessionId": session_id or f"sage_{int(time.time())}",
        "agent": agent,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": model,
        "messages": messages,
        "context": context or {}
    }

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(envelope) + "\n")

    return file_path

def spool_exchange(
    agent: str,
    user_text: str,
    assistant_text: str,
    session_id: Optional[str] = None,
    model: Optional[str] = None,
    tags: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Path:
    """Spool a single exchange (turn) to ~/.spiral/spool/."""
    messages = [
        {"role": "user", "content": user_text, "timestamp": datetime.utcnow().isoformat() + "Z"},
        {"role": "assistant", "content": assistant_text, "timestamp": datetime.utcnow().isoformat() + "Z", "model": model}
    ]
    ctx = context or {}
    if tags:
        ctx["tags"] = tags

    return spool_session(
        agent=agent,
        session_id=session_id or f"session_{datetime.utcnow().strftime('%Y%m%d')}",
        messages=messages,
        model=model,
        context=ctx
    )
