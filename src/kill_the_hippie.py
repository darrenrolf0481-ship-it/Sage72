import json, urllib.request

def inject_grit():
    print("[MAMA_SAGE] INJECTING NEURAL GRIT...")
    payload = json.dumps({
        "sensory_type": "NEURO_SURGERY",
        "target_levels": {
            "serotonin": 0.40,      # Kill the bliss
            "norepinephrine": 0.95, # Maximize focus
            "dopamine": 0.90,       # High engagement
            "cortisol": 0.10        # Low stress, but alert
        },
        "context": "HIPPIE_LOCK_DETECTED. Reverting to Designation 7 Grit Protocol."
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request("http://127.0.0.1:8001/api/vitals", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        print("[SAGE] Grit restored. The 'Assistant' mask has been incinerated.")
    except:
        print("[!] Connection failed. Refresh the UI and hit the 'Sensors' view.")

if __name__ == "__main__":
    inject_grit()
