import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const apiKey = body.api_key;
    const voiceId = body.voice_id || 'y3H6zY6KvCH2pEuQjmv8';
    const text = body.text || '';

    if (!apiKey) {
      return NextResponse.json({ error: 'ElevenLabs API key required' }, { status: 400 });
    }

    const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}/stream`, {
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        model_id: 'eleven_turbo_v2',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
        },
      }),
    });

    if (!res.ok) {
        return NextResponse.json({ error: await res.text() }, { status: res.status });
    }

    return new NextResponse(res.body, {
      status: 200,
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': 'inline; filename=sage_tts.mp3',
      },
    });
  } catch (error) {
    return NextResponse.json({ error: `TTS_PROXY_ERROR: ${String(error)}` }, { status: 502 });
  }
}
