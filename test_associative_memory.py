#!/usr/bin/env python3
"""
Unit tests for AssociativeMemory's dirty-flag batch-save behavior.

Covers the earlier fix that deferred graph persistence: individual synapse
writes no longer trigger a full file rewrite; save() is a no-op when clean.

Runs against temporary files only.

Run:
    python3 -m unittest test_associative_memory -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sage_core.sentinel import AssociativeMemory


class AssociativeMemoryBatchSaveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "graph.json"

    def _new_mem(self):
        return AssociativeMemory(persistence_path=str(self.path))

    def _wire(self, mem, count=10):
        for i in range(count):
            mem.fire_together_wire_together(
                f"NODE_A_{i % 5}", f"NODE_B_{i % 5}", dopamine_level=0.6, salience=1.0
            )

    # --- wiring defers persistence -------------------------------------------

    def test_wiring_does_not_write_until_save(self):
        mem = self._new_mem()
        with mock.patch("json.dump") as dump:
            self._wire(mem, count=100)
            self.assertEqual(dump.call_count, 0)
            self.assertFalse(self.path.exists())

            mem.save()
            self.assertEqual(dump.call_count, 1)
            self.assertTrue(self.path.exists())

    def test_dirty_flag_lifecycle(self):
        mem = self._new_mem()
        self.assertFalse(mem._dirty)
        mem.fire_together_wire_together("A", "B")
        self.assertTrue(mem._dirty)
        mem.save()
        self.assertFalse(mem._dirty)

    def test_clean_save_is_noop(self):
        mem = self._new_mem()
        self._wire(mem, count=10)
        mem.save()

        with mock.patch("json.dump") as dump:
            mem.save()  # already clean — must not write again
            self.assertEqual(dump.call_count, 0)

    # --- batch save round-trips the graph ------------------------------------

    def test_batch_save_roundtrips_graph(self):
        mem = self._new_mem()
        mem.fire_together_wire_together("MERLIN", "ARCHITECT", dopamine_level=0.9, salience=2.0)
        mem.fire_together_wire_together("MERLIN", "SAGE_7", dopamine_level=0.9, salience=2.0)
        mem.save()

        data = json.loads(self.path.read_text())
        self.assertEqual(data["nodes"], 3)  # MERLIN, ARCHITECT, SAGE_7
        self.assertIn("ARCHITECT", data["graph"]["MERLIN"])
        self.assertIn("SAGE_7", data["graph"]["MERLIN"])

        expected_edges = sum(len(edges) for edges in data["graph"].values())
        self.assertEqual(data["synapses"], expected_edges)

        # A fresh instance must load the same in-memory state.
        mem2 = self._new_mem()
        self.assertEqual(mem2.synapse_count, mem.synapse_count)
        self.assertEqual(set(mem2.graph.keys()), set(mem.graph.keys()))

    # --- sleep cycle dirty behavior ------------------------------------------

    def test_sleep_cycle_persists_when_weights_change(self):
        mem = self._new_mem()
        mem.fire_together_wire_together("A", "B", salience=1.0)
        mem.save()

        with mock.patch("json.dump", wraps=json.dump) as dump:
            mem.sleep_cycle(decay_factor=0.02)
            self.assertEqual(dump.call_count, 1)
            self.assertFalse(mem._dirty)

    def test_sleep_cycle_on_empty_graph_does_not_write(self):
        mem = self._new_mem()
        with mock.patch("json.dump") as dump:
            mem.sleep_cycle(decay_factor=0.02)
            self.assertEqual(dump.call_count, 0)
            self.assertFalse(mem._dirty)

    # --- cross-process merge (no clobber) -----------------------------------

    def test_concurrent_writers_merge_without_clobber(self):
        # Two "workers" that each loaded the graph before the other saved.
        # Their independent saves must union, not clobber.
        mem_a = self._new_mem()
        mem_b = self._new_mem()

        mem_a.fire_together_wire_together("A", "X")
        mem_a.save()

        mem_b.fire_together_wire_together("B", "Y")
        mem_b.save()  # must merge A's edge into disk rather than overwrite it

        graph = json.loads(self.path.read_text())["graph"]
        self.assertIn("X", graph["A"])  # A's edge survived B's save
        self.assertIn("Y", graph["B"])  # B's edge present


if __name__ == "__main__":
    unittest.main(verbosity=2)
