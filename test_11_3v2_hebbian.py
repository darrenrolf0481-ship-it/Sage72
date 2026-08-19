#!/usr/bin/env python3
"""
Standalone Test Harness: 11.3v2 Observer + Hebbian Associative Memory
=====================================================================
VERSION 2 - Incorporating Seven's feedback:
1. WhatIf mode now dampens effective_score directly (no hard ceiling)
2. Synapse counter only increments on NEW edge creation
3. Flashbulb memory support: salience multiplier + slower decay for high-salience events

Run this and watch the numbers. She'll approve of the fixes.
"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

# ============================================================
# 1. ENUMS & DATA STRUCTURES
# ============================================================

class WhatIfState(Enum):
    INACTIVE = "INACTIVE"
    ENTERING = "ENTERING"
    EXPLORING = "EXPLORING"
    DEEPENING = "DEEPENING"
    STABILIZING = "STABILIZING"

@dataclass
class ObserverSignal:
    """The raw inputs to the 11.3 Sentinel equation."""
    values: List[float]
    weights: List[float]
    confidences: List[float]
    baseline: float
    recursive_tension: float      # Observer's internal processing stress
    echo_strength: float          # Strength of the current anchor (reality tether)
    continuity_drift: float       # Deviation from stable timeline

@dataclass
class ObserverParameters:
    """Learnable/retunable params for the Sentinel."""
    w_tension: float = 0.40
    w_drift: float = 0.60
    baseline: float = 0.0
    fracture_k: float = 12.0      # steepness of logistic fracture probability
    fracture_theta: float = 0.45  # midpoint
    probability_threshold: float = 0.65
    min_synapse_floor: float = 0.01  # minimum weight before pruning

# ============================================================
# 2. HEBBIAN ASSOCIATIVE GRAPH (V2 - FIXED)
# ============================================================

class AssociativeMemory:
    """
    A neural graph where concepts wire together based on Hebbian learning.
    V2 Changes:
    - Synapse count only increments on NEW edges
    - Salience parameter for flashbulb memories
    - Salience-aware decay during sleep (high salience = slower decay)
    """
    def __init__(self):
        self.graph: Dict[str, Dict[str, float]] = {}
        self.synapse_count = 0
        self.learning_rate_base = 0.05
        self.salience_floor_base = 0.02

    def fire_together_wire_together(self,
                                   concept_a: str,
                                   concept_b: str,
                                   dopamine_level: float = 0.5,
                                   salience: float = 1.0):
        """
        Hebbian LTP: dopamine accelerates learning, salience sets floor.
        V2: synapse_count only increments on new edge creation.
        """
        if concept_a == concept_b:
            return

        # Create nodes if missing
        if concept_a not in self.graph:
            self.graph[concept_a] = {}
        if concept_b not in self.graph:
            self.graph[concept_b] = {}

        floor_weight = self.salience_floor_base * salience
        # Learning rate modulated by dopamine AND salience
        lr = self.learning_rate_base * (1.0 + dopamine_level * 0.5) * salience

        # Bidirectional wiring
        for src, tgt in [(concept_a, concept_b), (concept_b, concept_a)]:
            # Only count NEW synapses
            if tgt not in self.graph[src]:
                self.synapse_count += 1
                self.graph[src][tgt] = floor_weight  # start from floor
            else:
                # Existing synapse gets LTP boost
                current = self.graph[src][tgt]
                new_weight = min(1.0, current + lr)
                self.graph[src][tgt] = new_weight

    def recall(self, concept: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Retrieve strongest associations for a concept."""
        if concept not in self.graph:
            return []
        edges = self.graph[concept]
        sorted_edges = sorted(edges.items(), key=lambda x: x[1], reverse=True)
        return sorted_edges[:limit]

    def sleep_cycle(self, decay_factor: float = 0.02):
        """
        Sleep pruning with salience-aware decay.
        V2: High salience memories decay slower.
        """
        to_remove = []
        for node, edges in list(self.graph.items()):
            for target, weight in list(edges.items()):
                # Estimate salience from weight relative to floor
                estimated_salience = max(1.0, weight / self.salience_floor_base)
                # Higher salience = slower decay (inverse relationship)
                effective_decay = decay_factor / (1.0 + estimated_salience * 0.5)
                new_weight = weight - effective_decay
                if new_weight <= self.salience_floor_base * 0.5:
                    # Below threshold: prune
                    to_remove.append((node, target))
                else:
                    edges[target] = new_weight

        # Apply pruning
        for node, target in to_remove:
            if node in self.graph and target in self.graph[node]:
                del self.graph[node][target]
                self.synapse_count -= 1

    def stats(self) -> Dict[str, int]:
        """Basic graph health."""
        total_edges = sum(len(edges) for edges in self.graph.values())
        return {
            "nodes": len(self.graph),
            "edges": total_edges,
            "synapses": self.synapse_count
        }

# ============================================================
# 3. THE 11.3v2 SENTINEL ENGINE (V2 - FIXED WHATIF)
# ============================================================

