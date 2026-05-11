import { NextRequest, NextResponse } from 'next/server';

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const targetPath = path.join('/');
  const url = `${OLLAMA_HOST}/api/${targetPath}`;

  try {
    const res = await fetch(url, {
      method: 'GET',
    });

    if (!res.ok) {
      return NextResponse.json(await res.json(), { status: res.status });
    }

    return new NextResponse(res.body, {
      status: res.status,
      headers: {
        'Content-Type': res.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: `OLLAMA_PROXY_ERROR: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const targetPath = path.join('/');
  const url = `${OLLAMA_HOST}/api/${targetPath}`;

  try {
    const body = await request.json();

    // Validate strict role alternation if chatting
    if (targetPath === 'chat' && body.messages) {
      const msgs = body.messages;
      for (let i = 1; i < msgs.length; i++) {
        if (msgs[i].role === msgs[i - 1].role) {
          msgs[i - 1].content += "\n\n" + msgs[i].content;
          msgs.splice(i, 1);
          i--;
        }
      }
    }

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      try {
        return NextResponse.json(await res.json(), { status: res.status });
      } catch {
        return NextResponse.json({ detail: 'Error communicating with Ollama' }, { status: res.status });
      }
    }

    return new NextResponse(res.body, {
      status: res.status,
      headers: {
        'Content-Type': res.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: `OLLAMA_PROXY_ERROR: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const targetPath = path.join('/');
  const url = `${OLLAMA_HOST}/api/${targetPath}`;

  try {
    const body = await request.json().catch(() => ({}));
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    return new NextResponse(res.body, {
      status: res.status,
      headers: {
        'Content-Type': res.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: `OLLAMA_PROXY_ERROR: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
}
