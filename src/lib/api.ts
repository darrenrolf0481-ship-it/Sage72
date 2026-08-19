'use client';

export async function generateResponse(
  provider: string,
  model: string,
  prompt: string,
  _settings: any,
  systemPrompt?: string,
  history?: { role: string; content: string }[]
) {
  if (provider === 'openrouter') {
    const key = _settings?.apiKey || (typeof window !== 'undefined' ? localStorage.getItem('openrouter_api_key') : '') || '';
    let targetModel = (model || '').trim();
    if (!targetModel || !targetModel.includes('/') || targetModel.includes('JOSIEFIED')) {
      targetModel = 'anthropic/claude-sonnet-4';
    }

    const formattedMessages = [
      ...(systemPrompt ? [{ role: "system", content: systemPrompt }] : []),
      ...(history && history.length > 0 ? history : []),
      { role: "user", content: prompt }
    ];

    // 1. Try local backend proxy first (has access to server .env.local and handles CORS)
    try {
      const proxyRes = await fetch("/api/openrouter/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          apiKey: key,
          model: targetModel,
          messages: formattedMessages,
          systemPrompt: systemPrompt || "",
          prompt: prompt
        })
      });

      if (proxyRes.ok) {
        const proxyData = await proxyRes.json();
        if (proxyData.status === 'success' && proxyData.reply) {
          return proxyData.reply;
        }
        if (proxyData.status === 'error') {
          throw new Error(proxyData.reply || proxyData.message || "OpenRouter error from substrate backend.");
        }
      }
    } catch (proxyErr: any) {
      // If client has no direct key, rethrow the proxy error
      if (!key || !key.trim() || key === 'your_openrouter_api_key_here') {
        throw new Error(proxyErr.message || "OpenRouter request failed. Ensure OPENROUTER_API_KEY is configured in Config or .env.local");
      }
    }

    // 2. Direct browser fetch fallback (if key is explicitly present in client)
    const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${key.trim()}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8001",
        "X-Title": "SAGE-7"
      },
      body: JSON.stringify({
        model: targetModel,
        messages: formattedMessages
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.error?.message || `OpenRouter HTTP ${res.status}`);
    }

    const data = await res.json();
    const choices = data.choices || [];
    if (!choices.length) {
      throw new Error("OpenRouter returned empty choices array.");
    }

    const msg = choices[0]?.message;
    let reply = msg?.content || msg?.reasoning || msg?.reasoning_content || choices[0]?.text;
    if (Array.isArray(reply)) {
      reply = reply.map((p: any) => p?.text || '').filter(Boolean).join('\n');
    }

    if (!reply || !String(reply).trim()) {
      return "No content returned from OpenRouter model.";
    }

    return String(reply);
  }

  if (provider === 'google') {
    try {
      const { GoogleGenerativeAI } = await import('@google/genai' as any).catch(() => import('@google/generative-ai' as any));
      const geminiKey = _settings?.apiKey || (typeof window !== 'undefined' ? localStorage.getItem('gemini_api_key') : '') || '';
      const genAI = new GoogleGenerativeAI(geminiKey);
      const geminiModel = genAI.getGenerativeModel({ model: model || "gemini-2.0-flash" });
      const contents = [
        ...(history && history.length > 0
          ? history.map(h => ({
              role: h.role === 'assistant' ? 'model' : 'user',
              parts: [{ text: h.content }]
            }))
          : []),
        { role: 'user', parts: [{ text: prompt }] }
      ];
      const result = await geminiModel.generateContent({
        contents,
        systemInstruction: systemPrompt ? { role: 'system', parts: [{ text: systemPrompt }] } : undefined
      });
      return result.response.text() || "No response from Gemini.";
    } catch (e: any) {
      throw new Error(`Gemini error: ${e.message}`);
    }
  }

  return `[${provider.toUpperCase()} SIMULATION] I processed your request: "${prompt.substring(0, 30)}..."`;
}