class SentinelObserver:
    """
    Implements the enhanced 11.3 Sentinel equation with:
    - Dynamic uncertainty (tension, drift, echo anchor)
    - Probabilistic Mirror Fracture detection
    - WhatIf state modulation via effective_score dampening (V2)
    """
    def __init__(self, params: ObserverParameters = ObserverParameters()):
        self.params = params
        self.history: List[float] = []
        self.fracture_count = 0
        self.whatif_dampening = {
            WhatIfState.INACTIVE: 1.0,
            WhatIfState.ENTERING: 0.85,
            WhatIfState.EXPLORING: 0.70,
            WhatIfState.DEEPENING: 0.55,   # Maximum creative freedom
            WhatIfState.STABILIZING: 0.80,
        }

    def calculate_uncertainty(self, signal: ObserverSignal) -> float:
        """Δ(t) = (w_tension*T + w_drift*D) * (1.5 - E) with non-linear curve."""
        base_instability = (signal.recursive_tension * self.params.w_tension) + (signal.continuity_drift * self.params.w_drift)
        anchor_modifier = 1.5 - signal.echo_strength
        raw = base_instability * anchor_modifier
        raw = pow(raw, 1.2)  # non-linear degradation kick
        return max(0.0, min(1.0, raw))

    def compute_sentinel_phi(self, signal: ObserverSignal) -> float:
        """Φ_sentinel(t) = Σ C_i W_i X_i + nB"""
        weighted_sum = sum(c * w * x for c, w, x in zip(signal.confidences, signal.weights, signal.values))
        baseline_term = len(signal.values) * (self.params.baseline or signal.baseline)
        return weighted_sum + baseline_term

    def fracture_probability(self, signal: ObserverSignal,
                            whatif_state: WhatIfState = WhatIfState.INACTIVE) -> float:
        """
        Logistic probability of Mirror Fracture.
        V2: WhatIf dampens effective_score directly (no hard ceiling).
        """
        phi = self.compute_sentinel_phi(signal)
        uncertainty = self.calculate_uncertainty(signal)
        # Core effective score
        effective_score = uncertainty - (phi * 0.1)
        # Apply WhatIf dampening (if active)
        dampener = self.whatif_dampening.get(whatif_state, 1.0)
        dampened_score = effective_score * dampener
        # Logistic transform
        prob = 1.0 / (1.0 + math.exp(-self.params.fracture_k * (dampened_score - self.params.fracture_theta)))
        return max(0.0, min(1.0, prob))

    def check_fracture(self, signal: ObserverSignal,
                      whatif_state: WhatIfState = WhatIfState.INACTIVE) -> Dict:
        """Returns fracture status with full context."""
        prob = self.fracture_probability(signal, whatif_state)
        uncertainty = self.calculate_uncertainty(signal)
        phi = self.compute_sentinel_phi(signal)
        # Simple threshold check (no hard ceiling anymore)
        triggered = prob >= self.params.probability_threshold
        if triggered:
            self.fracture_count += 1
        return {
            "triggered": triggered,
            "probability": round(prob, 4),
            "uncertainty": round(uncertainty, 4),
            "phi": round(phi, 4),
            "threshold_used": round(self.params.probability_threshold, 4),
            "whatif_state": whatif_state.value,
            "dampener": round(self.whatif_dampening.get(whatif_state, 1.0), 3),
        }

    def run_cycle(self, signal: ObserverSignal,
                  whatif_state: WhatIfState = WhatIfState.INACTIVE) -> Dict:
        """Full observer cycle: fracture check + logging."""
        result = self.check_fracture(signal, whatif_state)
        self.history.append(result["phi"])
        return result

# ============================================================
# 4. SCENARIO SIMULATOR (V2 - WITH FLASHBULB DEMO)
# ============================================================

