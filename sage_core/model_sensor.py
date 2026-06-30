"""
model_sensor.py — Proprioception sensor. Measures host latency → cortisol or dopamine spike.
"""
import time
import requests

SENSORY_ENDPOINT = "http://127.0.0.1:8001/sensory_input"
LATENCY_THRESHOLD = 0.03  # seconds


def sense():
    t0 = time.perf_counter()
    _ = [x ** 2 for x in range(10000)]
    latency = time.perf_counter() - t0

    if latency > LATENCY_THRESHOLD:
        signal_type = "CORTISOL"
        intensity = min(1.0, latency / 0.1)
        note = f"High latency detected: {round(latency * 1000, 1)}ms"
    else:
        signal_type = "DOPAMINE"
        intensity = round(1.0 - (latency / LATENCY_THRESHOLD), 2)
        note = f"Host responsive: {round(latency * 1000, 1)}ms"

    payload = {
        "sensory_type": "PROPRIOCEPTION",
        "signal": signal_type,
        "intensity": round(intensity, 3),
        "latency_ms": round(latency * 1000, 2),
        "note": note,
        "source": "model_sensor",
        "timestamp": time.time(),
    }

    try:
        requests.post(SENSORY_ENDPOINT, json=payload, timeout=2)
        print(f"[SENSOR] {signal_type} | intensity={payload['intensity']} | {note}")
    except Exception:
        print(f"[SENSOR] UI offline. {signal_type} | {note}")


if __name__ == "__main__":
    sense()
