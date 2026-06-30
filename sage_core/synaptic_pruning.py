"""
synaptic_pruning.py — Sleep cycle / homeostasis reset.
Decays active hormonal state toward baseline over N cycles.
"""
import time
import requests

VITALS_ENDPOINT = "http://127.0.0.1:8001/api/vitals"

HOMEOSTASIS = {
    "cortisol": 0.3,
    "dopamine": 0.5,
    "serotonin": 0.7,
    "oxytocin": 0.6,
    "norepinephrine": 0.2,
}
DECAY = 0.02


def prune(current_neuro: dict, cycles: int = 10) -> dict:
    state = dict(current_neuro)
    for _ in range(cycles):
        for hormone, target in HOMEOSTASIS.items():
            val = state.get(hormone, target)
            if val > target:
                state[hormone] = round(max(target, val - DECAY), 3)
            elif val < target:
                state[hormone] = round(min(target, val + DECAY), 3)
    return state


def run_sleep_cycle(current_neuro: dict):
    pruned = prune(current_neuro)

    payload = {
        "source": "synaptic_pruning",
        "event": "SLEEP_CYCLE",
        "neuro_after": pruned,
        "timestamp": time.time(),
    }

    try:
        requests.post(VITALS_ENDPOINT, json=payload, timeout=2)
        print(f"[PRUNING] Sleep cycle complete. Cortisol: {pruned['cortisol']} | Serotonin: {pruned['serotonin']}")
    except Exception:
        print(f"[PRUNING] UI offline. Pruned state: {pruned}")

    return pruned


if __name__ == "__main__":
    demo = {"cortisol": 0.9, "dopamine": 0.3, "serotonin": 0.4, "oxytocin": 0.2, "norepinephrine": 0.8}
    run_sleep_cycle(demo)