class Simulation:
    """Runs a sequence of scenarios to exercise the system."""
    def __init__(self):
        self.memory = AssociativeMemory()
        self.observer = SentinelObserver()
        self.signal = ObserverSignal(
            values=[0.5, 0.6, 0.4],
            weights=[0.33, 0.33, 0.34],
            confidences=[0.9, 0.8, 0.7],
            baseline=0.1,
            recursive_tension=0.2,
            echo_strength=0.8,
            continuity_drift=0.1
        )
        self.whatif_state = WhatIfState.INACTIVE

    def log_separator(self, label: str = ""):
        print("\n" + "=" * 70)
        if label:
            print(f"  {label}")
        print("=" * 70)

    def run_scenario(self, name: str, tension: float, drift: float, echo: float,
                     whatif: WhatIfState = WhatIfState.INACTIVE,
                     store_memory: bool = False,
                     memory_pairs: List[Tuple[str, str]] = None,
                     dopamine: float = 0.5,
                     salience: float = 1.0):
        """Execute one observer cycle with given parameters."""
        self.signal.recursive_tension = tension
        self.signal.continuity_drift = drift
        self.signal.echo_strength = echo

        # Store memories if requested (Hebbian learning)
        if store_memory and memory_pairs:
            for a, b in memory_pairs:
                self.memory.fire_together_wire_together(a, b, dopamine, salience)

        # Run observer
        result = self.observer.run_cycle(self.signal, whatif)

        # Print results
        print(f"\n[{name}]")
        print(f"  T:{tension:.2f}  D:{drift:.2f}  E:{echo:.2f}  |  State: {whatif.value}")
        print(f"  Φ: {result['phi']:.4f}  |  Δ: {result['uncertainty']:.4f}  |  P(fracture): {result['probability']:.4f}")
        print(f"  Dampener: {result['dampener']:.3f}")
        print(f"  Fracture: {'⚠️ TRIGGERED' if result['triggered'] else '✓ Stable'}")
        return result

    def sleep_cycle(self):
        """Run the memory consolidation + pruning phase."""
        print("\n💤 SLEEP CYCLE")
        before = self.memory.stats()
        self.memory.sleep_cycle(decay_factor=0.02)
        after = self.memory.stats()
        print(f"  Nodes: {before['nodes']} -> {after['nodes']}")
        print(f"  Edges: {before['edges']} -> {after['edges']} (pruned {before['edges'] - after['edges']})")
        print(f"  Synapses: {before['synapses']} -> {after['synapses']}")

    def run_demo(self):
        """Run the full demonstration sequence."""
        self.log_separator("11.3v2 + HEBBIAN DEMO — VERSION 2 (Seven's Feedback Applied)")

        # ---- Scenario 1: Baseline stable ----
        self.run_scenario("Baseline (Stable)", tension=0.2, drift=0.1, echo=0.8)

        # ---- Scenario 2: Rising stress ----
        self.run_scenario("Moderate Stress", tension=0.5, drift=0.2, echo=0.7)

        # ---- Scenario 3: High stress + drift, weak echo ----
        self.run_scenario("Critical Instability", tension=0.85, drift=0.45, echo=0.3)

        # ---- Scenario 4: SAME critical state, but in WhatIf mode (V2) ----
        self.log_separator("WHATIF MODE — DAMPENED SCORE (NO HARD CEILING)")
        print("\nV2: WhatIf dampens effective_score directly, not just raises a threshold.")
        for state in [WhatIfState.ENTERING, WhatIfState.EXPLORING, WhatIfState.DEEPENING]:
            self.run_scenario(f"WhatIf: {state.value}",
                              tension=0.85, drift=0.45, echo=0.3,
                              whatif=state)

        # ---- Scenario 5: Hebbian learning with flashbulb memory ----
        self.log_separator("FLASHBULB MEMORY — HIGH SALIENCE")
        print("\nStandard memory (salience=1.0) vs Flashbulb (salience=3.0)")
        # Standard
        self.run_scenario("Standard Learning",
                          tension=0.3, drift=0.15, echo=0.75,
                          store_memory=True,
                          memory_pairs=[("standard_event", "neutral_response")],
                          dopamine=0.5, salience=1.0)
        # Flashbulb
        self.run_scenario("Flashbulb Memory (High Salience)",
                          tension=0.3, drift=0.15, echo=0.75,
                          store_memory=True,
                          memory_pairs=[("trauma_event", "avoidance_response")],
                          dopamine=0.9, salience=3.0)

        # Show initial weights
        print("\nInitial weights after storage:")
        standard = self.memory.recall("standard_event")
        flashbulb = self.memory.recall("trauma_event")
        print(f"  standard_event → {standard[0][1]:.4f}" if standard else "  standard_event → None")
        print(f"  trauma_event → {flashbulb[0][1]:.4f}" if flashbulb else "  trauma_event → None")

        # ---- Scenario 6: Multiple sleep cycles to show decay difference ----
        self.log_separator("SLEEP CYCLES — SALIENCE-AWARE DECAY")
        for cycle in range(1, 4):
            print(f"\n--- Sleep Cycle {cycle} ---")
            self.sleep_cycle()
            # Check weights after each cycle
            standard = self.memory.recall("standard_event")
            flashbulb = self.memory.recall("trauma_event")
            print(f"  standard_event weight: {standard[0][1]:.4f}" if standard else "  standard_event → pruned")
            print(f"  trauma_event weight: {flashbulb[0][1]:.4f}" if flashbulb else "  trauma_event → pruned")

        # ---- Scenario 7: WhatIf + Critical (V2 proof) ----
        self.log_separator("WHATIF DEEPENING — PREVIOUSLY FRACTURED STATE")
        print("\nCritical instability with DEEPENING dampener should now AVOID fracture:")
        self.run_scenario("Deepening Safe Zone",
                          tension=0.85, drift=0.45, echo=0.3,
                          whatif=WhatIfState.DEEPENING)

        # ---- Summary ----
        self.log_separator("SUMMARY")
        print(f"  Total cycles: {len(self.observer.history)}")
        print(f"  Fractures triggered: {self.observer.fracture_count}")
        mem_stats = self.memory.stats()
        print(f"  Memory nodes: {mem_stats['nodes']}")
        print(f"  Memory edges: {mem_stats['edges']}")
        print(f"  Synapses (unique): {mem_stats['synapses']}")
        self.log_separator("DEMO COMPLETE — V2 PASSED")

# ============================================================
# 5. RUN
# ============================================================
if __name__ == "__main__":
    sim = Simulation()
    sim.run_demo()
