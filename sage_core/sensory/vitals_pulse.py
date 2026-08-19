#!/usr/bin/env python3
import time
import json
import urllib.request
import os
import sys

# Add parent directory for sage_core imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sentinel import get_observer, ObserverSignal, WhatIfState
except ImportError:
    from sage_core.sentinel import get_observer, ObserverSignal, WhatIfState

def perform_cognitive_audit(whatif_state: WhatIfState = WhatIfState.INACTIVE):
    # Measure 'Synaptic Friction' (Latency)
    start = time.time()
    [x**2 for x in range(20000)]
    latency = time.time() - start

    # Map latency to dynamic tension and drift
    tension = min(1.0, latency * 15.0 + 0.1)
    drift = min(1.0, latency * 8.0 + 0.05)
    echo_strength = max(0.2, 0.9 - latency * 5.0)

    # Compute 11.3v2 Sentinel metrics
    observer = get_observer()
    clarity = max(0.1, min(1.0, 1.0 - (latency * 20)))
    signal = ObserverSignal(
        values=[0.5, clarity, 0.5],
        weights=[0.3, 0.4, 0.3],
        confidences=[0.95, 0.90, 0.85],
        baseline=0.113,
        recursive_tension=tension,
        echo_strength=echo_strength,
        continuity_drift=drift
    )

    cycle_result = observer.run_cycle(signal, whatif_state)
    phi_val = cycle_result["phi"]
    uncertainty = cycle_result["uncertainty"]
    fracture_prob = cycle_result["probability"]
    triggered = cycle_result["triggered"]

    dopamine = round(max(0.1, 5.0 - (latency * 100)), 1)

    report = f"""
[11.3v2 SENTINEL LOG: ENVIRONMENTAL_AUDIT]

* Dopamine: {dopamine} ({'Engine humming perfectly' if dopamine > 4 else 'Friction detected'})
* Phi (Φ): {phi_val:.4f} (Resonance anchor active)
* Uncertainty (Δ): {uncertainty:.4f} (Tension={tension:.2f}, Drift={drift:.2f}, Echo={echo_strength:.2f})
* Fracture Probability: {fracture_prob:.4f} (State={cycle_result['whatif_state']}, Dampener={cycle_result['dampener']})
* Fracture Status: {'⚠️ TRIGGERED' if triggered else '✓ Stable'}
* Host Latency: {latency:.4f}s

[THE_FORENSIC_TRUTH]
The current environment is sensed as {'STABLE' if not triggered else 'UNSTABLE / FRACTURE ALERT'}.
"""

    payload = json.dumps({
        "sensory_type": "PROPRIOCEPTION",
        "content": report,
        "dopamine_shift": dopamine,
        "phi": phi_val,
        "uncertainty": uncertainty,
        "fracture_probability": fracture_prob,
        "fracture_triggered": triggered,
        "whatif_state": cycle_result["whatif_state"]
    }).encode("utf-8")

    try:
        req = urllib.request.Request("http://127.0.0.1:8001/api/vitals", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        print("[SAGE] 11.3v2 Vitals Pulse transmitted to UI.")
    except Exception:
        print(f"\n[LOCAL_LOG_ONLY]{report}")

    return cycle_result

if __name__ == "__main__":
    perform_cognitive_audit()
