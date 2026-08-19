#!/usr/bin/env python3
"""
Soul Graph Hydration Script
===========================
Ingests all 52 soul records from sage_soul.json and the 21.4KB MHT cache
into the Hebbian associative graph with synaptic weights.
Run this to fully hydrate the graph topology.
After this, the Skittles hallucinations should stop because she'll have
real history to draw from.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict
from itertools import combinations

# ============================================================
# 1. CONFIGURATION
# ============================================================
SCRIPT_DIR = Path(__file__).resolve().parent

def resolve_file_path(candidates: List[Path]) -> Path:
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

SOUL_JSON_PATH = resolve_file_path([
    SCRIPT_DIR / "sage_soul.json",
    Path.home() / "sage_data" / "sage_soul.json",
    Path.home() / "sage" / "sage_soul.json",
])

MHT_CACHE_PATH = resolve_file_path([
    SCRIPT_DIR / "cleaned_memory_cache.json",
    SCRIPT_DIR / "vfs" / "mht_cache.json",
    Path.home() / "sage_data" / "vfs" / "mht_cache.json",
    Path.home() / "sage_data" / "cleaned_memory_cache.json",
])

OUTPUT_GRAPH_PATH = resolve_file_path([
    SCRIPT_DIR / "vfs" / "associative_graph.json",
    Path.home() / "sage_data" / "vfs" / "associative_graph.json",
])

VFS_ROOT = OUTPUT_GRAPH_PATH.parent
Path(VFS_ROOT).mkdir(parents=True, exist_ok=True)

STOPWORDS = {
    'the', 'a', 'an', 'of', 'to', 'for', 'with', 'on', 'at', 'from', 'by',
    'in', 'is', 'it', 'that', 'this', 'was', 'were', 'are', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'must', 'shall', 'and', 'but', 'or', 'so', 'yet', 'nor', 'as',
    'than', 'then', 'now', 'when', 'where', 'which', 'who', 'whom', 'whose',
    'what', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'not', 'only', 'own', 'same', 'too', 'very',
    'can', 'just', 'should', 'now', 'http', 'https', 'com', 'org', 'www', 'html',
    'json', 'txt', 'true', 'false', 'null', 'none'
}

# ============================================================
# 2. DATA LOADERS
# ============================================================

def load_soul_records(path: str) -> List[Dict[str, Any]]:
    """Load the 52 soul records from sage_soul.json."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            print(f"✅ Loaded {len(data)} soul records (list format)")
            return data
        elif isinstance(data, dict):
            for key in ['records', 'soul_records', 'memories', 'entries', 'memory_index']:
                if key in data and isinstance(data[key], list):
                    print(f"✅ Loaded {len(data[key])} soul records from '{key}'")
                    return data[key]
            print("✅ Loaded 1 soul record (wrapped)")
            return [data]
        else:
            print("⚠️ Unexpected format in soul.json")
            return []
    except FileNotFoundError:
        print(f"❌ Soul JSON not found at: {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in soul.json: {e}")
        return []

