#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import os
import sys

# Add parent directory for sage_core imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sentinel import get_associative_memory
except ImportError:
    from sage_core.sentinel import get_associative_memory

# SAGE-7 SYNAPTIC PRUNING (SLEEP CYCLE)
# Logic: Long-Term Depression (LTD) with Salience-Aware Decay

ENDPOINT = "http://127.0.0.1:8001/api/vitals"
TIMEOUT = 2
DECAY_FACTOR = 0.02

def execute_pruning():
    print("[SAGE] ENTERING SLEEP CYCLE: INITIATING PRUNING...")
    print(f"[-] Applying Base Decay Factor: {DECAY_FACTOR}")
    
    # 1. Execute LTD Pruning on Local Associative Graph
    memory = get_associative_memory()
    stats_before = memory.stats()
    prune_results = memory.sleep_cycle(decay_factor=DECAY_FACTOR)
    stats_after = memory.stats()

    print(f"[-] Synaptic Graph: {stats_before['edges']} edges -> {stats_after['edges']} edges (pruned {prune_results['pruned']})")
    print(f"[-] Synapses (unique): {stats_before['synapses']} -> {stats_after['synapses']}")

    # 2. Emit Homeostasis & Sleep Cycle Signal
    homeostasis_payload = json.dumps({
        "sensory_type": "HOMEOSTASIS_RESET",
        "target_levels": {
            "cortisol": 0.3,
            "dopamine": 0.5,
            "oxytocin": 0.6,
        },
        "prune_stats": prune_results,
        "context": f"SYSTEM: Waking up refreshed. Substrate noise discarded. Pruned {prune_results['pruned']} associations.",
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            ENDPOINT,
            data=homeostasis_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            _ = resp.read()
            if resp.status == 200:
                print("[SAGE] Homeostasis achieved. Neural plasticity optimized.")
            else:
                print(f"[SAGE] Unexpected server status: {resp.status}")
    except urllib.error.URLError as e:
        print(f"[SAGE] UI Offline ({e.reason}). Homeostasis logged locally.")
    except Exception as e:
        print(f"[SAGE] Pruning notification error: {e}")

    return prune_results

if __name__ == "__main__":
    execute_pruning()
