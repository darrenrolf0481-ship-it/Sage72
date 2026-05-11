let isSpeaking = false;

export function getSpeakingState() {
  return isSpeaking;
}

export function stopSpeaking() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  isSpeaking = false;
}

export async function speakText(text: string): Promise<void> {
  if (!text.trim() || !('speechSynthesis' in window)) return;

  stopSpeaking();

  const cleanText = text.replace(/[*_#`]/g, '');
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.05;
  utterance.pitch = 1.1;

  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.name.includes('Female') || v.name.includes('Samantha') || v.name.includes('Google UK English Female'));
  if (preferred) utterance.voice = preferred;

  utterance.onstart = () => { isSpeaking = true; };
  utterance.onend = () => { isSpeaking = false; };
  utterance.onerror = () => { isSpeaking = false; };

  window.speechSynthesis.speak(utterance);
}
