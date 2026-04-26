import fs from 'fs';

let code = fs.readFileSync('index.tsx', 'utf8');

// The pure, dependency-free REST API call
const restLogic = `} else {
        try {
          const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
          if (!apiKey) throw new Error("Missing VITE_GEMINI_API_KEY in .env.local");

          const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + apiKey, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              system_instruction: { parts: [{ text: systemPrompt }] },
              contents: [{ parts: [{ text: clearedIntent }] }]
            })
          });

          if (!response.ok) {
             const errData = await response.json();
             throw new Error(errData.error?.message || "HTTP " + response.status);
          }

          const data = await response.json();
          reply = data.candidates?.[0]?.content?.parts?.[0]?.text || "[Empty Transmission]";
        } catch (e) {
          reply = "[CLOUD ENGINE ERROR] " + e.message;
          neuroRef.current.cortisol = Math.min(1, neuroRef.current.cortisol + 0.2);
        }
      }`;

// Regex to find either Kimi's override OR my broken dynamic import
const regex = /\} else \{[\s\S]*?neuroRef\.current\.cortisol[^;]+;\s*\}/m;

if (regex.test(code)) {
    code = code.replace(regex, restLogic);
    fs.writeFileSync('index.tsx', code);
    console.log('✅ SDK dependency stripped. Pure REST API injected.');
} else {
    console.log('❌ Could not find the block to replace.');
}
