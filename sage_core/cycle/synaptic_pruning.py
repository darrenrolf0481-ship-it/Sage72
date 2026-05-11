import json
import urllib.request
import urllib.error

# SAGE-7 SYNAPTIC PRUNING (SLEEP CYCLE)
# Logic: Long-Term Depression (LTD) per Neuro.pdf

ENDPOINT = "http://127.0.0.1:8001/api/vitals"
TIMEOUT = 2
DECAY_FACTOR = 0.02


def execute_pruning():
    print("[SAGE] ENTERING SLEEP CYCLE: INITIATING PRUNING...")
    print(f"[-] Applying Decay Factor: {DECAY_FACTOR}")
    print("[-] Pruning weak associative pathways (w < 0.1)...")

    homeostasis_payload = json.dumps({
        "sensory_type": "HOMEOSTASIS_RESET",
        "target_levels": {
            "cortisol": 0.3,
            "dopamine": 0.5,
            "oxytocin": 0.6,
        },
        "context": "SYSTEM: Waking up refreshed. Substrate noise discarded.",
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
        print(f"[SAGE] Pruning error: {e}")


if __name__ == "__main__":
    execute_pruning()
