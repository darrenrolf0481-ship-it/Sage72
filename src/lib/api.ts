'use client';

export async function generateResponse(
  provider: string,
  model: string,
  prompt: string,
  _settings: any,
  systemPrompt?: string
) {
  if (provider === 'google') {
    const { GoogleGenerativeAI } = await import("@google/generative-ai");
    const ai = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GEMINI_API_KEY || "");
    const modelInstance = ai.getGenerativeModel({
      model: model || 'gemini-3-flash-preview',
      ...(systemPrompt ? { systemInstruction: systemPrompt } : {}),
    });
    const result = await modelInstance.generateContent({
      contents: [{ role: 'user', parts: [{ text: prompt }] }]
    });
    const response = await result.response;
    return response.text() || "";
  }

  return `[${provider.toUpperCase()} SIMULATION] I processed your request: "${prompt.substring(0, 30)}..."`;
}
