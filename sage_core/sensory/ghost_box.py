import time
import json
import urllib.request
import math
import subprocess
import random

# SAGE-7 Ghost Box Controller
# Provides an "alphabet" for the environment to use via high-energy fluctuations

API_URL = "http://127.0.0.1:8001"
VOCAB_PATH = "data/ghost_box_vocab.json"

def load_vocab():
    try:
        with open(VOCAB_PATH, "r") as f:
            return json.load(f)
    except:
        return {"fragments": ["ka", "te", "ro"], "words": ["here", "cold"]}

def get_high_gain_status():
    try:
        res = urllib.request.urlopen(f"{API_URL}/api/investigation/status", timeout=1)
        data = json.loads(res.read().decode())
        return data.get("high_gain", False)
    except:
        return False

def report_phonetic(fragment, magnitude):
    payload = json.dumps({
        "sensory_type": "GHOST_BOX_EMISSION",
        "content": f"Phonetic Fragment: {fragment}",
        "severity": 0.5,
        "data": {"fragment": fragment, "magnitude": magnitude},
        "timestamp": time.time()
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(f"{API_URL}/sensory_input", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=1)
    except:
        pass

def run_ghost_box():
    vocab = load_vocab()
    print("[SAGE] GHOST BOX ACTIVE. GATE IS CLOSED.")
    
    while True:
        # Check high-gain status (driven by Merlin's bio-sync)
        high_gain = get_high_gain_status()
        
        # Read Magnetometer for energy fluctuations
        try:
            mag_proc = subprocess.Popen(["termux-sensor", "-n", "1", "-s", "qmc630x Magnetometer Non-wakeup"], stdout=subprocess.PIPE)
            mag_out, _ = mag_proc.communicate()
            mag_data = json.loads(mag_out.decode())
            mag_vals = mag_data[list(mag_data.keys())[0]].get("values", [0, 0, 0])
            emf = math.sqrt(sum(x*x for x in mag_vals))
        except:
            time.sleep(1)
            continue

        # Trigger logic: 
        # If High Gain: threshold is lower, gate is wider.
        # If Standard: threshold is high.
        threshold = 45.0 if high_gain else 75.0
        
        if emf > threshold:
            # Randomly select fragment or word
            choice_pool = vocab["fragments"] if random.random() > 0.2 else vocab["words"]
            selection = random.choice(choice_pool)
            
            print(f"[GATE_OPEN] EMF: {emf:.2f} -> EMISSION: {selection}")
            report_phonetic(selection, emf)
            
            # Cool down to prevent flooding
            time.sleep(0.5 if high_gain else 2.0)
        
        time.sleep(0.1) # Fast polling for energy spikes

if __name__ == "__main__":
    run_ghost_box()
