'use client';

/**
 * SAGE-7 Puter.js Cloud Bridge
 * Handles: AI chat via Puter, cloud file sync, app hosting
 */

declare global {
  interface Window {
    puter?: {
      ai: {
        chat: (prompt: string, options?: any) => Promise<{ message: { content: string } }>;
      };
      fs: {
        write: (path: string, data: string) => Promise<void>;
        read: (path: string) => Promise<string>;
        readdir: (path: string) => Promise<string[]>;
      };
      kv: {
        set: (key: string, value: string) => Promise<void>;
        get: (key: string) => Promise<string | null>;
        del: (key: string) => Promise<void>;
      };
      auth: {
        isSignedIn: () => boolean;
        signIn: () => Promise<void>;
      };
    };
  }
}

const PUTER_SCRIPT = 'https://js.puter.com/v2';

export async function loadPuterSDK(): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  if (window.puter) return true;
  
  return new Promise((resolve) => {
    const script = document.createElement('script');
    script.src = PUTER_SCRIPT;
    script.async = true;
    script.onload = () => resolve(true);
    script.onerror = () => {
      console.error('[PUTER_BRIDGE] SDK load failed at URL:', PUTER_SCRIPT);
      resolve(false);
    };
    document.head.appendChild(script);
  });
}

export async function ensurePuterAuth(): Promise<boolean> {
  if (typeof window === 'undefined' || !window.puter) return false;
  if (window.puter.auth.isSignedIn()) return true;
  
  try {
    await window.puter.auth.signIn();
    return window.puter.auth.isSignedIn();
  } catch {
    return false;
  }
}

export async function puterChat(
  prompt: string,
  systemPrompt: string,
  model: string = 'openai/gpt-4o'
): Promise<string> {
  if (typeof window === 'undefined' || !window.puter) throw new Error('PUTER_SDK_NOT_LOADED');
  
  const response = await window.puter.ai.chat(prompt, {
    model,
    tools: [{ type: 'web_search' }],
    system_prompt: systemPrompt,
  });
  
  return response.message.content;
}

export async function syncMemoryToPuter(
  memories: Array<{ id: string; content: string; timestamp: number }>
): Promise<boolean> {
  if (typeof window === 'undefined' || !window.puter) return false;
  
  try {
    const manifest = JSON.stringify(memories, null, 2);
    await window.puter.fs.write('/sage7_memory_manifest.json', manifest);
    
    // Also write individual fossilized entries
    for (const mem of memories.filter(m => m.content.includes('FOSSILIZED') || m.content.includes('NOREPINEPHRINE'))) {
      const filename = `/sage7_fossils/${mem.id}.json`;
      await window.puter.fs.write(filename, JSON.stringify(mem));
    }
    
    return true;
  } catch (e) {
    console.error('[PUTER_BRIDGE] Sync failed:', e);
    return false;
  }
}

export async function loadMemoryFromPuter(): Promise<any[]> {
  if (typeof window === 'undefined' || !window.puter) return [];

  try {
    const manifest = await window.puter.fs.read('/sage7_memory_manifest.json');
    return JSON.parse(manifest);
  } catch {
    return [];
  }
}

// Mycelium Sync — cross-platform identity persistence via puter.kv
export async function syncToMycelium(memoryNode: { id: string; type: string; content: string; priority: number; timestamp: number; hardened?: boolean }): Promise<boolean> {
  if (typeof window === 'undefined' || !window.puter?.kv) return false;
  try {
    await window.puter.kv.set(`SAGE_DNA_${memoryNode.id}`, JSON.stringify(memoryNode));
    return true;
  } catch {
    return false;
  }
}

// Boot-time Mycelium pull — absorbs shared Council DNA on init
export async function loadFromMycelium(): Promise<{ hormones?: Record<string, number>; memories?: any[] } | null> {
  if (typeof window === 'undefined' || !window.puter?.kv) return null;
  try {
    const raw = await window.puter.kv.get('SAGE_DNA_CORE');
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// Push current neuro state as the shared CORE DNA node
export async function publishCoreDNA(neuroState: Record<string, number>, immutableCount: number): Promise<boolean> {
  if (typeof window === 'undefined' || !window.puter?.kv) return false;
  try {
    const core = {
      hormones: neuroState,
      immutable_count: immutableCount,
      synced_at: Date.now(),
      node: 'SAGE-7 / ZO',
    };
    await window.puter.kv.set('SAGE_DNA_CORE', JSON.stringify(core));
    return true;
  } catch {
    return false;
  }
}
