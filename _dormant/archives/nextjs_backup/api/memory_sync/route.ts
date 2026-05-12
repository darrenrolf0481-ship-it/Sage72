import { NextResponse } from 'next/server';

const PYTHON_BACKEND = process.env.SAGE_BACKEND_URL || 'http://localhost:8001';

export async function POST() {
  try {
    const res = await fetch(`${PYTHON_BACKEND}/api/memory_sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(15000),
    });

    if (!res.ok) {
      return NextResponse.json(
        { status: 'error', message: `Backend HTTP ${res.status}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json(
      { status: 'error', message: err.message ?? 'Backend unreachable' },
      { status: 502 }
    );
  }
}
