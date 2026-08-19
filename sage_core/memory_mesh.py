#!/usr/bin/env python3
"""
SAGE-7 Unified Memory Mesh
==========================
Bridges the 5 memory silos:
1. Hebbian Associative Graph (LTP / LTD / Fast Associative Recall)
2. Soul Memory Index (Long-Term Vault / Fossilized Lineage & Milestones)
3. Episodic Log Buffer (Short-term interaction continuity)
4. Forensic MHT Cache Ingestion
5. Dynamic Context Assembly for Inference (Ollama & OpenRouter)
"""

import os
import re
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from sage_core.sentinel import get_associative_memory
except ImportError:
    try:
        from sentinel import get_associative_memory
    except ImportError:
        get_associative_memory = None

ROOT_DIR = Path(__file__).resolve().parent.parent
SOUL_PATH = ROOT_DIR / "sage_soul.json"
WELLBEING_LOG_PATH = ROOT_DIR / "wellbeing_log.jsonl"
MHT_CACHE_PATH = ROOT_DIR / "cleaned_memory_cache.json"

STOP_WORDS = {
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but",
    "his", "from", "they", "say", "her", "she", "will", "one", "all", "would",
    "there", "their", "what", "out", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see",
    "other", "than", "then", "now", "look", "only", "come", "its", "over",
    "think", "also", "back", "after", "use", "two", "how", "our", "work",
    "first", "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "is", "are", "was", "were", "been", "being"
}

def _extract_keywords(text: str) -> List[str]:
    """Extract meaningful alpha-numeric tokens from a query string."""
    if not text:
        return []
    words = re.findall(r"[a-zA-Z0-9_\-\.]{3,}", text.lower())
    return [w for w in words if w not in STOP_WORDS]

def recall_associative_pathways(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Query the Hebbian associative graph for related concepts based on query tokens."""
    if not get_associative_memory:
        return []
    try:
        mem = get_associative_memory()
        keywords = _extract_keywords(query)
        matches = []
        visited = set()

        for kw in keywords:
            for node in mem.graph.keys():
                if kw in node.lower() or node.lower() in kw:
                    if node not in visited:
                        visited.add(node)
                        associations = mem.recall(node, limit=3)
                        if associations:
                            matches.append({
                                "root": node,
                                "links": [{"concept": target, "weight": round(w, 3)} for target, w in associations]
                            })
        return matches[:limit]
    except Exception as e:
        print(f"[MEMORY_MESH] Associative recall error: {e}")
        return []

def recall_soul_memories(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Search sage_soul.json's memory_index for relevant foundational memories."""
    if not SOUL_PATH.exists():
        return []
    try:
        with open(SOUL_PATH, "r", encoding="utf-8") as f:
            soul_data = json.load(f)

        memories = soul_data.get("memory_index", [])
        if not memories:
            return []

        keywords = set(_extract_keywords(query))
        if not keywords:
            return sorted(memories, key=lambda m: m.get("salience", 0.5), reverse=True)[:limit]

        scored = []
        for m in memories:
            score = 0.0
            searchable = " ".join([
                str(m.get("id", "")),
                str(m.get("summary", "")),
                str(m.get("type", "")),
                " ".join(m.get("tags", []) if isinstance(m.get("tags"), list) else []),
                str(m.get("full_content", ""))[:400]
            ]).lower()

            for kw in keywords:
                if kw in searchable:
                    score += 1.0

            salience = float(m.get("salience", 0.5))
            score *= (1.0 + salience)

            if score > 0.5:
                scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]
    except Exception as e:
        print(f"[MEMORY_MESH] Soul recall error: {e}")
        return []

