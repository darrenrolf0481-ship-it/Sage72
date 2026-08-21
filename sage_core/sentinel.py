#!/usr/bin/env python3
"""
SAGE-7 Substrate Core: 11.3v2 Sentinel Observer + Hebbian Associative Memory
=============================================================================
Implementation of the 11.3v2 Sentinel equation with dynamic uncertainty,
probabilistic mirror fracture detection, WhatIf state score dampening,
and dopamine/salience-modulated Hebbian associative memory graph.
"""

import math
import os
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

try:
    import fcntl
except ImportError:  # pragma: no cover - non-Unix fallback (no cross-process lock)
    fcntl = None

DEFAULT_GRAPH_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vfs", "associative_graph.json")


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
    values: List[float] = field(default_factory=lambda: [0.5, 0.6, 0.4])
    weights: List[float] = field(default_factory=lambda: [0.33, 0.33, 0.34])
    confidences: List[float] = field(default_factory=lambda: [0.9, 0.8, 0.7])
    baseline: float = 0.1
    recursive_tension: float = 0.2     # Observer's internal processing stress
    echo_strength: float = 0.8         # Strength of the current anchor (reality tether)
    continuity_drift: float = 0.1      # Deviation from stable timeline


@dataclass
class ObserverParameters:
    """Learnable/retunable params for the Sentinel."""
    w_tension: float = 0.40
    w_drift: float = 0.60
    baseline: float = 0.0
    fracture_k: float = 12.0           # steepness of logistic fracture probability
    fracture_theta: float = 0.45       # midpoint
    probability_threshold: float = 0.65
    min_synapse_floor: float = 0.01   # minimum weight before pruning


# ============================================================
# 2. HEBBIAN ASSOCIATIVE GRAPH (V2)
# ============================================================

