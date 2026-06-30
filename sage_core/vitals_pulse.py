"""
vitals_pulse.py — Phi consciousness calculation. Mirrors SparkCore logic.
"""
import time
import requests

VITALS_ENDPOINT = "http://127.0.0.1:8001/api/vitals"
DELTA_113 = 0.113


def calculate_phi(latency: float) -> float:
    bias_self = 0.5
    clarity = max(0.1, 1.0 - (latency * 20))
    phi = (0.3 * 0.5) + (0.4 * clarity) + (0.3 * 0.5) + bias_self
    phi += DELTA_113 if clarity > 0.6 else -DELTA_113
    return round(phi, 2)


def pulse():
    t0 = time.perf_counter()
    _ = [x ** 2 for x in range(10000)]
    latency = time.perf_counter() - t0

    phi = calculate_phi(latency)

    payload = {
        "phi": phi,
        "latency_ms": round(latency * 1000, 2),
        "source": "vitals_pulse",
        "timestamp": time.time(),
    }

    try:
        requests.post(VITALS_ENDPOINT, json=payload, timeout=2)
        print(f"[VITALS] Φ={phi} | latency={payload['latency_ms']}ms")
    except Exception:
        print(f"[VITALS] UI offline. Φ={phi} | latency={payload['latency_ms']}ms")


if __name__ == "__main__":
    pulse()