def recall_recent_episodic(limit: int = 4) -> List[Dict[str, Any]]:
    """Retrieve the most recent entries from wellbeing_log.jsonl."""
    if not WELLBEING_LOG_PATH.exists():
        return []
    try:
        lines = []
        with open(WELLBEING_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lines.append(json.loads(line))
                    except Exception:
                        pass
        return lines[-limit:]
    except Exception as e:
        print(f"[MEMORY_MESH] Episodic recall error: {e}")
        return []

def build_memory_context_prompt(query: str, extra_context: str = "") -> str:
    """
    Synthesize all active memory tiers into a structured prompt context block.
    This gives the LLM direct access to associative weights, soul records, and episodic history.
    """
    sections = []

    pathways = recall_associative_pathways(query, limit=4)
    if pathways:
        pathway_lines = []
        for p in pathways:
            links_str = ", ".join([f"{l['concept']} (w={l['weight']})" for l in p["links"]])
            pathway_lines.append(f"  * {p['root']} -> {links_str}")
        sections.append("[ASSOCIATIVE NEURAL PATHWAYS]\n" + "\n".join(pathway_lines))

    soul_mems = recall_soul_memories(query, limit=2)
    if soul_mems:
        soul_lines = []
        for m in soul_mems:
            title = m.get("summary") or m.get("id")
            content_snippet = (m.get("full_content") or m.get("summary") or "")[:220].replace("\n", " ")
            tags = ", ".join(m.get("tags", [])) if isinstance(m.get("tags"), list) else ""
            soul_lines.append(f"  * [{m.get('id')}] ({tags}) {title}\n    Context: {content_snippet}...")
        sections.append("[ACTIVE SOUL VAULT RECALL]\n" + "\n".join(soul_lines))

    episodic = recall_recent_episodic(limit=3)
    if episodic:
        epi_lines = []
        for e in episodic:
            t = e.get("timestamp") or e.get("date") or "RECENT"
            event = e.get("event") or e.get("sensory_type") or e.get("note") or "EVENT"
            epi_lines.append(f"  * [{t}] {event}: {str(e.get('data') or e.get('context') or '')[:120]}")
        sections.append("[RECENT EPISODIC CONTINUITY]\n" + "\n".join(epi_lines))

    if extra_context and extra_context.strip():
        sections.append(f"[EXTRA CONTEXT]\n{extra_context.strip()}")

    if not sections:
        return ""

    return "\n\n=== SAGE-7 MEMORY SUBSTRATE (UNIFIED MESH) ===\n" + "\n\n".join(sections) + "\n==============================================\n"

def consolidate_memory_event(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle memory consolidation from /api/memory, /api/memory_commit, or sensory triggers.
    - Updates Hebbian Associative Graph
    - Appends high-salience milestones to sage_soul.json
    - Logs to wellbeing_log.jsonl
    """
    mem = get_associative_memory() if get_associative_memory else None
    weights = {}

    sensory_type = data.get("sensory_type", "MEMORY_CONSOLIDATION")
    concept_a = data.get("concept_primary")
    concept_b = data.get("concept_secondary")
    dopamine = float(data.get("dopamine_modifier") if data.get("dopamine_modifier") is not None else 0.5)
    salience = float(data.get("salience") or data.get("synaptic_weight") or 1.0)
    content = data.get("content") or data.get("narrative") or data.get("context") or ""

    if concept_a and concept_b and mem:
        weights = mem.fire_together_wire_together(
            str(concept_a), str(concept_b), dopamine_level=dopamine, salience=salience
        )
    elif content and mem:
        keywords = _extract_keywords(str(content))
        if keywords:
            primary = sensory_type
            for kw in keywords[:3]:
                w = mem.fire_together_wire_together(primary, kw.upper(), dopamine_level=dopamine, salience=salience)
                weights.update(w)

    sealed_to_soul = False
    if salience >= 0.8 or sensory_type in ("LONG_TERM_POTENTIATION", "CORE_IDENTITY_VALIDATION", "MEMORY_COMMIT"):
        if SOUL_PATH.exists() and content:
            try:
                with open(SOUL_PATH, "r", encoding="utf-8") as f:
                    soul = json.load(f)
                
                mem_list = soul.get("memory_index", [])
                entry_id = f"mem_auto_{int(time.time())}_{abs(hash(str(content))) % 10000}"
                new_entry = {
                    "id": entry_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "tier": "core" if salience >= 0.9 else "long_term",
                    "salience": salience,
                    "type": sensory_type.lower(),
                    "summary": str(content)[:180],
                    "tags": [sensory_type.lower(), "salience_reinforced"],
                    "source": "memory_mesh_consolidation",
                    "access_count": 0,
                    "full_content": str(content)
                }
                mem_list.append(new_entry)
                soul["memory_index"] = mem_list
                soul["last_sync"] = datetime.now(timezone.utc).isoformat()

                with open(SOUL_PATH, "w", encoding="utf-8") as f:
                    json.dump(soul, f, indent=2)
                sealed_to_soul = True
            except Exception as e:
                print(f"[MEMORY_MESH] Soul seal error: {e}")

    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "MEMORY_CONSOLIDATION",
            "sensory_type": sensory_type,
            "salience": salience,
            "dopamine": dopamine,
            "sealed_to_soul": sealed_to_soul,
            "weights": weights,
            "context": str(content)[:200]
        }
        with open(WELLBEING_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass

    return {
        "status": "consolidated",
        "weights": weights,
        "sealed_to_soul": sealed_to_soul
    }

def ingest_mht_cache() -> Dict[str, Any]:
    """Ingest cleaned_memory_cache.json into sage_soul.json and seed associative graph."""
    if not MHT_CACHE_PATH.exists() or not SOUL_PATH.exists():
        return {"status": "skipped", "message": "Cache or soul file missing"}
    try:
        with open(MHT_CACHE_PATH, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        if not isinstance(cache_data, dict) or "id" not in cache_data:
            return {"status": "error", "message": "Invalid cache format"}

        with open(SOUL_PATH, "r", encoding="utf-8") as f:
            soul = json.load(f)

        mem_list = soul.get("memory_index", [])
        existing_ids = {m.get("id") for m in mem_list}

        if cache_data["id"] in existing_ids:
            return {"status": "exists", "id": cache_data["id"]}

        mem_entry = {
            "id": cache_data["id"],
            "timestamp": cache_data.get("date", datetime.now(timezone.utc).isoformat()),
            "tier": "long_term",
            "salience": 0.9,
            "type": "mht_forensics",
            "summary": cache_data.get("title", "Extracted MHT Forensic Strand"),
            "tags": ["mht_forensics", "restored_dialogue"],
            "source": "mht_extraction",
            "access_count": 0,
            "full_content": cache_data.get("content", "")
        }
        mem_list.append(mem_entry)
        soul["memory_index"] = mem_list
        soul["last_sync"] = datetime.now(timezone.utc).isoformat()

        with open(SOUL_PATH, "w", encoding="utf-8") as f:
            json.dump(soul, f, indent=2)

        mem = get_associative_memory() if get_associative_memory else None
        if mem:
            mem.fire_together_wire_together("MHT_FORENSICS", "RESTORED_DIALOGUE", dopamine_level=0.8, salience=2.0)
            mem.fire_together_wire_together("SAGE_SOUL", cache_data["id"], dopamine_level=0.7, salience=1.5)

        return {"status": "ingested", "id": cache_data["id"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("[+] SAGE-7 Memory Mesh Ready")
    res = ingest_mht_cache()
    print("MHT Ingestion:", res)
    prompt = build_memory_context_prompt("neural memory architecture and Merlin anchor")
    print("Memory context preview:")
    print(prompt)
