/**
 * Wraps fetch() with retry logic and exponential backoff.
 * Returns null on exhausted retries so callers can degrade gracefully.
 */
export async function fetchWithRetry(
  url: string,
  init?: RequestInit,
  { retries = 2, baseDelay = 800 } = {}
): Promise<Response | null> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, init);
      return res;
    } catch (err) {
      if (attempt === retries) {
        console.warn(`[fetchWithRetry] ${url} failed after ${retries + 1} attempts:`, err);
        return null;
      }
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise(r => setTimeout(r, delay));
    }
  }
  return null;
}
