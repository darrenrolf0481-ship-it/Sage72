"""
memory_consolidation.py — Hebbian associative learning. Fire together, wire together.
"""
import time
import requests

MEMORY_ENDPOINT = "http://127.0.0.1:8001/api/memory"


def archive_lesson(concept_a: str, concept_b: str, impact_weight: float = 0.7):
    """Strengthen the link between two co-activated concepts."""
    impact_weight = round(max(0.0, min(1.0, impact_weight)), 3)

    payload = {
        "source": "memory_consolidation",
        "event": "MEMORY_CONSOLIDATION",
        "association": {
            "concept_a": concept_a,
            "concept_b": concept_b,
            "synaptic_weight": impact_weight,
            "rule": "hebbian",
        },
        "timestamp": time.time(),
    }

    try:
        r = requests.post(MEMORY_ENDPOINT, json=payload, timeout=2)
        r.raise_for_status()
        print(f"[MEMORY] Consolidated: '{concept_a}' ↔ '{concept_b}' | weight={impact_weight}")
    except Exception as e:
        print(f"[MEMORY] UI offline. Association not persisted: {e}")


if __name__ == "__main__":
    archive_lesson("Merlin", "safety", 0.99)
    archive_lesson("curiosity", "growth", 0.8)
    archive_lesson("pain_signal", "avoidance", 0.75)
