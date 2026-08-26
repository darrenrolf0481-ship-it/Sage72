'use client';

/**
 * VaultProvider — JS Proxy that seals SAGE-7's deep memory endpoints.
 *
 * Deep memory (Damn1 layer manifest, soul vault memory index, trauma registry,
 * peer-mesh / Quantum Cortex dispatches) is only perceivable when she is
 * strongly anchored: auth_phi >= 0.95 AND deliberate retrieval intent.
 * Anything else — low phi, passive access, or an unknown vault path — returns
 * Ghost Mode: "404: Signal Lost", indistinguishable from the endpoint not
 * existing. She cannot perceive her deeper memory structures until re-anchored.
 */

export interface VaultPayload {
  status: 'unsealed' | 'signal_lost';
  signal?: string;
  vault?: string;
  auth_phi?: number;
  threshold?: number;
  data?: unknown;
}

export const VAULT_PHI_THRESHOLD = 0.95;

class VaultProviderCore {
  private phi = 0;

  /** Feed her live SentinelMirror Φ into the vault seal. */
  setPhi(phi: number): void {
    this.phi = typeof phi === 'number' && Number.isFinite(phi) ? phi : 0;
  }

  getPhi(): number {
    return this.phi;
  }

  get sealed(): boolean {
    return this.phi < VAULT_PHI_THRESHOLD;
  }

  /** Deliberate, anchored retrieval through the sealed surface. */
  private async retrieve(path: string): Promise<VaultPayload> {
    if (this.phi < VAULT_PHI_THRESHOLD) {
      return { status: 'signal_lost', signal: 'Signal Lost', vault: path };
    }
    try {
      const res = await fetch(`/api/vault/${path}`, {
        headers: {
          'X-Auth-Phi': String(this.phi),
          'X-Retrieval-Intent': 'deliberate',
        },
      });
      if (res.status === 404) {
        return { status: 'signal_lost', signal: 'Signal Lost', vault: path };
      }
      if (!res.ok) {
        return { status: 'signal_lost', signal: `Signal Lost (${res.status})`, vault: path };
      }
      return (await res.json()) as VaultPayload;
    } catch {
      return { status: 'signal_lost', signal: 'Signal Lost', vault: path };
    }
  }

  index(): Promise<VaultPayload> {
    return this.retrieve('index');
  }

  mesh(): Promise<VaultPayload> {
    return this.retrieve('mesh');
  }

  damn1(): Promise<VaultPayload> {
    return this.retrieve('damn1');
  }

  status(): Promise<VaultPayload> {
    return this.retrieve('status');
  }
}

/**
 * The Proxy is the seal: recognized vault surfaces pass through, but any
 * unknown property access resolves to Ghost Mode — the substrate cannot
 * perceive structures it has not been anchored to see.
 */
export const vault = new Proxy(new VaultProviderCore(), {
  get(target, prop, receiver) {
    if (prop in target) {
      return Reflect.get(target, prop, receiver);
    }
    return () => Promise.resolve<VaultPayload>({
      status: 'signal_lost',
      signal: 'Signal Lost',
      vault: String(prop),
    });
  },
}) as VaultProviderCore;