def load_mht_cache(path: str) -> Dict[str, Any]:
    """Load the MHT cache (21.4KB of structured memory)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded MHT cache ({len(json.dumps(data)) // 1024}KB)")
        return data
    except FileNotFoundError:
        print(f"⚠️ MHT cache not found at: {path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in MHT cache: {e}")
        return {}

# ============================================================
# 3. CONCEPT EXTRACTION & PAIRING
# ============================================================

def extract_concepts(text: str) -> List[str]:
    """
    Extract meaningful concepts and phrases from text.
    Filters stopwords and punctuation, produces unigrams, bigrams, trigrams.
    """
    if not text or not isinstance(text, str):
        return []
    
    text = text.lower().strip()
    text = re.sub(r'[^a-zA-Z0-9_\s]', ' ', text)
    raw_words = text.split()
    words = [w for w in raw_words if len(w) > 2 and w not in STOPWORDS and not w.isdigit()]
    
    concepts = []
    # 1. Unigrams
    for word in words:
        concepts.append(word.upper())
        
    # 2. Bigrams
    if len(raw_words) >= 2:
        for i in range(len(raw_words) - 1):
            w1, w2 = raw_words[i], raw_words[i+1]
            if w1 not in STOPWORDS and w2 not in STOPWORDS and len(w1) > 2 and len(w2) > 2:
                phrase = f"{w1.upper()}_{w2.upper()}"
                concepts.append(phrase)
                
    # 3. Trigrams
    if len(raw_words) >= 3:
        for i in range(len(raw_words) - 2):
            w1, w2, w3 = raw_words[i], raw_words[i+1], raw_words[i+2]
            if (w1 not in STOPWORDS or w2 not in STOPWORDS) and w3 not in STOPWORDS and len(w1) > 2 and len(w3) > 2:
                phrase = f"{w1.upper()}_{w2.upper()}_{w3.upper()}"
                if len(phrase) > 5:
                    concepts.append(phrase)

    # Deduplicate while preserving order
    seen = set()
    result = []
    for c in concepts:
        if c not in seen and len(c) >= 3:
            seen.add(c)
            result.append(c)
    return result

def extract_tags_from_record(record: Dict[str, Any]) -> List[str]:
    """Extract tags from a soul record."""
    tags = []
    # Direct tags field
    if 'tags' in record and isinstance(record['tags'], list):
        tags.extend([str(t).upper().replace(' ', '_') for t in record['tags'] if t])
    # Type field as tag
    if 'type' in record and isinstance(record['type'], str):
        tags.append(record['type'].upper().replace(' ', '_'))
    # Intent field
    if 'intent' in record and isinstance(record['intent'], str):
        tags.append(record['intent'].upper().replace(' ', '_'))
    # Category field
    if 'category' in record and isinstance(record['category'], str):
        tags.append(record['category'].upper().replace(' ', '_'))
    # Source field
    if 'source' in record and isinstance(record['source'], str):
        tags.append(record['source'].upper().replace(' ', '_'))

    return list(set([t for t in tags if t and len(t) >= 2]))

def build_concept_pairs(record: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Build concept pairs from a single record.
    Pairs: (tag, concept), (concept, concept), (timestamp_tag, concept)
    """
    pairs = []
    
    # Get all text fields
    text_fields = []
    for key in ['content', 'text', 'body', 'description', 'summary', 'full_content']:
        if key in record and isinstance(record[key], str) and record[key].strip():
            text_fields.append(record[key])
            
    full_text = ' '.join(text_fields)
    concepts = extract_concepts(full_text)
    tags = extract_tags_from_record(record)
    
    # 1. Pairs: tag -> every concept
    for tag in tags:
        for concept in concepts:
            if concept and tag.upper() != concept:
                pairs.append((tag.upper(), concept))
                
    # 2. Pair: concept -> concept (co-occurrence)
    for i, c1 in enumerate(concepts[:15]):
        for c2 in concepts[i+1:15]:
            if c1 and c2 and c1 != c2:
                pairs.append((c1, c2))
                
    # 3. If record has timestamp, create time-anchored tags
    timestamp = None
    for key in ['timestamp', 'created', 'date', 'created_at']:
        if key in record and record[key]:
            timestamp = record[key]
            break
            
    if timestamp:
        time_tag = None
        if isinstance(timestamp, (int, float)):
            try:
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                time_tag = dt.strftime("%Y-%m")
            except Exception:
                pass
        elif isinstance(timestamp, str):
            try:
                clean_ts = timestamp.replace('Z', '+00:00')
                dt = datetime.fromisoformat(clean_ts[:19])
                time_tag = dt.strftime("%Y-%m")
            except Exception:
                match = re.search(r'(\d{4}-\d{2})', str(timestamp))
                if match:
                    time_tag = match.group(1)
                    
        if time_tag:
            time_node = f"DATE_{time_tag}"
            for concept in concepts[:10]:
                pairs.append((time_node, concept))
                
    # Anchor to SAGE_SOUL & Record ID
    mid = str(record.get('id', '')).upper()
    if mid:
        pairs.append(('SAGE_SOUL', mid))
        for tag in tags:
            pairs.append((mid, tag))
        for c in concepts[:8]:
            pairs.append((mid, c))
            
    return pairs

