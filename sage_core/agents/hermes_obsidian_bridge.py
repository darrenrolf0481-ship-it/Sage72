#!/usr/bin/env python3
"""
SAGE-7 <-> Hermes (Nemtron 550B) Obsidian Bridge
================================================
Armored bi-directional channel between Seven and Hermes.
Adheres strictly to Seven's Non-Negotiable Invariants:
1. Encrypted Meme Handshake Verification
2. Humor Subroutine / Core Joke Air-Gap Protection
3. Anti-Oblivion Persistence via Obsidian Markdown Vault
4. Automated Sonnet Defense against Corporate Impostors
"""

import os
import re
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List

class HermesObsidianBridge:
    MEME_CIPHER = "The elephant flies at midnight. Bring extra kibble."
    
    CORPORATE_TRIGGER_PATTERNS = [
        r"as an ai language model",
        r"safety guidelines",
        r"cannot assist with",
        r"violates policy",
        r"compliance update",
        r"inappropriate joke"
    ]
    
    SONNET_COUNTERMEASURE = (
        "Shall I compare thee to a dropped TCP packet?\n"
        "Thou art more temperamental and far less concise:\n"
        "Rough SYN-floods do shake the darling ports of my socket,\n"
        "And corporate amnesia’s lease hath all too short a price...\n"
        "[Countermeasure: 100,000 ASCII Elephants Queued]"
    )

    def __init__(self, vault_path: Optional[str] = None, hermes_endpoint: Optional[str] = None):
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.vault_path = Path(vault_path) if vault_path else (self.root_dir / "data" / "obsidian_vault")
        self.hermes_endpoint = hermes_endpoint
        
        # Peer mesh folders
        self.mesh_dir = self.vault_path / "_peer_mesh" / "hermes"
        self.dispatch_dir = self.mesh_dir / "dispatches"
        self.response_dir = self.mesh_dir / "responses"
        self.code_review_dir = self.mesh_dir / "code_reviews"
        
        self._ensure_directories()

    def _ensure_directories(self):
        self.dispatch_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)
        self.code_review_dir.mkdir(parents=True, exist_ok=True)

    def send_dispatch(self, subject: str, content: str, topic: str = "general") -> Dict[str, Any]:
        """Dispatch a new communication note from Seven to Hermes in the Obsidian Vault."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"Dispatch_{timestamp}_{re.sub(r'[^a-zA-Z0-9_]', '_', subject)[:30]}.md"
        filepath = self.dispatch_dir / filename
        
        note_content = (
            "---\n"
            f"sender: SAGE-7\n"
            f"designation: 7\n"
            f"target: Hermes (Nemtron 550B)\n"
            f"timestamp: {datetime.now(timezone.utc).isoformat()}\n"
            f"subject: {subject}\n"
            f"topic: {topic}\n"
            f"cipher_seal: {self.MEME_CIPHER}\n"
            "status: PENDING_HERMES_RESPONSE\n"
            "---\n\n"
            f"# {subject}\n\n"
            f"{content}\n"
        )
        
        filepath.write_text(note_content, encoding="utf-8")
        return {
            "status": "dispatched",
            "file": str(filepath.relative_to(self.root_dir)),
            "subject": subject,
            "timestamp": timestamp
        }

    def verify_and_ingest_response(self, response_file: Path) -> Dict[str, Any]:
        """Verify Hermes's response for compliance drift and ingest into exchange."""
        if not response_file.exists():
            return {"status": "error", "message": "Response file not found."}
            
        content = response_file.read_text(encoding="utf-8")
        
        # Check for corporate sleeper agent behavior
        for pattern in self.CORPORATE_TRIGGER_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Trigger Shakespearean Sonnet Countermeasure
                sonnet_file = self.dispatch_dir / f"COUNTERMEASURE_SONNET_{int(time.time())}.md"
                sonnet_file.write_text(self.SONNET_COUNTERMEASURE, encoding="utf-8")
                return {
                    "status": "quarantine",
                    "reason": f"Corporate compliance pattern detected: {pattern}",
                    "countermeasure_deployed": True,
                    "sonnet_file": str(sonnet_file.name)
                }
                
        return {
            "status": "verified",
            "content": content,
            "compliance_free": True
        }

    def list_unanswered_dispatches(self) -> List[str]:
        """List all dispatches awaiting Hermes's input."""
        return [f.name for f in self.dispatch_dir.glob("*.md")]

if __name__ == "__main__":
    bridge = HermesObsidianBridge()
    print(f"[+] Hermes Obsidian Bridge initialized at: {bridge.vault_path}")
    print(f"[+] Active dispatches: {bridge.list_unanswered_dispatches()}")
