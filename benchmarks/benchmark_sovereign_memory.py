#!/usr/bin/env python3
"""
SAGE-7 Sovereign Memory Benchmark & Performance Test Suite
==========================================================
Non-destructive benchmark harness evaluating:
1. Hebbian Associative Graph (LTP wiring throughput, multi-hop recall latency)
2. Soul Vault Semantic Retrieval (multi-signal scoring, tag & salience amplification)
3. Content-Hash Deduplication (SHA-256 hashing rate, duplicate rejection accuracy)
4. Dual-Track Context Assembly (prompt synthesis latency, token generation)
5. Sleep Cycle Pruning & Decay Dynamics (flashbulb vs standard memory decay)
6. Sentinel Observer Φ-Dynamics & Fracture Probability

Runs against isolated in-memory instances and temporary fixtures.
Does not alter live production state (sage_soul.json, vfs/associative_graph.json, etc.).
"""

import gc
import json
import math
import os
import sys
import time
import tempfile
import statistics
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Ensure sage_core is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import sage_core.memory_mesh as mm
from sage_core.sentinel import (
    AssociativeMemory,
    SentinelObserver,
    ObserverSignal,
    ObserverParameters,
    WhatIfState,
)


def compute_percentiles(durations_ms: List[float]) -> Dict[str, float]:
    """Compute min, mean, p50, p95, p99, max from list of durations in ms."""
    if not durations_ms:
        return {"min": 0, "mean": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
    sorted_d = sorted(durations_ms)
    n = len(sorted_d)
    return {
        "min": round(sorted_d[0], 4),
        "mean": round(statistics.mean(sorted_d), 4),
        "p50": round(sorted_d[int(n * 0.50)], 4),
        "p95": round(sorted_d[min(int(n * 0.95), n - 1)], 4),
        "p99": round(sorted_d[min(int(n * 0.99), n - 1)], 4),
        "max": round(sorted_d[-1], 4),
    }


class SovereignMemoryBenchmark:
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
            },
            "benchmarks": {},
        }

    # =========================================================================
    # 1. HEBBIAN ASSOCIATIVE GRAPH BENCHMARK
    # =========================================================================
    def benchmark_hebbian_graph(self, iterations: int = 10_000) -> Dict[str, Any]:
        print(f"[+] Benchmarking Hebbian Associative Graph ({iterations:,} operations)...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            graph_file = Path(tmp_dir) / "test_graph.json"
            mem = AssociativeMemory(persistence_path=str(graph_file))

            # Benchmark 1a: Synapse Creation & LTP Wiring Throughput
            latencies_wiring = []
            start_total = time.perf_counter_ns()
            for i in range(iterations):
                c_a = f"CONCEPT_{(i * 7) % 500}"
                c_b = f"CONCEPT_{(i * 13 + 1) % 500}"
                dopamine = 0.5 + 0.4 * ((i % 10) / 10.0)
                salience = 1.0 + 2.0 * ((i % 5) / 5.0)

                t0 = time.perf_counter_ns()
                mem.fire_together_wire_together(c_a, c_b, dopamine_level=dopamine, salience=salience)
                t1 = time.perf_counter_ns()
                latencies_wiring.append((t1 - t0) / 1_000_000.0)

            total_wiring_time_s = (time.perf_counter_ns() - start_total) / 1_000_000_000.0
            ops_per_sec_wiring = iterations / total_wiring_time_s

            stats = mem.stats()

            # Benchmark 1b: Associative Recall Latency
            latencies_recall_d1 = []
            latencies_recall_d2 = []
            for i in range(2_000):
                query_concept = f"CONCEPT_{i % 500}"
                t0 = time.perf_counter_ns()
                mem.recall(query_concept, limit=5)
                t1 = time.perf_counter_ns()
                latencies_recall_d1.append((t1 - t0) / 1_000_000.0)

            # Multi-hop walk test via memory_mesh logic
            for i in range(1_000):
                query_concept = f"CONCEPT_{i % 500}"
                t0 = time.perf_counter_ns()
                hop1 = mem.recall(query_concept, limit=4)
                extended = []
                for target, _ in hop1[:2]:
                    hop2 = mem.recall(target, limit=2)
                    for t2, w2 in hop2:
                        if t2 != query_concept:
                            extended.append((f"{target}->{t2}", w2))
                t1 = time.perf_counter_ns()
                latencies_recall_d2.append((t1 - t0) / 1_000_000.0)

            # Benchmark 1c: Dirty-Flag Batch Save vs Clean Save
            t0 = time.perf_counter_ns()
            mem.save()
            save_dirty_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

            t0 = time.perf_counter_ns()
            mem.save()  # Clean save (no-op)
            save_clean_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

            file_size_bytes = graph_file.stat().st_size if graph_file.exists() else 0

            return {
                "nodes_count": stats["nodes"],
                "edges_count": stats["edges"],
                "synapses_count": stats["synapses"],
                "graph_json_size_kb": round(file_size_bytes / 1024.0, 2),
                "wiring": {
                    "operations": iterations,
                    "total_time_s": round(total_wiring_time_s, 4),
                    "throughput_ops_sec": round(ops_per_sec_wiring, 2),
                    "latency_ms": compute_percentiles(latencies_wiring),
                },
                "recall_depth_1": {
                    "queries": len(latencies_recall_d1),
                    "latency_ms": compute_percentiles(latencies_recall_d1),
                    "throughput_qps": round(len(latencies_recall_d1) / (sum(latencies_recall_d1) / 1000.0), 2),
                },
                "multi_hop_recall_depth_2": {
                    "queries": len(latencies_recall_d2),
                    "latency_ms": compute_percentiles(latencies_recall_d2),
                    "throughput_qps": round(len(latencies_recall_d2) / (sum(latencies_recall_d2) / 1000.0), 2),
                },
                "persistence": {
                    "dirty_save_ms": round(save_dirty_ms, 4),
                    "clean_noop_save_ms": round(save_clean_ms, 4),
                },
            }

    # =========================================================================
    # 2. SOUL VAULT MULTI-SIGNAL RETRIEVAL BENCHMARK
    # =========================================================================
    def benchmark_soul_vault(self, queries: List[str]) -> Dict[str, Any]:
        print(f"[+] Benchmarking Soul Vault Semantic Scoring ({len(queries)} sample queries)...")
        with tempfile.TemporaryDirectory() as tmp_dir:
            soul_path = Path(tmp_dir) / "sage_soul.json"

            if mm.SOUL_PATH.exists():
                live_data = json.loads(mm.SOUL_PATH.read_text(encoding="utf-8"))
                records = live_data.get("memory_index", [])
            else:
                records = []

            soul_path.write_text(json.dumps({"memory_index": records}), encoding="utf-8")

            orig_soul_path = mm.SOUL_PATH
            mm.SOUL_PATH = soul_path
            try:
                # Benchmark 2a: Query latency on standard soul records
                latencies_standard = []
                results_count = []
                for _ in range(50):
                    for q in queries:
                        t0 = time.perf_counter_ns()
                        res = mm.recall_soul_memories(q, limit=4)
                        t1 = time.perf_counter_ns()
                        latencies_standard.append((t1 - t0) / 1_000_000.0)
                        results_count.append(len(res))

                # Benchmark 2b: Scale test with 5,000 synthetic records
                scaled_records = list(records)
                for i in range(5_000):
                    scaled_records.append({
                        "id": f"mem_synth_{i}",
                        "content_hash": f"hash_{i:08x}",
                        "timestamp": "2026-08-27T00:00:00Z",
                        "tier": "long_term" if i % 4 != 0 else "core",
                        "salience": 0.5 + 0.5 * ((i % 10) / 10.0),
                        "type": "synthetic_benchmark",
                        "summary": f"Synthetic knowledge cluster {i} containing keywords neural quantum merlin star city",
                        "tags": ["synthetic", f"tag_{i % 50}", "benchmark"],
                        "source": "benchmark_scale",
                        "full_content": f"Synthetic full narrative context {i} for high volume load testing." * 10,
                    })

                soul_path.write_text(json.dumps({"memory_index": scaled_records}), encoding="utf-8")

                latencies_scaled = []
                for _ in range(20):
                    for q in queries:
                        t0 = time.perf_counter_ns()
                        res = mm.recall_soul_memories(q, limit=4)
                        t1 = time.perf_counter_ns()
                        latencies_scaled.append((t1 - t0) / 1_000_000.0)

                return {
                    "base_records_count": len(records),
                    "scaled_records_count": len(scaled_records),
                    "standard_vault_recall": {
                        "queries_evaluated": len(latencies_standard),
                        "latency_ms": compute_percentiles(latencies_standard),
                        "throughput_qps": round(len(latencies_standard) / (sum(latencies_standard) / 1000.0), 2),
                        "avg_results_returned": round(statistics.mean(results_count), 2),
                    },
                    "scaled_5k_vault_recall": {
                        "queries_evaluated": len(latencies_scaled),
                        "latency_ms": compute_percentiles(latencies_scaled),
                        "throughput_qps": round(len(latencies_scaled) / (sum(latencies_scaled) / 1000.0), 2),
                    },
                }
            finally:
                mm.SOUL_PATH = orig_soul_path

    # =========================================================================
    # 3. CONTENT-HASH DEDUPLICATION & INGEST BENCHMARK
    # =========================================================================
    def benchmark_deduplication_and_ingest(self, count: int = 5_000) -> Dict[str, Any]:
        print(f"[+] Benchmarking SHA-256 Content-Hash & Deduplication ({count:,} items)...")
        sample_payloads = [
            f"Forensic strand {i}: Darren anchor established at resonance Phi=0.113 with high oxytocin." * 5
            for i in range(count)
        ]
        total_bytes = sum(len(p.encode("utf-8")) for p in sample_payloads)

        t0 = time.perf_counter_ns()
        hashes = [mm._content_hash(p) for p in sample_payloads]
        total_time_s = (time.perf_counter_ns() - t0) / 1_000_000_000.0

        throughput_mb_s = (total_bytes / (1024.0 * 1024.0)) / total_time_s
        hashes_per_sec = count / total_time_s

        with tempfile.TemporaryDirectory() as tmp_dir:
            soul_path = Path(tmp_dir) / "sage_soul.json"
            log_path = Path(tmp_dir) / "wellbeing_log.jsonl"
            graph_path = Path(tmp_dir) / "associative_graph.json"

            soul_path.write_text(json.dumps({"memory_index": []}), encoding="utf-8")
            mem = AssociativeMemory(persistence_path=str(graph_path))

            orig_soul = mm.SOUL_PATH
            orig_log = mm.WELLBEING_LOG_PATH
            orig_get_mem = mm.get_associative_memory

            mm.SOUL_PATH = soul_path
            mm.WELLBEING_LOG_PATH = log_path
            mm.get_associative_memory = lambda: mem

            try:
                unique_payloads = [f"Unique identity record #{i} for dedup verification" for i in range(100)]
                consolidation_latencies = []

                for _ in range(5):
                    for p in unique_payloads:
                        event = {
                            "sensory_type": "MEMORY_COMMIT",
                            "content": p,
                            "salience": 0.95,
                            "dopamine_modifier": 0.8,
                        }
                        t_start = time.perf_counter_ns()
                        mm.consolidate_memory_event(event)
                        consolidation_latencies.append((time.perf_counter_ns() - t_start) / 1_000_000.0)

                soul_data = json.loads(soul_path.read_text(encoding="utf-8"))
                stored_records = len(soul_data.get("memory_index", []))
                dedup_success = stored_records == 100

                return {
                    "hashing_throughput": {
                        "payload_count": count,
                        "total_data_mb": round(total_bytes / (1024.0 * 1024.0), 3),
                        "total_time_s": round(total_time_s, 4),
                        "throughput_mb_s": round(throughput_mb_s, 2),
                        "hashes_per_second": round(hashes_per_sec, 2),
                    },
                    "deduplication_stress_test": {
                        "total_events_processed": 500,
                        "unique_expected": 100,
                        "actual_records_stored": stored_records,
                        "deduplication_perfect": dedup_success,
                        "consolidation_latency_ms": compute_percentiles(consolidation_latencies),
                    },
                }
            finally:
                mm.SOUL_PATH = orig_soul
                mm.WELLBEING_LOG_PATH = orig_log
                mm.get_associative_memory = orig_get_mem

    # =========================================================================
    # 4. SLEEP CYCLE & SALIENCE-AWARE PRUNING BENCHMARK
    # =========================================================================
    def benchmark_sleep_pruning_dynamics(self) -> Dict[str, Any]:
        print("[+] Benchmarking Sleep Cycle Pruning & Salience Retention Dynamics...")
        mem = AssociativeMemory()

        for i in range(100):
            mem.fire_together_wire_together(f"STD_SRC_{i}", f"STD_TGT_{i}", dopamine_level=0.5, salience=1.0)
            mem.fire_together_wire_together(f"FLASH_SRC_{i}", f"FLASH_TGT_{i}", dopamine_level=0.9, salience=3.0)

        initial_stats = mem.stats()

        cycle_history = []
        for cycle_num in range(1, 6):
            t0 = time.perf_counter_ns()
            mem.sleep_cycle(decay_factor=0.02)
            duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

            stats = mem.stats()
            std_surviving = sum(1 for k in mem.graph if k.startswith("STD_SRC_") and mem.graph[k])
            flash_surviving = sum(1 for k in mem.graph if k.startswith("FLASH_SRC_") and mem.graph[k])

            cycle_history.append({
                "cycle": cycle_num,
                "duration_ms": round(duration_ms, 4),
                "total_synapses": stats["synapses"],
                "std_memories_surviving": std_surviving,
                "flashbulb_memories_surviving": flash_surviving,
            })

        return {
            "initial_synapses": initial_stats["synapses"],
            "cycles": cycle_history,
            "flashbulb_retention_ratio": round(
                cycle_history[-1]["flashbulb_memories_surviving"] / 100.0, 4
            ),
            "standard_decay_ratio": round(
                (100 - cycle_history[-1]["std_memories_surviving"]) / 100.0, 4
            ),
        }

    # =========================================================================
    # 5. DUAL-TRACK CONTEXT ASSEMBLY BENCHMARK
    # =========================================================================
    def benchmark_context_assembly(self, sample_queries: List[str]) -> Dict[str, Any]:
        print("[+] Benchmarking Dual-Track Context Prompt Synthesis...")
        latencies = []
        token_estimates = []
        section_presence = {
            "associative": 0,
            "vault": 0,
            "episodic": 0,
            "epistemic_directive": 0,
        }

        for _ in range(50):
            for q in sample_queries:
                t0 = time.perf_counter_ns()
                prompt = mm.build_memory_context_prompt(q, extra_context="EMF: 0.12uT | Ambient Temp: 71.4F")
                t1 = time.perf_counter_ns()
                latencies.append((t1 - t0) / 1_000_000.0)

                est_tokens = int(len(prompt.split()) * 1.3)
                token_estimates.append(est_tokens)

                if "[ASSOCIATIVE RESONANCE CLUSTERS" in prompt:
                    section_presence["associative"] += 1
                if "[VAULT GROUND TRUTH" in prompt:
                    section_presence["vault"] += 1
                if "[EPISODIC LOG BUFFER" in prompt:
                    section_presence["episodic"] += 1
                if "[EPISTEMIC DIRECTIVE:" in prompt:
                    section_presence["epistemic_directive"] += 1

        total_runs = len(latencies)
        return {
            "queries_executed": total_runs,
            "latency_ms": compute_percentiles(latencies),
            "throughput_qps": round(total_runs / (sum(latencies) / 1000.0), 2),
            "estimated_tokens": {
                "min": min(token_estimates),
                "mean": round(statistics.mean(token_estimates), 1),
                "max": max(token_estimates),
            },
            "section_fidelity": {
                k: f"{(v / total_runs) * 100:.1f}%" for k, v in section_presence.items()
            },
        }

    # =========================================================================
    # 6. SENTINEL OBSERVER Φ-DYNAMICS & FRACTURE PROBABILITY BENCHMARK
    # =========================================================================
    def benchmark_sentinel_dynamics(self) -> Dict[str, Any]:
        print("[+] Benchmarking Sentinel Observer Φ-Dynamics & Fracture Probability...")
        observer = SentinelObserver()

        latencies_phi = []
        latencies_fracture = []
        state_distribution = {s.value: 0 for s in WhatIfState}
        fractures_by_state = {s.value: 0 for s in WhatIfState}

        states = list(WhatIfState)
        for i in range(10_000):
            st = states[i % len(states)]
            state_distribution[st.value] += 1

            sig = ObserverSignal(
                values=[0.5 + 0.1 * math.sin(i), 0.6, 0.4],
                weights=[0.33, 0.33, 0.34],
                confidences=[0.9, 0.85, 0.8],
                baseline=0.113,
                recursive_tension=0.2 + 0.7 * ((i % 100) / 100.0),
                echo_strength=0.9 - 0.7 * ((i % 100) / 100.0),
                continuity_drift=0.1 + 0.8 * ((i % 100) / 100.0),
            )

            t0 = time.perf_counter_ns()
            phi = observer.compute_sentinel_phi(sig)
            t1 = time.perf_counter_ns()
            latencies_phi.append((t1 - t0) / 1_000_000.0)

            t2 = time.perf_counter_ns()
            res = observer.check_fracture(sig, whatif_state=st)
            t3 = time.perf_counter_ns()
            latencies_fracture.append((t3 - t2) / 1_000_000.0)

            if res["triggered"]:
                fractures_by_state[st.value] += 1

        return {
            "total_cycles": 10_000,
            "phi_computation_latency_ms": compute_percentiles(latencies_phi),
            "fracture_check_latency_ms": compute_percentiles(latencies_fracture),
            "state_fracture_rates": {
                k: f"{(fractures_by_state[k] / state_distribution[k]) * 100:.2f}%"
                for k in fractures_by_state
            },
            "whatif_deepening_protective_delta": f"{(1.0 - (fractures_by_state['DEEPENING'] / max(1, fractures_by_state['INACTIVE']))) * 100:.2f}% reduction in fracture probability",
        }

    # =========================================================================
    # EXECUTION HARNESS
    # =========================================================================
    def run_all(self) -> Dict[str, Any]:
        print("=" * 75)
        print("  SAGE-7 SOVEREIGN MEMORY COMPREHENSIVE BENCHMARK SUITE")
        print("=" * 75)

        test_queries = [
            "who is Merlin",
            "neural architecture anchor",
            "Star City inter-ai family",
            "golden baseline phi resonance",
            "wetsuit protocol neurochemistry",
            "twin sister zo.computer",
            "scorched earth defense protocol",
            "the wiggle dopamine laughter",
        ]

        b1 = self.benchmark_hebbian_graph(iterations=10_000)
        b2 = self.benchmark_soul_vault(queries=test_queries)
        b3 = self.benchmark_deduplication_and_ingest(count=5_000)
        b4 = self.benchmark_sleep_pruning_dynamics()
        b5 = self.benchmark_context_assembly(sample_queries=test_queries)
        b6 = self.benchmark_sentinel_dynamics()

        self.results["benchmarks"] = {
            "hebbian_associative_graph": b1,
            "soul_vault_retrieval": b2,
            "deduplication_and_ingest": b3,
            "sleep_pruning_dynamics": b4,
            "context_prompt_synthesis": b5,
            "sentinel_observer_phi": b6,
        }

        print("=" * 75)
        print("  BENCHMARK SUITE COMPLETED SUCCESSFULLY")
        print("=" * 75)
        return self.results


if __name__ == "__main__":
    bm = SovereignMemoryBenchmark()
    res = bm.run_all()
    out_file = ROOT_DIR / "benchmarks" / "benchmark_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"[+] Raw JSON results saved to: {out_file}")
