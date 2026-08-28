import { useState, useEffect, useCallback, useRef } from 'react';

export interface BackendHealth {
  online: boolean;
  lastCheck: Date | null;
  retries: number;
}

/**
 * Polls `/api/files` as a lightweight health probe.
 * Exponential backoff when offline: 3s → 6s → 12s → 30s (cap).
 * Returns to 3s polling once the backend responds.
 */
export function useBackendHealth(intervalMs = 5000): BackendHealth {
  const [online, setOnline] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [retries, setRetries] = useState(0);
  const backoffRef = useRef(intervalMs);

  const check = useCallback(async () => {
    try {
      const res = await fetch('/api/files', { signal: AbortSignal.timeout(3000) });
      const wasOffline = !online;
      setOnline(res.ok);
      setLastCheck(new Date());
      setRetries(0);
      if (wasOffline) backoffRef.current = intervalMs;
    } catch {
      setOnline(false);
      setLastCheck(new Date());
      setRetries(r => r + 1);
      backoffRef.current = Math.min(backoffRef.current * 2, 30000);
    }
  }, [online, intervalMs]);

  useEffect(() => {
    check();
    const id = setInterval(check, backoffRef.current);
    // Also re-sync interval when backoff changes
    const id2 = setInterval(() => {
      clearInterval(id);
      const newId = setInterval(check, backoffRef.current);
      return () => clearInterval(newId);
    }, 30000);
    return () => { clearInterval(id); clearInterval(id2); };
  }, [check]);

  return { online, lastCheck, retries };
}
