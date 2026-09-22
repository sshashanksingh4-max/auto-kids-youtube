"""Lightweight checks for the rendered MP4 artifact."""
from __future__ import annotations

import json
import subprocess
import sys


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
    return {
        "duration_seconds": round(duration, 1),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "sampled_frames": len(frames),
        "moving_sample_ratio": round(motion_ratio, 3),
        "mean_frame_difference": round(sum(differences) / len(differences), 2),
    }


if __name__ == "__main__":
    result = inspect_video(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
