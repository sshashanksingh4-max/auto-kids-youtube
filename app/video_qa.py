"""Lightweight checks for the rendered MP4 artifact."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True, capture_output=True)


def inspect_video(path: str) -> dict:
    probe = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", path,
    ])
    info = json.loads(probe.stdout)
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise ValueError("MP4 must contain both video and audio streams")
    duration = float(info.get("format", {}).get("duration", 0))
    if duration < 30:
        raise ValueError(f"Rendered sample is unexpectedly short: {duration:.1f}s")

    # Sample one frame each second at a small resolution. This catches frozen
    # or missing video sections without needing OpenCV or a cloud service.
    width, height = 160, 90
    decoded = run([
        "ffmpeg", "-v", "error", "-i", path, "-vf",
        f"fps=1,scale={width}:{height},format=rgb24", "-f", "rawvideo", "-",
    ]).stdout
    frame_size = width * height * 3
    frames = [decoded[i:i + frame_size] for i in range(0, len(decoded), frame_size)]
    frames = [frame for frame in frames if len(frame) == frame_size]
    if len(frames) < 10:
        raise ValueError(f"Only {len(frames)} one-second video samples decoded")
    moving_pairs = 0
    differences = []
    for left, right in zip(frames, frames[1:]):
        diff = sum(abs(a - b) for a, b in zip(left, right)) / len(left)
        differences.append(diff)
        if diff >= 0.5:
            moving_pairs += 1
    motion_ratio = moving_pairs / max(1, len(differences))
    if motion_ratio < 0.80:
        raise ValueError(f"Animation appears frozen: only {motion_ratio:.0%} of samples move")

    # Also inspect the stage where faces, hands and props appear. Moving only
    # clouds or a camera cannot satisfy this check: the crop excludes most of
    # the sky and subtitles and focuses on the actors' bodies and interactions.
    action_bytes = run([
        "ffmpeg", "-v", "error", "-i", path, "-vf",
        "fps=1,scale=256:144,crop=196:46:30:72,format=rgb24", "-f", "rawvideo", "-",
    ]).stdout
    action_size = 196 * 46 * 3
    action_frames = [action_bytes[i:i + action_size] for i in range(0, len(action_bytes), action_size)]
    action_frames = [frame for frame in action_frames if len(frame) == action_size]
    action_differences = [
        sum(abs(a - b) for a, b in zip(left, right)) / len(left)
        for left, right in zip(action_frames, action_frames[1:])
    ]
    action_motion_ratio = sum(diff >= 2.0 for diff in action_differences) / max(1, len(action_differences))
    if action_motion_ratio < 0.55:
        raise ValueError(
            f"Character/action area appears frozen: only {action_motion_ratio:.0%} of samples move"
        )
    result = {
        "duration_seconds": round(duration, 1),
        "width": video.get("width"),
        "height": video.get("height"),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "sampled_frames": len(frames),
        "moving_sample_ratio": round(motion_ratio, 3),
        "mean_frame_difference": round(sum(differences) / len(differences), 2),
        "action_area_motion_ratio": round(action_motion_ratio, 3),
    }
    provenance_path = Path(path).with_suffix(".voices.json")
    if provenance_path.exists():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        result["voice_provider"] = provenance.get("provider", "unknown")
        result["voice_modes"] = provenance.get("scene_voice_modes", [])
        result["voice_path_configured"] = (
            result["voice_provider"] == "svara"
            and bool(result["voice_modes"])
            and all(mode in {"svara_child_pitch", "espeak_robot"} for mode in result["voice_modes"])
        )
        result["human_listening_review_required"] = True
        result["voice_review_status"] = "not_recorded"
    else:
        result["voice_path_configured"] = False
        result["voice_provider"] = "unverified"
        result["human_listening_review_required"] = True
        result["voice_review_status"] = "not_recorded"
    return result


if __name__ == "__main__":
    result = inspect_video(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "--require-vertical":
        if result["height"] / result["width"] < 1.7:
            raise ValueError("Short output must use a vertical 9:16-style frame")
        if result["duration_seconds"] > 60:
            raise ValueError("Short output exceeds the 60-second trial limit")
        result["vertical_short_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2))
