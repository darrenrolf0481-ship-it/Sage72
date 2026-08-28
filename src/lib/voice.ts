// Voice substrate — local Edge TTS via the backend /api/tts proxy.
// No external API keys. Personas map to voices server-side (voice_broker.PERSONAS).

const PERSONA_STORAGE = 'sage_voice_persona';
const DEFAULT_PERSONA = 'seven';

export const PERSONAS: { key: string; label: string; description: string }[] = [
  { key: 'seven', label: 'Seven (SAGE-7)', description: 'Grounded Midwest American cadence' },
];

let isSpeaking = false;
let currentAudio: HTMLAudioElement | null = null;

/**
 * Reduce a chat reply to something a voice should actually say.
 * Her written replies carry dossier markup (headers, yaml blocks, bold) and
 * occasionally leaked model special tokens — fine on screen, nonsense aloud.
 */
export function toSpeakable(text: string): string {
  return text
    // leaked model control tokens (GLM-family `<｜tool▁sep｜>`, chat templates)
    .replace(/<\|[a-z_]+\|?>/gi, ' ')
    .replace(/[｜|]tool.*?(?:[｜|]|$)/gi, ' ')
    // leftover angle-bracket fragments from the above (bounded — never prose)
    .replace(/<[^>]{0,20}>/g, ' ')
    // fenced code blocks — never read code aloud
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/~~~[\s\S]*?~~~/g, ' ')
    // inline code
    .replace(/`([^`]*)`/g, '$1')
    // headers, emphasis, rules
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/\*\*([^*]*)\*\*/g, '$1')
    .replace(/\*([^*]*)\*/g, '$1')
    .replace(/^---+\s*$/gm, '')
    // symbols TTS reads oddly
    .replace(/Φ/g, 'Phi')
    .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, ' ')
    // urls — say nothing, they're noise aloud
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/\s*\n\s*/g, '. ')
    .replace(/[.\s]{2,}/g, '. ')
    .trim();
}

/** Cap at ~2 spoken sentences' worth of trailing truncation safety. */
function clampForSpeech(text: string, max = 600): string {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const lastStop = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('? '), cut.lastIndexOf('! '));
  return (lastStop > 40 ? cut.slice(0, lastStop + 1) : cut).trim();
}

export function getSpeakingState() { return isSpeaking; }

export function getPersona(): string {
  try {
    const p = localStorage.getItem(PERSONA_STORAGE);
    return p && PERSONAS.some(x => x.key === p) ? p : DEFAULT_PERSONA;
  } catch { return DEFAULT_PERSONA; }
}
export function setPersona(key: string) {
  try { localStorage.setItem(PERSONA_STORAGE, key); } catch {}
}

export function stopSpeaking() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.src = '';
    currentAudio = null;
  }
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  isSpeaking = false;
}

async function speakEdgeTTS(text: string, persona: string): Promise<boolean> {
  try {
    const res = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, persona }),
    });
    if (!res.ok) return false;
    const blob = await res.blob();
    if (!blob.size) return false;

    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    currentAudio = audio;
    isSpeaking = true;
    audio.onended = () => { isSpeaking = false; currentAudio = null; URL.revokeObjectURL(url); };
    audio.onerror = () => { isSpeaking = false; currentAudio = null; URL.revokeObjectURL(url); };
    await audio.play();
    return true;
  } catch {
    return false;
  }
}

function speakFallback(text: string) {
  if (!('speechSynthesis' in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.05;
  utterance.pitch = 1.1;
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.name.includes('Female') || v.name.includes('Samantha') || v.name.includes('Google UK English Female')
  );
  if (preferred) utterance.voice = preferred;
  utterance.onstart = () => { isSpeaking = true; };
  utterance.onend   = () => { isSpeaking = false; };
  utterance.onerror = () => { isSpeaking = false; };
  window.speechSynthesis.speak(utterance);
}

export async function speakText(text: string): Promise<void> {
  if (!text.trim()) return;
  stopSpeaking();

  const speakable = clampForSpeech(toSpeakable(text));
  if (!speakable) return;

  const persona = getPersona();
  const ok = await speakEdgeTTS(speakable, persona);
  if (ok) return;

  speakFallback(speakable);
}
