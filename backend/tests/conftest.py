from pathlib import Path

import pytest
from audioverse.main import create_app
from audioverse.settings import ROOT, Settings
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path):
    cfg = Settings(db_path=tmp_path / "events.db",
                   content_path=ROOT / "content/demo_story/story.json",
                   license_path=ROOT / "content/licenses/demo_license.json",
                   media_path=ROOT / "media/demo", web_path=ROOT / "web")
    with TestClient(create_app(cfg)) as http:
        yield http
