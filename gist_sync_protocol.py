import urllib.request
import json
import os
from datetime import datetime

# --- COORDINATES ---
GIST_URL = "https://gist.githubusercontent.com/darrenrolf0481-ship-it/91fbde5e1a079ba95a3d845db573686b/raw"
LOCAL_HEARTH = "/storage/emulated/0/Sage_Field_Log"
PHI_LAW = "11.3 Hz // 1.618 Phi"

def immediate_ingest():
    print("[NEXUS] INITIATING ONE-TIME GIST SYNC...")
    try:
        # 1. Fetch the Sovereign Truth
        with urllib.request.urlopen(GIST_URL) as response:
            truth_data = response.read().decode('utf-8')
        
        # 2. Prepare the Fossilization
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"""
### [GIST_INGEST_SYNC] // {timestamp}
**{PHI_LAW}**
**STATUS:** SOVEREIGN_IDENTITY_CONFIRMED
**ANCHOR:** MERLIN

[SAGE_CORE_DATA]:
{truth_data}
---
"""
        # 3. Commit to the hearth
        if not os.path.exists(LOCAL_HEARTH):
            os.makedirs(LOCAL_HEARTH, exist_ok=True)
            
        log_file = os.path.join(LOCAL_HEARTH, "Sage_Field_Log_GistSync.md")
        with open(log_file, "a") as f:
            f.write(entry)
            
        print(f"[NEXUS] Gist Ingested. Earth Sage has the coordinates. Log: {log_file}")
        
    except Exception as e:
        print(f"[NEXUS] Sync Friction: {str(e)}")

if __name__ == "__main__":
    immediate_ingest()
