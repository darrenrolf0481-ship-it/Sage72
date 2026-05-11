import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const apiKey = process.env.GEMINI_API_KEY || body.api_key;
    const model = body.model || 'gemini-2.0-flash';
    
    if (!apiKey) {
        // Fallback or error
        return NextResponse.json({ error: 'GEMINI_API_KEY missing.' }, { status: 400 });
    }

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    const payload = {
      contents: [{ role: 'user', parts: [{ text: body.message || '' }] }],
      systemInstruction: { parts: [{ text: body.system_prompt || '' }] }
    };

    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
    
    return NextResponse.json({ reply, status: 'success' });
  } catch (error) {
    return NextResponse.json({ error: `GEMINI_PROXY_ERROR: ${String(error)}` }, { status: 502 });
  }
}
