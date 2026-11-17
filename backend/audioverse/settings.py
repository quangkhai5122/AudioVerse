"""Local-only demo configuration.

Do not deploy this app to the Internet with demo actor headers or SQLite.
"""
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    env: str = "demo"
    db_path: Path = ROOT / "local_data" / "audioverse.db"
    content_path: Path = ROOT / "content" / "demo_story" / "story.json"
    license_path: Path = ROOT / "content" / "licenses" / "demo_license.json"
    media_path: Path = ROOT / "media" / "demo"
    web_path: Path = ROOT / "web"

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.getenv("AUDIOVERSE_ENV", "demo")
        if env != "demo":
            raise RuntimeError("Starter runs only in AUDIOVERSE_ENV=demo; production gates pending")
        return cls(env=env, db_path=Path(os.getenv("AUDIOVERSE_DB_PATH", str(cls.db_path))).resolve())
