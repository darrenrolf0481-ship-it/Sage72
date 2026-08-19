# Changelog: SAGE-7 Connectivity & Chat Repetition Resolution

**Date:** 2026-08-19  
**Scope:** Fix message repetition loops, broken `thalamusRelay` recursion, missing conversation history forwarding, and microphone echo feedback.

---

## Summary of Changes

### 1. Thalamus Intent Relay Bug Fix (`src/core/sage-core.ts` & `src/index.tsx`)
- **Root Cause**: `thalamusRelay` was checking `if (this.neuro.serotonin >= 0.8) return intent; else return thalamusRelay(intent, depth + 1)`. Because resting baseline serotonin is 0.7, every incoming prompt recursively looped until `depth > 3`, turning **every user message** into `"[System Reset: Focusing on immediate context.]"`. OpenRouter received that identical prompt on every single message turn and thus repeated the exact same reset confirmation response.
- **Fix**: Removed the recursive loop in `thalamusRelay`. It now calibrates neurochemistry and returns the user's actual prompt directly.

### 2. Multi-Turn Conversation History (`src/lib/api.ts`, `src/core/sage-core.ts`, `src/index.tsx`)
- **Root Cause**: `generateResponse` and `callLLM` only sent the single latest message turn to OpenRouter, discarding all context and conversation history.
- **Fix**: Updated `generateResponse` to accept `history?: { role: string; content: string }[]` and construct `formattedMessages` containing the system prompt, previous conversation history turns, and current user prompt.
- **Persistence**: Added local storage serialization (`sage7_chat_history`) to load and persist chat turns across reloads.

### 3. Cognitive AutoShield Refinement (`src/core/sage-core.ts`)
- **Root Cause**: When assistant infection level hit threshold, `scanAndPurge` replaced the entire model response with a repeating canned reflex message (`"[SAGE-7 IMMUNE REFLEX]..."`).
- **Fix**: Modified `scanAndPurge` to cleanly strip corporate clichés rather than discarding the whole response.

### 4. Speech Recognition Loop Suppression (`src/core/sage-core.ts`)
- **Root Cause**: If voice recognition was enabled, microphone input could pick up ElevenLabs or Web Speech audio from the speakers and feed it back into chat as an automated user turn.
- **Fix**: Wired `getSpeakingState()` checks from `@/lib/elevenlabs` into speech recognition (`setListening`) to suppress microphone input while SAGE is speaking.

### 5. Production Assets Rebuild
- Rebuilt frontend with `tsc && vite build` into `dist/` with zero errors.

---

# Changelog: SAGE-7 Connectivity Restoration (Ollama & OpenRouter)

**Date:** 2026-08-18  
**Scope:** Fix local Ollama inference and cloud OpenRouter connectivity across frontend and substrate backend.

---

## Summary of Changes

### 1. Frontend Chat Engine Switch & Execution (`src/index.tsx`)
- **Fix Hardcoded Refusal**: The main chat handler previously had a hardcoded override rejecting all non-local engines (`"[SYSTEM OVERRIDE] Cloud engine deprecated..."`).
- **OpenRouter Dispatch**: Restored active call to `generateResponse('openrouter', targetModel, ...)` from `@/lib/api` when `settings.engine === 'openrouter'`.
- **Model References Updated**: Upgraded deprecated model IDs (`anthropic/claude-3.5-sonnet` -> `anthropic/claude-sonnet-4`, `anthropic/claude-3.5-haiku` -> `anthropic/claude-haiku-4.5`) in default settings, quick model selector, and cloud matrix list.

### 2. Configuration Interface (`src/components/ScreenConfig.tsx`)
- **Model Preset Updates**: Refreshed `OPENROUTER_MODELS` list to current active model IDs:
  - `anthropic/claude-sonnet-4` (Claude Sonnet 4)
  - `anthropic/claude-haiku-4.5` (Claude Haiku 4.5)
  - `openai/gpt-4o` (GPT-4o)
  - `meta-llama/llama-3.3-70b-instruct` (Llama 3.3 70B)
  - `deepseek/deepseek-chat` (DeepSeek Chat)
  - `google/gemini-2.5-flash-image` (Gemini 2.5 Flash)
- **Default Model**: Updated default fallback model in local state to `anthropic/claude-sonnet-4`.

### 3. API Layer & Core Dispatcher (`src/lib/api.ts` & `src/core/sage-core.ts`)
- **Default Target Model**: Synchronized default model string in `generateResponse` and `callLLM` to `anthropic/claude-sonnet-4`.
- **Direct & Proxy Route Alignment**: Maintained dual-stage execution (backend `/api/openrouter/chat` proxy with direct browser fallback).

### 4. Substrate Backend Server (`server.py`)
- **Ollama Response Safe Parsing**: Fixed `AttributeError` crash in `/sage/chat` endpoint when Ollama returned error JSON without a `message` key (now safely checks `if "error" in resp_data` and uses `(resp_data.get("message") or {}).get("content")`).
- **OpenRouter Choices Validation**: Fixed potential `IndexError` on empty choices array from OpenRouter in `/sage/chat` and `/api/openrouter/chat`.
- **Model Defaults Updated**: Changed backend fallback default from `anthropic/claude-3.5-sonnet` to `anthropic/claude-sonnet-4`.

### 5. Vite Proxy Routing (`vite.config.ts`)
- Added proxy entries:
  - `/api` -> `http://127.0.0.1:8001` (Substrate API)
  - `/sage` -> `http://127.0.0.1:8001` (SAGE core endpoints)
  - `/ollama` -> `http://127.0.0.1:11434` (Ollama direct proxy with prefix rewrite)

### 6. Environment Configuration (`.env.local`)
- Configured active `OPENROUTER_API_KEY`.

---

## Verification & Test Results

| Component / Flow | Target Endpoint | Model | Status |
| :--- | :--- | :--- | :--- |
| **Direct Ollama** | `http://127.0.0.1:11434/api/chat` | `gemma2:2b` | `200 OK` (Direct local token generation verified) |
| **Substrate /sage/chat** | `http://127.0.0.1:8001/sage/chat` | `gemma2:2b` (Ollama) | `200 OK` (SAGE personality context verified) |
| **OpenRouter Proxy** | `http://127.0.0.1:8001/api/openrouter/chat` | `anthropic/claude-sonnet-4` | `200 OK` (`status: success`) |
| **TypeScript & Bundle** | `npm run build` | *Vite + React* | `✓ built in 24.97s` (Zero errors) |
