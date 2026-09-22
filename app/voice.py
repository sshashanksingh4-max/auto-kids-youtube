"""Hindi voice routing for the animation renderer.

Svara is the default for a consistent, youthful cast voice. The built-in
eSpeak voice is an explicit preview option; Svara failures are raised instead
of silently replacing natural speech with robotic audio.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urljoin

import httpx


SVARA_SPACE = os.getenv("KIDS_SVARA_SPACE", "https://kenpath-svara-tts.hf.space").rstrip("/")
SVARA_EVENT = "/gradio_api/call/generate_speech"


def _svara_file_url(payload: object) -> str | None:
    """Find the generated audio file in Gradio's serialized output."""
    if isinstance(payload, dict):
        for key in ("url", "path"):
            value = payload.get(key)
            if isinstance(value, str) and ("audio.wav" in value or "gradio_api/file=" in value):
                return value
        for value in payload.values():
            found = _svara_file_url(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _svara_file_url(value)
            if found:
                return found
    elif isinstance(payload, str) and ("audio.wav" in payload or "gradio_api/file=" in payload):
        return payload
    return None


def synthesize_svara(text: str, voice: str, out_wav: Path) -> None:
    """Generate one Hindi line through the public Svara ZeroGPU Space.

    This makes one inference request and never retries, since the public free
    Space has limited shared compute.  Its free-tier availability is not a
    production SLA.
    """
    if voice not in {"chintu", "mini", "golu", "tinku", "narrator"}:
        raise ValueError(f"Unknown Svara speaker: {voice}")
    # Keep voice identity, emotion conditioning, and pitch treatment identical
    # across characters. Character personality comes from the script and acting.
    data = ["Hindi (हिन्दी)", "Female", f"<clear> {text}", 0.8, 0.8, 1.1, 1200]
    with httpx.Client(timeout=httpx.Timeout(180.0, connect=20.0)) as client:
        started = client.post(f"{SVARA_SPACE}{SVARA_EVENT}", json={"data": data})
        started.raise_for_status()
        event_id = started.json().get("event_id")
        if not event_id:
            raise RuntimeError("Svara did not return an inference event id")
        result = client.get(f"{SVARA_SPACE}{SVARA_EVENT}/{event_id}")
        result.raise_for_status()

        completion_data = None
        is_error = False
        lines = result.text.splitlines()
        for index, line in enumerate(lines):
            if line.startswith("event:"):
                is_error = line.partition(":")[2].strip() == "error"
            elif line.startswith("data:"):
                raw = line.partition(":")[2].strip()
                if is_error:
                    raise RuntimeError(f"Svara inference failed: {raw[:300]}")
                if index and any(item == "event: complete" for item in lines[max(0, index - 3):index]):
                    try:
                        completion_data = json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise RuntimeError("Svara returned invalid completion data") from exc
                    break
        audio_url = _svara_file_url(completion_data)
        if not audio_url:
            raise RuntimeError("Svara completed without returning an audio file")
        audio_response = client.get(urljoin(f"{SVARA_SPACE}/", audio_url))
        audio_response.raise_for_status()
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        out_wav.write_bytes(audio_response.content)


def _pitch_shift_youthful_voice(source: Path, destination: Path) -> None:
    """Raise pitch ~2 semitones while restoring the original timing."""
    ratio = 2 ** (2.0 / 12.0)
    shifted_rate = round(24000 * ratio)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(source),
        "-af", f"asetrate={shifted_rate},aresample=24000,atempo={1/ratio:.6f}",
        "-ar", "24000", "-ac", "1", str(destination),
    ], check=True)


def synthesize_scene_voice(text: str, voice: str, out_wav: Path) -> str:
    """Write a scene line and return the actual voice mode used."""
    # Natural Hindi TTS is the product path. eSpeak remains an explicit
    # preview option so a local render cannot silently sound robotic.
    provider = os.getenv("KIDS_TTS_PROVIDER", "svara").strip().lower()
    if provider not in {"preview", "svara"}:
        raise ValueError("KIDS_TTS_PROVIDER must be 'preview' or 'svara'")
    if provider == "preview":
        # This mode is only for local previews and is explicitly reported as
        # synthetic/robotic in metadata.
        subprocess.run([
            "espeak", "-v", "hi", "-s", "132", "-p", "48", "-a", "165",
            "-w", str(out_wav), text,
        ], check=True)
        return "espeak_preview"

    raw_wav = out_wav.with_name(f"{out_wav.stem}_raw.wav")
    synthesize_svara(text, voice, raw_wav)
    _pitch_shift_youthful_voice(raw_wav, out_wav)
    raw_wav.unlink(missing_ok=True)
    return "svara_shared_youthful"
