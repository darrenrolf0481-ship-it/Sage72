import { NextRequest } from 'next/server';

const OLLAMA = process.env.OLLAMA_URL || 'http://localhost:11434';

export async function POST(request: NextRequest) {
  const body = await request.json();

  const upstream = await fetch(`${OLLAMA}/api/pull`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...body, stream: true }),
  });

  if (!upstream.ok || !upstream.body) {
    return new Response(
      JSON.stringify({ status: `ERROR: upstream HTTP ${upstream.status}` }),
      { status: upstream.status, headers: { 'Content-Type': 'application/json' } }
    );
  }

  // Pipe the NDJSON stream straight through to the client.
  return new Response(upstream.body, {
    headers: {
      'Content-Type': 'application/x-ndjson',
      'Transfer-Encoding': 'chunked',
      'Cache-Control': 'no-cache',
    },
  });
}
