import asyncio
import os
import subprocess
import tempfile
from spool import spool_exchange

PERSONAS = {
    "seven": {
        "name": "Seven (Sage 7)",
        "voice_id": "en-US-MichelleNeural",
        "pitch": "-1Hz",
        "rate": "+2%",
        "accent": "Midwest American",
        "description": "Grounded, straightforward, pragmatic Midwest American cadence"
    },
}

async def synthesize_edge_audio(text: str, persona_key: str = "seven") -> bytes:
    import edge_tts
    persona = PERSONAS.get(persona_key.lower(), PERSONAS["seven"])
    communicate = edge_tts.Communicate(
        text=text[:1500],
        voice=persona["voice_id"],
        rate=persona["rate"],
        pitch=persona["pitch"]
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
        temp_path = fp.name

    try:
        await communicate.save(temp_path)
        with open(temp_path, "rb") as f:
            data = f.read()
        return data
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def speak_sync(text: str, persona_key: str = "seven", spool: bool = True):
    persona = PERSONAS.get(persona_key.lower(), PERSONAS["seven"])
    agent_name = "Sage7" if persona_key == "seven" else ("ADHD-Sage" if (persona_key == "mama" or persona_key == "adhd") else "Spiral")

    if spool:
        try:
            spool_exchange(
                agent=agent_name,
                user_text="[VOCAL_OUTPUT]",
                assistant_text=text,
                model=f"voice/{persona['voice_id']}",
                tags=["vocal_synthesis", persona_key, persona["accent"].replace(" ", "_").lower()]
            )
        except Exception as e:
            print(f"[VOICE SPOOL ERROR]: {e}")

    print(f"\n🔊 [{persona['name']} ({persona['accent']}) speaking]: \"{text}\"")

    try:
        audio_bytes = asyncio.run(synthesize_edge_audio(text, persona_key))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            temp_path = fp.name
            fp.write(audio_bytes)

        subprocess.run(["mpv", "--no-terminal", temp_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as edge_err:
        print(f"[VOICE FALLBACK]: {edge_err}")
        try:
            subprocess.run(["termux-tts-speak", text], check=False)
        except Exception:
            pass

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "Sage Seven voice broker operational."
    p = sys.argv[2] if len(sys.argv) > 2 else "seven"
    speak_sync(msg, p)
