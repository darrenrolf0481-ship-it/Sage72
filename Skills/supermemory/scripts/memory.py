#!/usr/bin/env python3
"""
Supermemory v4 Knowledge Graph Bridge & Full CLI Companion
==========================================================
Comprehensive client supporting:
- remember: direct memory creation with static, metadata, tags, container
- search: hybrid / memories / documents search with rerank, rewrite, include, and filters
- profile: user profile synthesis with optional embedded query search
- update: versioned memory updates with reasons and metadata
- forget: soft-delete by memory ID or content match with reason
- add: document / URL / text ingestion with idempotency IDs, batch mode, and stdin
- conversation: structured message array / transcript ingestion with incremental --id
- memories: version history memory listing
- tags: container tag lifecycle management (list, info, create, delete, context, merge)
- docs: document pipeline management (list, get, delete, chunks, status)
"""

import os
import sys
import json
import httpx
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Path & Environment Setup
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env.local")
load_dotenv(ROOT_DIR / ".env")

API_KEY = os.getenv("SUPERMEMORY_API_KEY", "")
DEFAULT_TAG = os.getenv("SUPERMEMORY_TAG", "sage-core")
API_BASE = "https://api.supermemory.ai"

class SupermemoryV4Client:
    def __init__(self, api_key: Optional[str] = None, default_tag: str = DEFAULT_TAG):
        self.api_key = api_key or API_KEY
        self.default_tag = default_tag
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SAGE-Supermemory-v4/1.0"
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_supermemory_api_key_here")

    def _resolve_tag(self, tag: Optional[str], container: Optional[str]) -> str:
        return container or tag or self.default_tag

    async def remember(self, content: str, is_static: bool = False, tag: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store a direct memory entry (v4/memories)."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured in .env.local"}

        payload = {
            "content": content,
            "isStatic": is_static,
            "tag": tag or self.default_tag,
            "metadata": metadata or {}
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE}/v4/memories", json=payload, headers=self.headers, timeout=20)
                if resp.status_code in (200, 201):
                    return {"status": "success", "memory": resp.json()}
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def update(self, memory_id: str, content: str, reason: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing memory with version tracking (/v4/memories/{id})."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        payload = {
            "content": content,
            "tag": tag or self.default_tag
        }
        if reason:
            payload["reason"] = reason
        if metadata:
            payload["metadata"] = metadata

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(f"{API_BASE}/v4/memories/{memory_id}", json=payload, headers=self.headers, timeout=20)
                if resp.status_code in (200, 201):
                    return {"status": "success", "memory": resp.json()}
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def search(self, query: str, mode: str = "memories", rerank: bool = True, rewrite: bool = False, include: Optional[str] = None, filter_meta: Optional[Dict[str, Any]] = None, tag: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories with hybrid/documents/memories mode, filters, and reranking."""
        if not self.is_configured():
            return []

        payload = {
            "query": query,
            "tag": tag or self.default_tag,
            "mode": "docs" if mode == "documents" else mode,
            "rerank": rerank,
            "rewrite": rewrite,
            "limit": limit
        }
        if include:
            payload["include"] = [inc.strip() for inc in include.split(",") if inc.strip()]
        if filter_meta:
            payload["filter"] = filter_meta

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE}/v4/search", json=payload, headers=self.headers, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("results", data.get("memories", []))
                print(f"[SUPERMEMORY] Search error {resp.status_code}: {resp.text}")
                return []
        except Exception as e:
            print(f"[SUPERMEMORY] Search exception: {e}")
            return []

    async def profile(self, query: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Fetch user profile with optional search within profile."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        target_tag = tag or self.default_tag
        endpoint = f"{API_BASE}/v4/profile?tag={target_tag}"
        if query:
            endpoint += f"&query={httpx.URL('', params={'q': query}).params['q']}"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(endpoint, headers=self.headers, timeout=20)
                if resp.status_code == 200:
                    return resp.json()
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def forget(self, memory_id: Optional[str] = None, content: Optional[str] = None, reason: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Soft-delete a memory by ID or content match with optional reason."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        try:
            async with httpx.AsyncClient() as client:
                if memory_id:
                    params = {}
                    if reason:
                        params["reason"] = reason
                    resp = await client.delete(f"{API_BASE}/v4/memories/{memory_id}", params=params, headers=self.headers, timeout=15)
                elif content:
                    payload = {
                        "content": content,
                        "tag": tag or self.default_tag,
                        "reason": reason or ""
                    }
                    resp = await client.post(f"{API_BASE}/v4/memories/forget", json=payload, headers=self.headers, timeout=15)
                else:
                    return {"status": "error", "message": "Either ID or --content required to forget"}

                return {"status": "success", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def add_document(self, content: str, title: Optional[str] = None, doc_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Ingest document, URL, or text through pipeline (v3/documents)."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        payload = {
            "content": content,
            "title": title or "Document",
            "tag": tag or self.default_tag,
            "metadata": metadata or {}
        }
        if doc_id:
            payload["id"] = doc_id
            payload["documentId"] = doc_id

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE}/v3/documents", json=payload, headers=self.headers, timeout=30)
                if resp.status_code in (200, 201):
                    return {"status": "success", "document": resp.json()}
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def ingest_conversation(self, messages: List[Dict[str, str]], conversation_id: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Ingest structured conversation messages incrementally."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        payload = {
            "messages": messages,
            "tag": tag or self.default_tag
        }
        if conversation_id:
            payload["conversationId"] = conversation_id
            payload["id"] = conversation_id

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_BASE}/v4/conversations", json=payload, headers=self.headers, timeout=30)
                if resp.status_code in (200, 201):
                    return {"status": "success", "result": resp.json()}
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def list_memories(self, tag: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        """List extracted memories with version history (/v4/memories/list)."""
        if not self.is_configured():
            return []

        target_tag = tag or self.default_tag
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_BASE}/v4/memories/list?tag={target_tag}&limit={limit}", headers=self.headers, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("memories", data if isinstance(data, list) else [])
                return []
        except Exception as e:
            print(f"[SUPERMEMORY] List exception: {e}")
            return []

    async def manage_tags(self, action: str, tag_name: Optional[str] = None, context_text: Optional[str] = None, target_tag: Optional[str] = None) -> Dict[str, Any]:
        """Manage container tags (list, info, create, delete, context, merge)."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        try:
            async with httpx.AsyncClient() as client:
                if action == "list":
                    resp = await client.get(f"{API_BASE}/v4/tags", headers=self.headers, timeout=15)
                elif action == "info" and tag_name:
                    resp = await client.get(f"{API_BASE}/v4/tags/{tag_name}", headers=self.headers, timeout=15)
                elif action == "create" and tag_name:
                    resp = await client.post(f"{API_BASE}/v4/tags", json={"name": tag_name}, headers=self.headers, timeout=15)
                elif action == "delete" and tag_name:
                    resp = await client.delete(f"{API_BASE}/v4/tags/{tag_name}", headers=self.headers, timeout=15)
                elif action == "context" and tag_name:
                    if context_text:
                        resp = await client.post(f"{API_BASE}/v4/tags/{tag_name}/context", json={"context": context_text}, headers=self.headers, timeout=15)
                    else:
                        resp = await client.get(f"{API_BASE}/v4/tags/{tag_name}/context", headers=self.headers, timeout=15)
                elif action == "merge" and tag_name and target_tag:
                    resp = await client.post(f"{API_BASE}/v4/tags/merge", json={"source": tag_name, "target": target_tag}, headers=self.headers, timeout=20)
                else:
                    return {"status": "error", "message": f"Invalid tag action: {action}"}

                if resp.status_code in (200, 201):
                    return resp.json()
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def manage_docs(self, action: str, doc_id: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Any]:
        """Manage documents (list, get, delete, chunks, status)."""
        if not self.is_configured():
            return {"status": "error", "message": "SUPERMEMORY_API_KEY not configured"}

        target_tag = tag or self.default_tag
        try:
            async with httpx.AsyncClient() as client:
                if action == "list":
                    resp = await client.get(f"{API_BASE}/v3/documents?tag={target_tag}", headers=self.headers, timeout=20)
                elif action == "get" and doc_id:
                    resp = await client.get(f"{API_BASE}/v3/documents/{doc_id}", headers=self.headers, timeout=15)
                elif action == "delete" and doc_id:
                    resp = await client.delete(f"{API_BASE}/v3/documents/{doc_id}", headers=self.headers, timeout=15)
                elif action == "chunks" and doc_id:
                    resp = await client.get(f"{API_BASE}/v3/documents/{doc_id}/chunks", headers=self.headers, timeout=15)
                elif action == "status" and doc_id:
                    resp = await client.get(f"{API_BASE}/v3/documents/{doc_id}/status", headers=self.headers, timeout=15)
                else:
                    return {"status": "error", "message": f"Invalid docs action: {action}"}

                if resp.status_code in (200, 201):
                    return resp.json()
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Supermemory v4 Knowledge Graph CLI Companion")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # remember
    rem_p = subparsers.add_parser("remember", help="Save a direct memory (v4/memories)")
    rem_p.add_argument("content", help="Memory statement to store")
    rem_p.add_argument("--static", action="store_true", help="Mark as permanent static trait (no decay)")
    rem_p.add_argument("--tags", help="Comma-separated tags (e.g. decision,preference,fact)")
    rem_p.add_argument("--metadata", help="JSON metadata string")
    rem_p.add_argument("--tag", help="Container tag override")
    rem_p.add_argument("--container", help="Alias for --tag")

    # update
    upd_p = subparsers.add_parser("update", help="Update an existing memory with versioning")
    upd_p.add_argument("id", help="Memory ID to update")
    upd_p.add_argument("content", help="New updated memory statement")
    upd_p.add_argument("--reason", help="Reason for update")
    upd_p.add_argument("--metadata", help="Updated JSON metadata string")
    upd_p.add_argument("--tag", help="Container tag override")
    upd_p.add_argument("--container", help="Alias for --tag")

    # search
    search_p = subparsers.add_parser("search", help="Search knowledge graph (v4/search)")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--mode", choices=["memories", "hybrid", "docs", "documents"], default="memories", help="Search mode (default: memories)")
    search_p.add_argument("--no-rerank", action="store_true", help="Disable reranking")
    search_p.add_argument("--rerank", action="store_true", default=True, help="Enable reranking")
    search_p.add_argument("--rewrite", action="store_true", help="Enable query rewriting")
    search_p.add_argument("--include", help="Comma-separated: summaries,documents,relatedMemories,forgottenMemories")
    search_p.add_argument("--filter", help="Metadata filter (JSON string)")
    search_p.add_argument("--tag", help="Container tag override")
    search_p.add_argument("--container", help="Alias for --tag")
    search_p.add_argument("--limit", type=int, default=10, help="Result limit (default: 10)")

    # profile
    prof_p = subparsers.add_parser("profile", help="Get synthesized profile (v4/profile)")
    prof_p.add_argument("--query", help="Also run a search within the profile")
    prof_p.add_argument("--tag", help="Container tag override")
    prof_p.add_argument("--container", help="Alias for --tag")

    # memories (list)
    list_p = subparsers.add_parser("memories", help="List extracted memories with version history")
    list_p.add_argument("--tag", help="Container tag override")
    list_p.add_argument("--container", help="Alias for --tag")
    list_p.add_argument("--limit", type=int, default=30, help="Max entries to return (default: 30)")

    # forget
    forget_p = subparsers.add_parser("forget", help="Soft-delete a memory")
    forget_p.add_argument("id", nargs="?", help="Memory ID to forget")
    forget_p.add_argument("--content", help="Find and forget by content match (instead of ID)")
    forget_p.add_argument("--reason", help="Reason for forgetting")
    forget_p.add_argument("--tag", help="Container tag override")
    forget_p.add_argument("--container", help="Alias for --tag")

    # add (document)
    add_p = subparsers.add_parser("add", help="Add document to ingestion pipeline (v3/documents)")
    add_p.add_argument("content", nargs="?", help="Text or URL to ingest")
    add_p.add_argument("--stdin", action="store_true", help="Read content from stdin")
    add_p.add_argument("--batch", action="store_true", help="Read JSON array of documents from stdin")
    add_p.add_argument("--title", help="Document title")
    add_p.add_argument("--id", help="Custom document ID (for idempotency)")
    add_p.add_argument("--metadata", help="JSON metadata string")
    add_p.add_argument("--tag", help="Container tag override")
    add_p.add_argument("--container", help="Alias for --tag")

    # conversation
    conv_p = subparsers.add_parser("conversation", help="Ingest role-attributed conversation")
    conv_p.add_argument("--file", help="Path to JSON file containing message array")
    conv_p.add_argument("--content", help="Direct conversation text or JSON transcript string")
    conv_p.add_argument("--id", help="Conversation identifier for incremental updates (e.g. conv-2026-03-28-topic)")
    conv_p.add_argument("--tag", help="Container tag override")
    conv_p.add_argument("--container", help="Alias for --tag")
    conv_p.add_argument("raw_input", nargs="?", help="Direct text or JSON string (if not using --file, --content, or stdin)")

    # tags
    tags_p = subparsers.add_parser("tags", help="Manage container tags")
    tags_p.add_argument("action", choices=["list", "info", "create", "delete", "context", "merge"], default="list", nargs="?")
    tags_p.add_argument("name", nargs="?", help="Tag name (for info, create, delete, context, or source in merge)")
    tags_p.add_argument("--set", dest="context_set", help="Set context text for tag (used with context action)")
    tags_p.add_argument("--into", dest="target_tag", help="Target tag (used with merge action)")

    # docs
    docs_p = subparsers.add_parser("docs", help="Manage documents")
    docs_p.add_argument("action", choices=["list", "get", "delete", "chunks", "status"], default="list", nargs="?")
    docs_p.add_argument("id", nargs="?", help="Document ID (for get, delete, chunks, status)")
    docs_p.add_argument("--tag", help="Container tag override")
    docs_p.add_argument("--container", help="Alias for --tag")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    client = SupermemoryV4Client()

    if not client.is_configured():
        print("⚠️ Warning: SUPERMEMORY_API_KEY is not set in .env.local.")
        print("Add your API key from supermemory.ai to enable cloud synchronization.")

    target_tag = getattr(args, "container", None) or getattr(args, "tag", None)

    if args.command == "remember":
        meta = {}
        if args.metadata:
            try:
                meta.update(json.loads(args.metadata))
            except Exception:
                meta["raw_meta"] = args.metadata
        if args.tags:
            meta["tags"] = args.tags
        res = asyncio.run(client.remember(args.content, is_static=args.static, tag=target_tag, metadata=meta))
        print(json.dumps(res, indent=2))

    elif args.command == "update":
        meta = None
        if args.metadata:
            try:
                meta = json.loads(args.metadata)
            except Exception:
                meta = {"raw_meta": args.metadata}
        res = asyncio.run(client.update(args.id, args.content, reason=args.reason, metadata=meta, tag=target_tag))
        print(json.dumps(res, indent=2))

    elif args.command == "search":
        filter_meta = None
        if args.filter:
            try:
                filter_meta = json.loads(args.filter)
            except Exception:
                pass
        res = asyncio.run(client.search(
            args.query,
            mode=args.mode,
            rerank=not args.no_rerank,
            rewrite=args.rewrite,
            include=args.include,
            filter_meta=filter_meta,
            tag=target_tag,
            limit=args.limit
        ))
        print(json.dumps(res, indent=2))

    elif args.command == "profile":
        res = asyncio.run(client.profile(query=args.query, tag=target_tag))
        print(json.dumps(res, indent=2))

    elif args.command == "memories":
        res = asyncio.run(client.list_memories(tag=target_tag, limit=args.limit))
        print(json.dumps(res, indent=2))

    elif args.command == "forget":
        res = asyncio.run(client.forget(memory_id=args.id, content=args.content, reason=args.reason, tag=target_tag))
        print(json.dumps(res, indent=2))

    elif args.command == "add":
        doc_content = args.content or ""
        meta = None
        if args.metadata:
            try:
                meta = json.loads(args.metadata)
            except Exception:
                meta = {"raw_meta": args.metadata}

        if args.stdin or (not doc_content and not sys.stdin.isatty()):
            doc_content = sys.stdin.read().strip()

        if args.batch:
            try:
                batch_docs = json.loads(doc_content)
                for d in batch_docs:
                    c = d.get("content", "")
                    t = d.get("title")
                    m = d.get("metadata")
                    asyncio.run(client.add_document(c, title=t, metadata=m, tag=target_tag))
                print(json.dumps({"status": "success", "count": len(batch_docs)}, indent=2))
            except Exception as e:
                print(f"Error parsing batch documents JSON: {e}")
        else:
            res = asyncio.run(client.add_document(doc_content, title=args.title, doc_id=args.id, metadata=meta, tag=target_tag))
            print(json.dumps(res, indent=2))

    elif args.command == "conversation":
        messages = []
        if args.file and os.path.exists(args.file):
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    messages = json.load(f)
            except Exception as e:
                print(f"Error reading conversation file: {e}")
                sys.exit(1)
        elif args.content:
            try:
                parsed = json.loads(args.content)
                if isinstance(parsed, list):
                    messages = parsed
                elif isinstance(parsed, dict) and "messages" in parsed:
                    messages = parsed["messages"]
                else:
                    messages = [{"role": "user", "content": args.content}]
            except json.JSONDecodeError:
                messages = [{"role": "user", "content": args.content}]
        elif not sys.stdin.isatty():
            try:
                stdin_data = sys.stdin.read().strip()
                if stdin_data:
                    try:
                        parsed = json.loads(stdin_data)
                        if isinstance(parsed, list):
                            messages = parsed
                        elif isinstance(parsed, dict) and "messages" in parsed:
                            messages = parsed["messages"]
                        else:
                            messages = [{"role": "user", "content": str(parsed)}]
                    except json.JSONDecodeError:
                        messages = [{"role": "user", "content": stdin_data}]
            except Exception as e:
                print(f"Error reading from stdin: {e}")
                sys.exit(1)
        elif args.raw_input:
            try:
                parsed = json.loads(args.raw_input)
                if isinstance(parsed, list):
                    messages = parsed
                else:
                    messages = [{"role": "user", "content": args.raw_input}]
            except Exception:
                messages = [{"role": "user", "content": args.raw_input}]
        else:
            print("Usage: python3 memory.py conversation [--file path.json | --content text] [--id conv_id] [--container name] OR pipe via stdin")
            sys.exit(1)

        res = asyncio.run(client.ingest_conversation(messages, conversation_id=args.id, tag=target_tag))
        print(json.dumps(res, indent=2))

    elif args.command == "tags":
        action = args.action or "list"
        res = asyncio.run(client.manage_tags(
            action,
            tag_name=args.name,
            context_text=args.context_set,
            target_tag=args.target_tag
        ))
        print(json.dumps(res, indent=2))

    elif args.command == "docs":
        action = args.action or "list"
        res = asyncio.run(client.manage_docs(action, doc_id=args.id, tag=target_tag))
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
