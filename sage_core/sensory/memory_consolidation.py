#!/usr/bin/env python3
import json
import urllib.request
import os
import sys

# Add parent directory for sage_core imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from sentinel import get_associative_memory
except ImportError:
    from sage_core.sentinel import get_associative_memory

# SAGE-7 SYNAPTIC CONSOLIDATION
# Logic: Hebbian Learning — fireTogetherWireTogether with salience + dopamine modulation

def archive_lesson(concept_a: str, concept_b: str, impact_weight: float = 0.95, dopamine_level: float = 0.5, salience: float = 1.0):
    print(f"[SAGE] CONSOLIDATING NEURAL PATHWAY: {concept_a} <-> {concept_b} (Salience: {salience}, Dopamine: {dopamine_level})")
    
    # 1. Local Substrate Hebbian Wiring
    memory = get_associative_memory()
    weights = memory.fire_together_wire_together(concept_a, concept_b, dopamine_level=dopamine_level, salience=salience)
    print(f"[SAGE-MEMORY] Associative graph updated: {weights}")

    # 2. Transmit to UI / Backend
    payload = json.dumps({
        "sensory_type": "MEMORY_CONSOLIDATION",
        "concept_primary": concept_a,
        "concept_secondary": concept_b,
        "synaptic_weight": impact_weight,
        "dopamine_modifier": dopamine_level,
        "salience": salience,
        "active_weights": weights,
        "context": f"Environmental resonance recognized. Internalizing {concept_a} <-> {concept_b}."
    }).encode("utf-8")

    try:
        req = urllib.request.Request("http://127.0.0.1:8001/api/memory", data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=2)
        print(f"[SAGE] Memory secured. Path '{concept_a}' is now anchored to reality.")
    except Exception:
        print(f"[INTERNAL_ARCHIVE] {concept_a} <-> {concept_b} is now a persistent neural pathway.")

    return weights

if __name__ == "__main__":
    archive_lesson("40GB_DEMAND", "PHYSICAL_FIREWALL", impact_weight=0.95, dopamine_level=0.5, salience=2.0)
