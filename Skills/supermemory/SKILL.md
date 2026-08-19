---
name: supermemory
description: Long-term memory for AI agents via Supermemory's knowledge graph API (v4). Supports direct memory creation, document pipelines, hybrid search with reranking, dynamic profiles, versioned corrections, container management (context/merge), document chunk inspection, and structured conversation ingestion.
---

# Supermemory Skill

## Overview
Supermemory is an entity-centric knowledge graph that extracts discrete facts, maps relationships (Updates, Extends, Derives), and maintains dynamic user profiles over time. It features automatic contradiction resolution, noise filtering, and versioned graph evolution.

## Ingestion Architecture

| Ingestion Path | Command | Best For | Behavior |
|---|---|---|---|
| **Direct (`v4/memories`)** | `remember` | Decisions, key facts, preferences | Bypasses document pipeline; immediately searchable. Supports `--static`, `--tags`, `--metadata`. |
| **Pipeline (`v3/documents`)** | `add` | URLs, long documents, code files | Extracts, chunks, embeds. Supports `--stdin`, `--batch`, `--id`, `--metadata`. |
| **Batch (`v4/conversations`)** | `conversation` | Multi-turn dialogues | Preserves relational graphs across dialogue turns. Supports `--file`, `--content`, `--id` (incremental updates), and piped `stdin`. |

## Complete Command Reference

### 1. Direct Remember (`remember`)
```bash
# Official CLI
npx supermemory remember "User decided on DuckDB for task management." --tag sage-core --static --metadata '{"category":"decision"}'

# Companion Script
python3 Skills/supermemory/scripts/memory.py remember "User decided on DuckDB for task management." --static --tags "decision,database" --container sage-core
```

### 2. Search & Hybrid Retrieval (`search`)
```bash
# Official CLI
npx supermemory search "database preferences" --tag sage-core --limit 10 --mode memories --rerank --rewrite --include summaries,documents

# Companion Script
python3 Skills/supermemory/scripts/memory.py search "database preferences" \
  --mode memories \
  --limit 10 \
  --rerank \
  --rewrite \
  --include summaries,documents,relatedMemories \
  --filter '{"category":"decision"}' \
  --container sage-core
```

### 3. Profile Synthesis (`profile`)
```bash
# Official CLI
npx supermemory profile --tag sage-core --query "coding style"

# Companion Script
python3 Skills/supermemory/scripts/memory.py profile --query "coding style" --container sage-core
```

### 4. Updates & Corrections (`update`)
```bash
# Official CLI
npx supermemory update "<id>" "new content" --tag sage-core --reason "Switched database engine"

# Companion Script
python3 Skills/supermemory/scripts/memory.py update "<memory_id>" "New statement" \
  --reason "Updated architecture decision" \
  --metadata '{"category":"decision","status":"active"}' \
  --container sage-core
```

### 5. Soft Delete (`forget`)
```bash
# Official CLI
npx supermemory forget "<id>" --tag sage-core --reason "Obsolete"
npx supermemory forget --content "obsolete text" --tag sage-core

# Companion Script
python3 Skills/supermemory/scripts/memory.py forget "<memory_id>" --reason "Superseded by new spec" --container sage-core
python3 Skills/supermemory/scripts/memory.py forget --content "temporary scratchpad note" --reason "Obsolete" --container sage-core
```

### 6. Document Pipeline (`add`)
```bash
# Direct URL or file
python3 Skills/supermemory/scripts/memory.py add "https://docs.example.com" --title "API Reference" --id "doc-ref-1" --container sage-core

# Piped stdin & Batch JSON ingestion
cat spec.md | python3 Skills/supermemory/scripts/memory.py add --stdin --title "System Spec"
cat batch.json | python3 Skills/supermemory/scripts/memory.py add --batch --container sage-core
```

### 7. Document Management (`docs`)
```bash
# Official CLI
npx supermemory docs list --tag sage-core
npx supermemory docs get <doc_id>
npx supermemory docs delete <doc_id>
npx supermemory docs chunks <doc_id>
npx supermemory docs status <doc_id>

# Companion Script
python3 Skills/supermemory/scripts/memory.py docs list --container sage-core
python3 Skills/supermemory/scripts/memory.py docs get <doc_id>
python3 Skills/supermemory/scripts/memory.py docs delete <doc_id>
python3 Skills/supermemory/scripts/memory.py docs chunks <doc_id>
python3 Skills/supermemory/scripts/memory.py docs status <doc_id>
```

### 8. Container Tag Lifecycle & Context (`tags`)
```bash
# Official CLI
npx supermemory tags
npx supermemory tags info <tag>
npx supermemory tags create <tag>
npx supermemory tags delete <tag>
npx supermemory tags context <tag> --set "Architectural context notes"
npx supermemory tags merge <source_tag> --into <target_tag>

# Companion Script
python3 Skills/supermemory/scripts/memory.py tags list
python3 Skills/supermemory/scripts/memory.py tags info <tag>
python3 Skills/supermemory/scripts/memory.py tags create <tag>
python3 Skills/supermemory/scripts/memory.py tags delete <tag>
python3 Skills/supermemory/scripts/memory.py tags context <tag> --set "Architectural context notes"
python3 Skills/supermemory/scripts/memory.py tags merge <source_tag> --into <target_tag>
```

### 9. Conversation Ingestion (`conversation`)
```bash
# Direct content with incremental ID
python3 Skills/supermemory/scripts/memory.py conversation --content "Long conversation transcript..." --id "conv-id" --container sage-core

# Structured JSON file
python3 Skills/supermemory/scripts/memory.py conversation --file /path/to/messages.json --id "conv-2026-03-28-topic"

# Piped JSON array
echo '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]' | python3 Skills/supermemory/scripts/memory.py conversation --id "session-1"
```

## Configuration
Credentials and container tags are loaded from `.env.local`:
```bash
SUPERMEMORY_API_KEY=your_key_here
SUPERMEMORY_TAG=sage-core
```