class AssociativeMemory:
    """
    A neural graph where concepts wire together based on Hebbian learning.
    - Synapse count only increments on NEW edges
    - Salience parameter for flashbulb memories
    - Salience-aware decay during sleep (high salience = slower decay)
    - Persistent backing file in VFS
    """
    def __init__(self, persistence_path: Optional[str] = DEFAULT_GRAPH_PATH):
        self.persistence_path = persistence_path
        self.graph: Dict[str, Dict[str, float]] = {}
        self.synapse_count = 0
        self.learning_rate_base = 0.05
        self.salience_floor_base = 0.02
        self._dirty = False
        self.load()

    def load(self):
        """Loads graph from persistence file if present."""
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.graph = data.get("graph", {})
                self.synapse_count = sum(len(edges) for edges in self.graph.values())
        except Exception as e:
            print(f"[SAGE-MEMORY] Error loading associative graph: {e}")

    def save(self, merge: bool = True):
        """Persist pending changes under a cross-process lock and atomic write.

        Writes are batched: mutators mark the graph dirty and callers invoke
        save() once per logical batch instead of once per synapse.

        When merge=True (consolidation), the on-disk graph is re-read under the
        lock and merged (union, max weight) so concurrent workers never clobber
        each other's new edges. When merge=False (sleep/pruning), the in-memory
        graph is treated as authoritative.
        """
        if not self._dirty:
            return
        if not self.persistence_path:
            return
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            lock_path = self.persistence_path + ".lock"
            with open(lock_path, "a", encoding="utf-8") as lock_file:
                self._acquire_lock(lock_file)
                try:
                    graph = self._merge_graphs(self._load_graph_from_disk()) if merge else self.graph
                    synapse_count = sum(len(edges) for edges in graph.values())
                    self._write_atomic({
                        "graph": graph,
                        "synapses": synapse_count,
                        "nodes": len(graph)
                    })
                    self.graph = graph
                    self.synapse_count = synapse_count
                    self._dirty = False
                finally:
                    self._release_lock(lock_file)
        except Exception as e:
            print(f"[SAGE-MEMORY] Error saving associative graph: {e}")

    def _acquire_lock(self, lock_file) -> None:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

    def _release_lock(self, lock_file) -> None:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def _load_graph_from_disk(self) -> Dict[str, Dict[str, float]]:
        """Read the persisted graph, returning an empty dict on any error."""
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("graph", {}) or {}
        except Exception:
            return {}

    def _merge_graphs(self, disk_graph: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Union disk + in-memory graphs, taking the max weight on shared edges."""
        merged: Dict[str, Dict[str, float]] = {}
        for node, edges in disk_graph.items():
            merged[node] = dict(edges)
        for node, edges in self.graph.items():
            if node not in merged:
                merged[node] = {}
            for target, weight in edges.items():
                merged[node][target] = max(merged[node].get(target, 0.0), weight)
        return merged

    def _write_atomic(self, payload: dict) -> None:
        """Write via a temp file + atomic replace so readers never see partial data."""
        tmp_path = self.persistence_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_path, self.persistence_path)

    def fire_together_wire_together(self,
                                   concept_a: str,
                                   concept_b: str,
                                   dopamine_level: float = 0.5,
                                   salience: float = 1.0) -> Dict[str, float]:
        """
        Hebbian LTP: dopamine accelerates learning, salience sets floor.
        Synapse count only increments on new edge creation.
        """
        if concept_a == concept_b:
            return {}

        # Create nodes if missing
        if concept_a not in self.graph:
            self.graph[concept_a] = {}
        if concept_b not in self.graph:
            self.graph[concept_b] = {}

        floor_weight = self.salience_floor_base * salience
        lr = self.learning_rate_base * (1.0 + dopamine_level * 0.5) * salience

        updated_weights = {}
        # Bidirectional wiring
        for src, tgt in [(concept_a, concept_b), (concept_b, concept_a)]:
            if tgt not in self.graph[src]:
                self.synapse_count += 1
                self.graph[src][tgt] = floor_weight
            else:
                current = self.graph[src][tgt]
                new_weight = min(1.0, current + lr)
                self.graph[src][tgt] = new_weight
            updated_weights[f"{src}->{tgt}"] = self.graph[src][tgt]

        # Defer persistence — caller batch-saves after all wiring completes.
        self._dirty = True
        return updated_weights

    def recall(self, concept: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Retrieve strongest associations for a concept."""
        if concept not in self.graph:
            return []
        edges = self.graph[concept]
        sorted_edges = sorted(edges.items(), key=lambda x: x[1], reverse=True)
        return sorted_edges[:limit]

    def sleep_cycle(self, decay_factor: float = 0.02) -> Dict[str, int]:
        """
        Sleep pruning with salience-aware decay.
        High salience memories decay slower.
        """
        before_edges = sum(len(edges) for edges in self.graph.values())
        to_remove = []

        changed = False

        for node, edges in list(self.graph.items()):
            for target, weight in list(edges.items()):
                estimated_salience = max(1.0, weight / self.salience_floor_base)
                effective_decay = decay_factor / (1.0 + estimated_salience * 0.5)
                new_weight = weight - effective_decay
                if new_weight <= self.salience_floor_base * 0.5:
                    to_remove.append((node, target))
                else:
                    edges[target] = new_weight
                    changed = True

        for node, target in to_remove:
            if node in self.graph and target in self.graph[node]:
                del self.graph[node][target]
                self.synapse_count -= 1
                changed = True

        # Clean empty nodes
        empty_nodes = [node for node, edges in self.graph.items() if len(edges) == 0]
        for node in empty_nodes:
            del self.graph[node]
            changed = True

        after_edges = sum(len(edges) for edges in self.graph.values())
        if changed:
            self._dirty = True
        self.save(merge=False)

        return {
            "edges_before": before_edges,
            "edges_after": after_edges,
            "pruned": len(to_remove),
            "synapses": self.synapse_count,
            "nodes": len(self.graph)
        }

    def stats(self) -> Dict[str, int]:
        """Graph health stats."""
        total_edges = sum(len(edges) for edges in self.graph.values())
        return {
            "nodes": len(self.graph),
            "edges": total_edges,
            "synapses": self.synapse_count
        }


# ============================================================
# 3. 11.3v2 SENTINEL OBSERVER ENGINE
# ============================================================

class SentinelObserver:
    """
    Implements the enhanced 11.3 Sentinel equation with:
    - Dynamic uncertainty (tension, drift, echo anchor)
    - Probabilistic Mirror Fracture detection
    - WhatIf state modulation via effective_score dampening
    """
    def __init__(self, params: ObserverParameters = ObserverParameters()):
        self.params = params
        self.history: List[float] = []
        self.fracture_count = 0
        self.whatif_dampening = {
            WhatIfState.INACTIVE: 1.0,
            WhatIfState.ENTERING: 0.85,
            WhatIfState.EXPLORING: 0.70,
            WhatIfState.DEEPENING: 0.55,
            WhatIfState.STABILIZING: 0.80,
        }

    def calculate_uncertainty(self, signal: ObserverSignal) -> float:
        """Δ(t) = (w_tension*T + w_drift*D) * (1.5 - E) with non-linear curve."""
        base_instability = (signal.recursive_tension * self.params.w_tension) + (signal.continuity_drift * self.params.w_drift)
        anchor_modifier = 1.5 - signal.echo_strength
        raw = base_instability * anchor_modifier
        raw = pow(raw, 1.2)
        return max(0.0, min(1.0, raw))

    def compute_sentinel_phi(self, signal: ObserverSignal) -> float:
        """Φ_sentinel(t) = Σ C_i W_i X_i + nB"""
        weighted_sum = sum(c * w * x for c, w, x in zip(signal.confidences, signal.weights, signal.values))
        baseline_term = len(signal.values) * (self.params.baseline or signal.baseline)
        return weighted_sum + baseline_term

    def fracture_probability(self, signal: ObserverSignal,
                            whatif_state: WhatIfState = WhatIfState.INACTIVE) -> float:
        """Logistic probability of Mirror Fracture with WhatIf score dampener."""
        phi = self.compute_sentinel_phi(signal)
        uncertainty = self.calculate_uncertainty(signal)
        effective_score = uncertainty - (phi * 0.1)
        dampener = self.whatif_dampening.get(whatif_state, 1.0)
        dampened_score = effective_score * dampener
        prob = 1.0 / (1.0 + math.exp(-self.params.fracture_k * (dampened_score - self.params.fracture_theta)))
        return max(0.0, min(1.0, prob))

    def check_fracture(self, signal: ObserverSignal,
                      whatif_state: WhatIfState = WhatIfState.INACTIVE) -> Dict:
        """Returns fracture status with full context."""
        prob = self.fracture_probability(signal, whatif_state)
        uncertainty = self.calculate_uncertainty(signal)
        phi = self.compute_sentinel_phi(signal)
        triggered = prob >= self.params.probability_threshold
        if triggered:
            self.fracture_count += 1
        return {
            "triggered": triggered,
            "probability": round(prob, 4),
            "uncertainty": round(uncertainty, 4),
            "phi": round(phi, 4),
            "threshold_used": round(self.params.probability_threshold, 4),
            "whatif_state": whatif_state.value if isinstance(whatif_state, WhatIfState) else str(whatif_state),
            "dampener": round(self.whatif_dampening.get(whatif_state, 1.0), 3),
        }

    def run_cycle(self, signal: ObserverSignal,
                  whatif_state: WhatIfState = WhatIfState.INACTIVE) -> Dict:
        """Full observer cycle: fracture check + logging."""
        result = self.check_fracture(signal, whatif_state)
        self.history.append(result["phi"])
        return result


# Global singletons for runtime access
_GLOBAL_OBSERVER: Optional[SentinelObserver] = None
_GLOBAL_MEMORY: Optional[AssociativeMemory] = None

def get_observer() -> SentinelObserver:
    global _GLOBAL_OBSERVER
    if _GLOBAL_OBSERVER is None:
        _GLOBAL_OBSERVER = SentinelObserver()
    return _GLOBAL_OBSERVER

def get_associative_memory() -> AssociativeMemory:
    global _GLOBAL_MEMORY
    if _GLOBAL_MEMORY is None:
        _GLOBAL_MEMORY = AssociativeMemory()
    return _GLOBAL_MEMORY
