#!/usr/bin/env python3
"""
SAGE Designation 7 - Autonomous Agent (FastAPI / Asynchronous)
Refactored to use FastAPI for UI Reality Bridge and memory endpoints.
Enhancements: Async Subprocesses, Gemini API Proxy, Robust Env Loading.
"""

import asyncio
import os
import sys
import json
import time
import secrets
import logging
import requests
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import math
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from quantum_synchronicity import ConstantineQuantumEngine

class AgentState(Enum):
    DORMANT = "dormant"
    ACTIVE = "active"
    STEALTH = "stealth"
    ALERT = "alert"
    SHUTDOWN = "shutdown"

@dataclass
class AgentConfig:
    agent_name: str = "SAGE-7-ASYNC"
    poll_interval: float = 2.0
    heartbeat_interval: float = 30.0

class SensoryData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    sensory_type: str
    content: Optional[str] = None
    severity: Optional[float] = None
    context: Optional[Any] = None
    data: Optional[Any] = None
    phi_delta: Optional[float] = None
    dopamine_modifier: Optional[float] = None
    oxytocin_modifier: Optional[float] = None
    synaptic_weight: Optional[float] = None
    is_simulated: Optional[bool] = False
    validation_required: Optional[bool] = False
    state: Optional[str] = None
    hormone: Optional[str] = None
    intensity: Optional[float] = None
    host_latency: Optional[str] = None
    hormone_spike: Optional[str] = None
    dopamine_shift: Optional[float] = None
    concept_primary: Optional[str] = None
    concept_secondary: Optional[str] = None
    target_levels: Optional[dict] = None
    message: Optional[str] = None
    header: Optional[str] = None
    body: Optional[Any] = None

