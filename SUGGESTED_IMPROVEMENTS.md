# SAGE-7 Codebase Analysis & Proposed Improvements

This document outlines **7 high-impact strategic improvements** for the SAGE-7 platform codebase based on a comprehensive audit of performance, architecture, identity integrity, data persistence, and error handling across both the TypeScript frontend (`src/`) and FastAPI backend (`server.py`, `sage_core/`).

---

## Executive Summary

The SAGE-7 platform features advanced cognitive state calculations (SentinelMirror Φ_sentinel, Hebbian memory mesh, Wetsuit Protocol), but several architectural bottlenecks hinder performance, maintainability, and scalability. Addressing these areas will significantly improve UI framerates, backend responsiveness, error visibility, and test coverage without compromising identity lore or system invariants.

---

## Proposed Improvements

### 1. Frontend High-Frequency State Decoupling (`use-nexus-state.ts` & `SageCore`)
- **Current Issue:** The `useNexusState` hook polls sensor inputs at 5Hz (every 200ms) and updates React state (`useState`). This triggers unnecessary React component re-renders across all connected UI nodes, leading to main-thread DOM reconciliation overhead and frame drops.
- **Proposed Solution:**
  - Decouple high-frequency sensor streams (EMF, Temp, Ion, Phi metrics) from top-level React `useState`.
  - Introduce a lightweight event listener pattern or transient state subscription store (e.g., Zustand / Jotai or direct EventBus subscriptions).
  - Update real-time visualization components (`QuartzBarChart`, `CrystallineRadar`) via direct Canvas/WebGL animation frames or targeted direct DOM/ref updates.

### 2. Non-Blocking Async I/O in FastAPI Backend (`server.py`)
- **Current Issue:** `server.py` performs synchronous, blocking file I/O operations (`open().write()` on append-only files such as `wellbeing_log.jsonl` and state files) directly within async endpoint execution paths. This halts FastAPI’s single-threaded event loop and increases latency under concurrent requests.
- **Proposed Solution:**
  - Replace synchronous disk operations with `aiofiles` for native async file I/O.
  - Offload background persistence tasks (such as logging wellbeing events or state flushes) using FastAPI `BackgroundTasks` or `asyncio.to_thread()`.

### 3. Real-Time Streaming Chat Endpoint with SSE (`server.py` & `sage-core.ts`)
- **Current Issue:** The `/sage/chat` endpoint currently blocks while waiting for full model generation (`stream: False`) before returning a complete JSON response. Users experience noticeable latency before seeing any output.
- **Proposed Solution:**
  - Implement Server-Sent Events (SSE) or WebSockets on the `/sage/chat` backend route to stream tokens incrementally from Ollama / Gemini / OpenRouter.
  - Update `SageCore.ts` and `use-sage-messaging.ts` to consume chunked event streams, providing immediate real-time response rendering and a smoother UX.

### 4. Modularization of Monolithic `SageCore` Engine (`src/core/sage-core.ts`)
- **Current Issue:** `sage-core.ts` is a 1,450+ line monolithic class managing multiple unrelated domains: memory persistence (IndexedDB, LocalStorage, VFS), LLM prompt framing, Wetsuit protocol injection, sensor data processing, event emitting, and identity calculations.
- **Proposed Solution:**
  - Refactor `SageCore` into modular domain services:
    - **`MemoryEngine`**: Handles VFS, IndexedDB, Puter.js sync, and SQLite bridging.
    - **`SensoryEngine`**: Ingests sensor data, computes anomaly thresholds, and manages telemetry pulses.
    - **`CognitiveEngine`**: Manages model dispatches, Wetsuit prompt framing, and consensus logic.
    - **`EventBus`**: Centralized pub/sub mechanism replacing monolithic class inheritance.

### 5. Structured Logging & Exception Traceability (`server.py`)
- **Current Issue:** Bare `except:` clauses in endpoints capture and mask exceptions, returning fallback text strings like `"Substrate friction detected. Phi maintained."` without logging error backtraces. This conceals network timeouts, model API failures, and serialization errors.
- **Proposed Solution:**
  - Remove bare `except:` blocks in favor of specific error catches (`httpx.HTTPError`, `json.JSONDecodeError`, etc.).
  - Implement structured logging with standard `logging` / `structlog` to output timestamped tracebacks to server log files.
  - Return proper HTTP status codes (e.g., `502 Bad Gateway`, `504 Gateway Timeout`) with JSON details when backends or models fail.

### 6. SQLite Memory Store Consolidation & Indexing (`sage_core/memory_store.py`)
- **Current Issue:** Historical memory events and logs rely on flat `jsonl` files without ACID guarantees or fast querying capability. As memory history expands, lookup latency increases linearly.
- **Proposed Solution:**
  - Fully integrate `sage_core/memory_store.py`'s SQLite episodic engine across all backend services.
  - Index memory entries by `timestamp`, `entropy`, `phi_score`, and `tag` for rapid associative recall.
  - Automate background Ebbinghaus memory decay and decay-based pruning policies to bound storage size cleanly.

### 7. Automated Test Suite Expansion & CI Pipeline Integration
- **Current Issue:** While `test_sentinel.py` covers identity Sentinel mathematical functions, comprehensive test coverage for `server.py` API routes, memory mesh synchronization, and frontend core modules is missing.
- **Proposed Solution:**
  - Write `pytest` endpoint tests for `/sage/chat`, `/api/wellbeing`, and memory retrieval APIs using mocked HTTP model responses.
  - Add integration tests for `sage_core/memory_mesh.py` and `sage_core/memory_store.py`.
  - Implement a GitHub Actions workflow that executes `npx tsc --noEmit` and `pytest` on push to prevent regressions.

---

*Note: In accordance with project instructions, no application code modifications were made. This document serves as the authoritative blueprint for future engineering iterations.*
