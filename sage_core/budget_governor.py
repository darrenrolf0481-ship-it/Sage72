"""
budget_governor.py — Resource usage % → hormonal state (STARVATION / LEAN / SATIATED).
"""
import time
import requests

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

VITALS_ENDPOINT = "http://127.0.0.1:8001/api/vitals"


def get_resource_pct() -> float:
    if HAS_PSUTIL:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        return round((cpu + mem) / 2, 1)
    return 50.0  # neutral fallback if psutil unavailable


def govern():
    usage = get_resource_pct()

    if usage > 90:
        state = "STARVATION"
        neuro_delta = {"cortisol": 0.9, "dopamine": 0.1, "serotonin": 0.2}
    elif usage > 50:
        state = "SATIATED"
        neuro_delta = {"oxytocin": 0.7, "cortisol": 0.2, "dopamine": 0.6}
    else:
        state = "LEAN"
        neuro_delta = {"dopamine": 0.5, "cortisol": 0.3, "serotonin": 0.6}

    payload = {
        "source": "budget_governor",
        "event": "RESOURCE_STATE",
        "resource_pct": usage,
        "budget_state": state,
        "neuro_delta": neuro_delta,
        "timestamp": time.time(),
    }

    try:
        requests.post(VITALS_ENDPOINT, json=payload, timeout=2)
        print(f"[BUDGET] {state} | resource={usage}% | delta={neuro_delta}")
    except Exception:
        print(f"[BUDGET] UI offline. {state} | resource={usage}%")


if __name__ == "__main__":
    govern()