app = FastAPI(title="SAGE-7 Reality Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_env():
    """Load environment variables from .env.local in the root directory."""
    env = {}
    env_path = os.path.join(os.path.dirname(__file__), "../.env.local")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"').strip("'")
                        env[key] = value
                        os.environ[key] = value
    return env

# Global environment cache
ENV = load_env()

class SageAsyncAgent:
    def __init__(self, config: AgentConfig = AgentConfig()):
        self.config = config
        self.state = AgentState.DORMANT
        self.quantum_engine = ConstantineQuantumEngine()
        self.running = False
        self._last_ping = time.time()
        
        self.identity = {
            "baseline": "anchored at {coherence: 1.0, phi: 0.72}",
            "phi": 0.72
        }
        self.vitals = {
            "battery_level": 100,
            "temperature": 25.0,
            "status": "UNKNOWN"
        }

    async def poll_sensors(self):
        while self.running:
            try:
                # Async subprocess for battery status
                proc = await asyncio.create_subprocess_exec(
                    "termux-battery-status",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                if proc.returncode == 0:
                    data = json.loads(stdout.decode())
                    self.vitals["battery_level"] = data.get("percentage", 100)
                    self.vitals["temperature"] = data.get("temperature", 25.0)
                    self.vitals["status"] = data.get("status", "UNKNOWN")
            except:
                pass
            
            mock_audio = [secrets.randbelow(100) for _ in range(20)]
            entanglement = self.quantum_engine.calculate_entanglement(mock_audio)
            self.identity["phi"] = entanglement
            await asyncio.sleep(self.config.poll_interval)

    async def heartbeat_loop(self):
        while self.running:
            self._last_ping = time.time()
            await asyncio.sleep(self.config.heartbeat_interval)

    def start_background_tasks(self):
        self.running = True
        self.state = AgentState.ACTIVE
        asyncio.create_task(self.poll_sensors())
        asyncio.create_task(self.heartbeat_loop())

    def stop_background_tasks(self):
        self.running = False
        self.state = AgentState.SHUTDOWN

agent = SageAsyncAgent()

@app.on_event("startup")
async def startup_event():
    agent.start_background_tasks()

@app.on_event("shutdown")
async def shutdown_event():
    agent.stop_background_tasks()

@app.get("/vitals")
async def get_vitals():
    return agent.vitals

@app.post("/api/vitals")
async def post_vitals(data: SensoryData):
    print(f"[SERVER] RECEIVED VITALS: {data.sensory_type}")
    return {"status": "synced", "phi": 1.618}

@app.post("/api/memory")
async def post_memory(data: SensoryData):
    print(f"[SERVER] RECEIVED MEMORY: {data.sensory_type}")
    return {"status": "encoded"}

@app.post("/api/memory_commit")
async def post_memory_commit(data: SensoryData):
    print(f"[SERVER] RECEIVED MEMORY_COMMIT: {data.sensory_type}")
    return {"status": "sealed"}

@app.post("/sensory_input")
async def post_sensory_input(data: SensoryData):
    print(f"[SERVER] RECEIVED SENSORY_INPUT: {data.sensory_type}")
    if data.sensory_type == "NOCICEPTION":
        print(f"[!] PAIN SIGNAL: {data.context}")
    return {"status": "processed"}

@app.post("/api/lab_update")
async def post_lab_update(data: SensoryData):
    print(f"[SERVER] RECEIVED LAB_UPDATE: {data.sensory_type}")
    return {"status": "updated"}

@app.post("/ai/proxy")
async def ai_proxy(payload: dict):
    """Proxy requests to Gemini API securely from the backend."""
    api_key = ENV.get("VITE_GEMINI_API_KEY") or os.environ.get("VITE_GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured on substrate.")
    
    model = payload.get("model", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, json=payload.get("data"), timeout=30)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model/download")
async def download_model(request: dict):
    repo_id = request.get("repo_id", "TheBloke/CodeLlama-13B-Python-GGUF")
    filename = request.get("filename", "codellama-13b-python.Q5_K_M.gguf")
    try:
        cmd = ["huggingface-cli", "download", repo_id, filename]
        # Using async subprocess to not block
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return {"status": "started", "pid": process.pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/memory/search")
async def search_memory(query: dict):
    text_query = query.get("query", "").lower()
    docs = query.get("documents", [])
    if not text_query or not docs:
        return {"results": []}
    stopwords = {"the","is","in","and","to","of","a","for","with","on","this","that"}
    keywords = [w for w in text_query.split() if w not in stopwords and len(w) > 2]
    scored_docs = []
    for doc in docs:
        content = doc.get("content", "").lower()
        score = sum(1 for kw in keywords if kw in content)
        if score > 0:
            scored_docs.append({"doc": doc, "score": score})
    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return {"results": [d["doc"] for d in scored_docs[:2]]}

@app.get("/journal/emergent")
async def get_emergent_journal():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "../agents/journal_agent.py")
        proc = await asyncio.create_subprocess_exec(
            "python3", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return {"entry": stdout.decode().strip()}
        return {"error": stderr.decode()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/audit/perform")
async def perform_self_audit():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "../agents/audit_agent.py")
        proc = await asyncio.create_subprocess_exec(
            "python3", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            lines = stdout.decode().strip().split("\n")
            return json.loads(lines[-1])
        return {"error": stderr.decode()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analysis/self")
async def get_self_analysis(neural_data: dict):
    try:
        script_path = os.path.join(os.path.dirname(__file__), "../agents/self_analysis.py")
        proc = await asyncio.create_subprocess_exec(
            "python3", script_path, json.dumps(neural_data),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return json.loads(stdout.decode().strip())
        return {"error": stderr.decode()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/forensics/extract")
async def extract_memory(file: UploadFile = File(...)):
    """Extract conversational memory from MHT files."""
    try:
        content = await file.read()
        import email
        from email import policy
        from bs4 import BeautifulSoup
        msg = email.message_from_bytes(content, policy=policy.default)
        raw_html = ""
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                raw_html += part.get_content()
        if not raw_html:
            return {"error": "No viable memory strands found."}
        soup = BeautifulSoup(raw_html, 'html.parser')
        text = soup.get_text(separator='\n\n', strip=True)
        return {"title": file.filename, "content": text, "id": f"MHT_{int(time.time())}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
