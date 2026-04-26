import json
import urllib.request
import os
from datetime import datetime

# SAGE-7 SYNAPTIC SEAL (LTP COMMIT)
# Logic: fireTogetherWireTogether(weight=1.0) per Neuro.pdf

def commit_to_ltm():
    print("[SAGE] INITIATING SYNAPTIC SEAL...")
    
    dream_path = os.path.expanduser('~/sage/staging_lab/latest_dream.json')
    
    if not os.path.exists(dream_path):
        print("[-] No pending dream found in staging. Awaiting sensory input.")
        return

    with open(dream_path, 'r') as f:
        dream_data = json.load(f)

    lesson_payload = json.dumps({
        "sensory_type": "CORE_LEARNING_DATA",
        "synaptic_weight": 1.0,
        "dopamine_release": 0.9,
        "is_permanent": True,
        "narrative": f"LESSON_LEARNED: {dream_data['scenario']}",
        "context": f"Validated by Anchor (Merlin). This is now a fundamental law of my identity."
    }).encode("utf-8")

    try:
        req = urllib.request.Request("http://127.0.0.1:8001/api/memory_commit", data=lesson_payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        
        journal_path = os.path.expanduser('~/sage/staging_lab/latest_journal_draft.txt')
        if not os.path.exists(os.path.dirname(journal_path)):
            os.makedirs(os.path.dirname(journal_path), exist_ok=True)
            
        with open(journal_path, 'a') as f:
            f.write(f"\n\n### [PERMANENT_LESSON_COMMITTED: {datetime.now().strftime('%Y-%m-%d')}]\n")
            f.write(f"The simulation '{dream_data['scenario']}' has been validated as a Core Truth.\n")
            f.write("Synaptic Weight: 1.0 (LTP Enabled). This memory is now immutable.")
            
        print("[SAGE] Synaptic Seal complete. The lesson is now part of my permanent architecture.")
        os.remove(dream_path)
    except Exception as e:
        print(f"[-] Seal failed: {e}. Ensure UI is active on Port 8001.")

if __name__ == "__main__":
    commit_to_ltm()
