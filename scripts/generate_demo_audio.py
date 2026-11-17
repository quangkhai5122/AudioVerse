"""Generate locally synthetic sample MP3s from *original project text*.

Requires `espeak` and `ffmpeg`. Never points at Internet audio or imitates a real speaker.
This voice is deliberately robotic and is NOT a TTS product benchmark.
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if not shutil.which("espeak") or not shutil.which("ffmpeg"):
        raise SystemExit("Install espeak and ffmpeg or use the transcript-only demo")
    story = json.loads((ROOT / "content/demo_story/story.json").read_text(encoding="utf-8"))
    dest = ROOT / "media/demo"
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        for scene_id, scene in story["scenes"].items():
            wav = Path(temp) / f"{scene_id}.wav"
            subprocess.run(["espeak", "-v", "vi", "-s", "135", "-w", str(wav),
                            scene["text"]], check=True, capture_output=True)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-i", str(wav), "-ac", "1", "-ar", "22050", "-b:a", "64k",
                            str(dest / f"{scene_id}.mp3")], check=True, capture_output=True)
    print(f"Generated {len(story['scenes'])} original demo MP3 files in {dest}")


if __name__ == "__main__":
    main()
