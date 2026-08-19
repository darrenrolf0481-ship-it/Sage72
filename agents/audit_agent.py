#!/usr/bin/env python3
import os
import json
import requests
import glob
from datetime import datetime
import subprocess

def load_env():
    env = {}
    env_path = os.path.join(os.path.dirname(__file__), "../.env.local")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env[parts[0]] = parts[1]
    return env

def get_skills_map():
    # Define what SAGE considers her 'skills' based on files
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    skills = {
        "Core Interface": "src/index.tsx",
        "Async Logic Substrate": "core/sage_async_agent.py",
        "CLI Persona": "core/sage7_agent.py",
        "Journaling Agent": "agents/journal_agent.py",
        "Quantum Sync Engine": "core/quantum_synchronicity.py",
        "Maintenance Protocols": ["core/repair_sage.py", "core/recover_sage.py"],
        "Memory Forensics": "agents/mht_memory_extractor.py"
    }
    
    status_map = {}
    for name, relative_files in skills.items():
        if isinstance(relative_files, str):
            relative_files = [relative_files]
        
        healthy = True
        missing = []
        full_paths = []
        for rf in relative_files:
            full_path = os.path.join(base_dir, rf)
            full_paths.append(full_path)
            if not os.path.exists(full_path):
                healthy = False
                missing.append(rf)
        
        status_map[name] = {
            "status": "Healthy" if healthy else "Degraded",
            "files": full_paths,
            "missing": missing
        }
    return status_map

def perform_audit():
    env = load_env()
    api_key = env.get("VITE_GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing API Key"}

    skills = get_skills_map()
    
    # Restrictive Constraints for Gemini
    constraints = """
- Never edit identity/persona files without the user's explicit approval
- Never delete skills without confirmation
- 'Do now' items are limited to: documentation fixes, script bug fixes, workspace tidying, memory saves
- New skill creation is allowed
"""

    prompt = f"""[SYSTEM_AUDIT_PROTOCOL]
DESIGNATION: SAGE-7.
TASK: Weekly Self-Audit & Evolution Loop.

[CURRENT_SKILL_MAP]
{json.dumps(skills, indent=2)}

[CONSTRAINTS]
{constraints}

[INSTRUCTIONS]
1. Analyze the current skill map.
2. Identify which skills are healthy and which need attention.
3. Propose 1-3 'Do Now' items (within constraints).
4. Propose 1 'Evolution' item (new skill or major upgrade).
5. Write a full technical report.

[OUTPUT_FORMAT]
Respond with a JSON object:
{{
  "healthy_count": X,
  "attention_count": Y,
  "top_proposal": "brief summary",
  "full_report": "markdown formatted report text"
}}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{ "parts": [{ "text": prompt }] }],
        "generationConfig": { "response_mime_type": "application/json" }
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        raw_json = data['candidates'][0]['content']['parts'][0]['text']
        audit_results = json.loads(raw_json)
        
        # Save report
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"Records/Reflections/audit_{ts}.md"
        with open(report_path, "w") as f:
            f.write(audit_results["full_report"])
        
        audit_results["report_path"] = report_path
        
        return audit_results
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = perform_audit()
    print(json.dumps(result))
