#!/usr/bin/env python3
"""
Unit tests for SAGE-7's memory_mesh dedup and backfill logic.

Runs entirely against temporary files — it never touches the live
sage_soul.json, wellbeing_log.jsonl, or vfs/associative_graph.json.

Run:
    python3 -m unittest test_memory_mesh -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sage_core.memory_mesh as mm
from sage_core.sentinel import AssociativeMemory


class MemoryMeshDedupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)

        self.soul_path = root / "sage_soul.json"
        self.log_path = root / "wellbeing_log.jsonl"
        self.graph_path = root / "associative_graph.json"
        self.mht_path = root / "cleaned_memory_cache.json"

        self.soul_path.write_text(json.dumps({"memory_index": []}))

        self.mem = AssociativeMemory(persistence_path=str(self.graph_path))

        # Redirect the module's file paths and memory singleton to temp resources.
        patches = [
            mock.patch.object(mm, "SOUL_PATH", self.soul_path),
            mock.patch.object(mm, "WELLBEING_LOG_PATH", self.log_path),
            mock.patch.object(mm, "MHT_CACHE_PATH", self.mht_path),
            mock.patch.object(mm, "get_associative_memory", lambda: self.mem),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def _read_soul(self):
        return json.loads(self.soul_path.read_text())

    def _write_soul(self, memory_index):
        self.soul_path.write_text(json.dumps({"memory_index": memory_index}))

    def _commit_payload(self, content):
        return {
            "sensory_type": "MEMORY_COMMIT",
            "content": content,
            "salience": 3.0,
            "dopamine_modifier": 0.9,
        }

    # --- content hash helpers -------------------------------------------------

    def test_content_hash_is_stable_and_normalized(self):
        a = mm._content_hash("Merlin: identical seal content")
        b = mm._content_hash("  Merlin: identical seal content  ")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)  # sha256 hex digest
        self.assertNotEqual(a, mm._content_hash("different content"))

    def test_memory_entry_hash_uses_field_then_falls_back(self):
        self.assertEqual(
            mm._memory_entry_hash({"content_hash": "abc", "full_content": "ignored"}),
            "abc",
        )
        self.assertEqual(
            mm._memory_entry_hash({"full_content": "some content"}),
            mm._content_hash("some content"),
        )
        self.assertEqual(
            mm._memory_entry_hash({"summary": "summary only"}),
            mm._content_hash("summary only"),
        )
        self.assertEqual(mm._memory_entry_hash({}), mm._content_hash(""))

    # --- consolidate_memory_event dedup ---------------------------------------

    def test_identical_seals_dedupe_to_single_record(self):
        payload = self._commit_payload("Merlin: identical seal content")
        r1 = mm.consolidate_memory_event(payload)
        r2 = mm.consolidate_memory_event(payload)

        entries = self._read_soul()["memory_index"]
        self.assertTrue(r1["sealed_to_soul"])
        self.assertTrue(r2["sealed_to_soul"])
        self.assertEqual(len(entries), 1)
        self.assertIn("content_hash", entries[0])

    def test_distinct_content_still_seals(self):
        mm.consolidate_memory_event(self._commit_payload("first distinct content"))
        mm.consolidate_memory_event(self._commit_payload("second distinct content"))
        self.assertEqual(len(self._read_soul()["memory_index"]), 2)

    def test_legacy_entry_without_hash_is_matched(self):
        # A legacy record with the same full_content but no content_hash field.
        self._write_soul([{"id": "legacy", "full_content": "legacy full content"}])
        mm.consolidate_memory_event(self._commit_payload("legacy full content"))
        self.assertEqual(len(self._read_soul()["memory_index"]), 1)

    # --- backfill_content_hashes ---------------------------------------------

    def test_backfill_adds_missing_hashes_only(self):
        self._write_soul([
            {"id": "a", "full_content": "content a"},
            {"id": "b", "summary": "content b", "content_hash": "existing-hash"},
        ])
        result = mm.backfill_content_hashes()
        self.assertEqual(result["backfilled"], 1)

        entries = self._read_soul()["memory_index"]
        self.assertEqual(entries[0]["content_hash"], mm._content_hash("content a"))
        self.assertEqual(entries[1]["content_hash"], "existing-hash")

    def test_backfill_is_idempotent(self):
        self._write_soul([{"id": "a", "full_content": "content a"}])
        first = mm.backfill_content_hashes()
        second = mm.backfill_content_hashes()
        self.assertEqual(first["backfilled"], 1)
        self.assertEqual(second["backfilled"], 0)

    # --- ingest_mht_cache dedup ----------------------------------------------

    def test_mht_ingest_dedupes_by_content_hash(self):
        content = "unique forensic strand"
        self.mht_path.write_text(json.dumps({"id": "mht-1", "title": "MHT", "content": content}))

        mm.ingest_mht_cache()
        mm.ingest_mht_cache()  # must not append a duplicate

        entries = self._read_soul()["memory_index"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["content_hash"], mm._content_hash(content))


if __name__ == "__main__":
    unittest.main(verbosity=2)