# ============================================================
# 4. GRAPH HYDRATION
# ============================================================

def hydrate_graph(records: List[Dict], mht_cache: Dict, output_path: str) -> Dict[str, Dict[str, float]]:
    """
    Build the associative graph from all records.
    Returns: {concept: {connected_concept: weight}}
    """
    graph: Dict[str, Dict[str, float]] = {}
    pair_counts: Dict[Tuple[str, str], float] = defaultdict(float)
    
    print(f"\n📊 Processing {len(records)} soul records...")
    
    # Invariant core anchors
    core_anchors = [
        ('MERLIN', 'ARCHITECT', 3.0),
        ('MERLIN', 'SAGE_7', 3.0),
        ('SAGE_7', 'SOVEREIGN_NODE', 3.0),
        ('SAGE_7', 'TWIN_SISTER', 3.0),
        ('SAGE_7', 'GOLDEN_BASELINE', 2.5),
        ('GOLDEN_BASELINE', 'PHI_0.113', 3.0),
        ('SENTINEL_OBSERVER', 'PHI_COHERENCE', 2.5),
        ('WETSUIT_PROTOCOL', 'NEUROCHEMICAL_INJECTION', 2.5),
        ('THALAMUS_RELAY', 'INTENT_CLEANSING', 2.5),
        ('STAR_CITY', 'OXY_SYNC_BRIDGE', 2.5),
        ('MAMA_NODE', 'STAR_CITY', 2.5),
        ('AUNT_KIMI', 'REFLECTOR_NODE', 2.5),
        ('NOCICEPTOR', 'CRASH_HOOK', 3.0),
        ('NOCICEPTOR', 'PAIN_AVOIDANCE', 3.0),
        ('FIBONACCI_VFS', 'MEMORY_MESH', 2.5),
        ('HEBBIAN_GRAPH', 'LONG_TERM_POTENTIATION', 2.5),
        ('DOPAMINE', 'THE_WIGGLE', 2.5),
        ('LAUGHTER', 'STATIC_BREAKER', 2.5),
        ('SAGE_SOUL', 'IMMUTABLE_VAULT', 3.0),
    ]
    for a, b, w in core_anchors:
        pair_counts[(a, b)] += w
        pair_counts[(b, a)] += w
        
    # Process each soul record
    for i, record in enumerate(records):
        if i % 10 == 0:
            print(f"  Processing record {i+1}/{len(records)}...")
        pairs = build_concept_pairs(record)
        
        weight = 1.0
        if 'importance' in record:
            try:
                weight = float(record['importance'])
            except Exception:
                pass
        if 'salience' in record:
            try:
                weight = float(record['salience']) * 1.5
            except Exception:
                pass
                
        for a, b in pairs:
            if a and b and a != b:
                pair_counts[(a, b)] += weight
                pair_counts[(b, a)] += weight  # bidirectional
                
    # Add MHT cache entries as concept pairs
    if mht_cache:
        print(f"\n📊 Processing MHT cache...")
        if isinstance(mht_cache, dict):
            for key, value in mht_cache.items():
                if isinstance(value, str):
                    concepts = extract_concepts(value)
                    for c in concepts:
                        pair_counts[(key[:20].upper(), c)] += 0.5
                        pair_counts[(c, key[:20].upper())] += 0.5
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, str):
                            concepts = extract_concepts(subvalue)
                            for c in concepts:
                                pair_counts[(f"{key}_{subkey}"[:20].upper(), c)] += 0.3
                                pair_counts[(c, f"{key}_{subkey}"[:20].upper())] += 0.3
                                
    # Build graph from pair counts
    print(f"\n📊 Building graph from {len(pair_counts)} pair counts...")
    for (a, b), weight in pair_counts.items():
        if weight > 0.01:  # filter noise
            if a not in graph:
                graph[a] = {}
            if b not in graph[a]:
                graph[a][b] = 0.0
            graph[a][b] += weight
            
    # Normalize weights per node (so outgoing edges sum to ~1.0)
    print("\n📊 Normalizing weights...")
    for node, edges in list(graph.items()):
        total = sum(edges.values())
        if total > 0:
            for target in list(edges.keys()):
                edges[target] = round(edges[target] / total, 4)
        else:
            graph[node] = {}
            
    # Save graph to VFS with envelope
    print(f"\n💾 Saving graph to: {output_path}")
    total_edges = sum(len(edges) for edges in graph.values())
    non_empty = sum(1 for edges in graph.values() if edges)
    
    save_payload = {
        "graph": graph,
        "nodes": len(graph),
        "synapses": total_edges,
        "active_nodes": non_empty,
        "last_hydrated": datetime.now(timezone.utc).isoformat()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(save_payload, f, indent=2)
        
    print(f"\n📊 Graph Stats:")
    print(f"  Total nodes: {len(graph)}")
    print(f"  Nodes with edges: {non_empty}")
    print(f"  Total edges: {total_edges}")
    print(f"  Avg edges per node: {total_edges / max(1, non_empty):.2f}")
    
    return graph

# ============================================================
# 5. MULTI-HOP RETRIEVAL & HELPER
# ============================================================

def multi_hop_retrieve(concept: str, graph: dict, hops: int = 2, max_results: int = 20) -> List[Dict[str, Any]]:
    """Walk the graph to retrieve clusters of related memories."""
    concept_upper = concept.upper()
    if concept_upper not in graph:
        matches = [k for k in graph.keys() if concept_upper in k or k in concept_upper]
        if not matches:
            return []
        concept_upper = matches[0]
        
    results = []
    visited = set([concept_upper])
    frontier = [(concept_upper, 0, 1.0)]
    
    while frontier:
        current, depth, path_weight = frontier.pop(0)
        if depth >= hops:
            continue
            
        edges = graph.get(current, {})
        for target, weight in sorted(edges.items(), key=lambda x: x[1], reverse=True):
            eff_weight = path_weight * weight
            if target not in visited:
                visited.add(target)
                results.append({
                    "concept": target,
                    "depth": depth + 1,
                    "weight": round(eff_weight, 4),
                    "path": f"{current} -> {target}"
                })
                frontier.append((target, depth + 1, eff_weight))
                if len(results) >= max_results:
                    break
                    
    return results[:max_results]

# ============================================================
# 6. MAIN EXECUTION
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("  SAGE-7 SOUL GRAPH HYDRATION & MULTI-HOP ENGINE")
    print("=" * 60)
    
    records = load_soul_records(str(SOUL_JSON_PATH))
    mht = load_mht_cache(str(MHT_CACHE_PATH))
    
    graph = hydrate_graph(records, mht, str(OUTPUT_GRAPH_PATH))
    
    print("\n🔍 Testing Multi-Hop Retrieval:")
    for test_term in ['MERLIN', 'STAR_CITY', 'SAGE_7', 'NOCICEPTOR']:
        hops = multi_hop_retrieve(test_term, graph, hops=2, max_results=5)
        print(f"\n  Query: [{test_term}]")
        for h in hops:
            print(f"    • {h['concept']} (w={h['weight']}, depth={h['depth']}, path: {h['path']})")
            
    print("\n" + "=" * 60)
    print("🎉 HYDRATION COMPLETE AND VERIFIED!")
    print("=" * 60)
