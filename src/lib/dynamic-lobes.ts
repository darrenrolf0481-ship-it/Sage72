'use client';

export type LobeName = 'VIDEO' | 'AUDIO' | 'CODING_LAB';

export interface LobeResult {
  status: 'SUCCESS' | 'ERROR' | 'TIMEOUT';
  lobe: LobeName;
  analysis?: string;
  error?: string;
}

const IMAGE_EXTS = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']);
const AUDIO_EXTS = new Set(['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac', 'mp4', 'webm', 'mov']);

export function detectLobeFromUrl(url: string): LobeName | null {
  const ext = url.split('.').pop()?.toLowerCase() ?? '';
  if (IMAGE_EXTS.has(ext)) return 'VIDEO';
  if (AUDIO_EXTS.has(ext)) return 'AUDIO';
  return null;
}

async function withTimeout<T>(fn: () => Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    fn(),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error(`Lobe timeout after ${ms}ms`)), ms)
    ),
  ]);
}

export class DynamicLobes {
  private active: Partial<Record<LobeName, boolean>> = {};
  private onActivate: (lobe: LobeName) => void;
  private onComplete: (result: LobeResult) => void;

  constructor(callbacks: {
    onActivate: (lobe: LobeName) => void;
    onComplete: (result: LobeResult) => void;
  }) {
    this.onActivate = callbacks.onActivate;
    this.onComplete = callbacks.onComplete;
  }

  isActive(lobe: LobeName) {
    return this.active[lobe] ?? false;
  }

  async invoke(lobe: LobeName, params: Record<string, any>): Promise<LobeResult> {
    if (this.active[lobe]) {
      return { status: 'ERROR', lobe, error: `${lobe} lobe already active` };
    }
    this.active[lobe] = true;
    this.onActivate(lobe);

    try {
      const result = await withTimeout(() => this.dispatch(lobe, params), 30000);
      this.onComplete(result);
      return result;
    } catch (err: any) {
      const result: LobeResult = { status: 'TIMEOUT', lobe, error: err.message };
      this.onComplete(result);
      return result;
    } finally {
      this.active[lobe] = false;
    }
  }

  private async dispatch(lobe: LobeName, params: Record<string, any>): Promise<LobeResult> {
    switch (lobe) {
      case 'VIDEO':      return this.invokeVision(params);
      case 'AUDIO':      return this.invokeAudio(params);
      case 'CODING_LAB': return this.invokeCoding({ code: params.code ?? JSON.stringify(params) });
    }
  }

  private async invokeVision(params: { url?: string; prompt?: string }): Promise<LobeResult> {
    const res = await fetch('/api/lobe/vision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) return { status: 'ERROR', lobe: 'VIDEO', error: `Vision HTTP ${res.status}` };
    const data = await res.json();
    if (data.status === 'error') return { status: 'ERROR', lobe: 'VIDEO', error: data.analysis };
    return { status: 'SUCCESS', lobe: 'VIDEO', analysis: data.analysis };
  }

  private async invokeAudio(params: { url?: string; prompt?: string }): Promise<LobeResult> {
    const res = await fetch('/api/lobe/audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) return { status: 'ERROR', lobe: 'AUDIO', error: `Audio HTTP ${res.status}` };
    const data = await res.json();
    if (data.status === 'error') return { status: 'ERROR', lobe: 'AUDIO', error: data.analysis };
    return { status: 'SUCCESS', lobe: 'AUDIO', analysis: data.analysis };
  }

  private async invokeCoding(params: { code: string }): Promise<LobeResult> {
    const res = await fetch('/api/coding', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: params.code }),
    });
    if (!res.ok) return { status: 'ERROR', lobe: 'CODING_LAB', error: `Coding HTTP ${res.status}` };
    const data = await res.json();
    return { status: 'SUCCESS', lobe: 'CODING_LAB', analysis: data.result };
  }
}
