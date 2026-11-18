"""Configuration for AudioVerse demo and authenticated test profiles.

Do not deploy this app to the Internet with demo actor headers enabled or SQLite.
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
    auth_secret: str = "demo-local-hmac-secret-do-not-use-in-prod-2026"
    allow_demo_header: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.getenv("AUDIOVERSE_ENV", "demo")
        if env != "demo":
            raise RuntimeError("Starter runs only in AUDIOVERSE_ENV=demo; production gates pending")
        allow_demo = os.getenv("AUDIOVERSE_ALLOW_DEMO_HEADER", "true").lower() in {
            "1",
            "true",
            "yes",
        }
        return cls(
            env=env,
            db_path=Path(os.getenv("AUDIOVERSE_DB_PATH", str(cls.db_path))).resolve(),
            auth_secret=os.getenv("AUDIOVERSE_AUTH_SECRET", cls.auth_secret),
            allow_demo_header=allow_demo,
        )
