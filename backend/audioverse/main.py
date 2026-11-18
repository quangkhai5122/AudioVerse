"""AudioVerse safe-local proof of concept.

THIS APP IS NOT PRODUCTION READY. X-Demo-Actor is NOT authentication.
"""
import re
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from audioverse.content import (
    assert_permission,
    read_json,
    validate_rights_manifest,
    validate_story,
)
from audioverse.engine import InvalidChoice
from audioverse.rights import RightsViolationError, renewal_warning_level
from audioverse.settings import Settings
from audioverse.storage import (
    ReplayConflict,
    RunNotFound,
    VersionConflict,
    choose,
    create_run,
    event_history,
    get_run,
    init_db,
)


class NewRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    story_id: str


class ChoiceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice_id: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings.from_env()
    if cfg.env != "demo":
        raise RuntimeError("This starter must not run outside demo mode")
    story = read_json(cfg.content_path)
    license_info = read_json(cfg.license_path)
    validate_story(story)
    if story["license_id"] != license_info["id"]:
        raise RuntimeError("Story license mismatch")
    manifest = validate_rights_manifest(license_info, story=story, media_dir=cfg.media_path)
    assert_permission(manifest, "stream")
    assert_permission(manifest, "derivative")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(cfg.db_path)
        yield

    app = FastAPI(title="AudioVerse — Local Demo API", version="0.1.0", lifespan=lifespan)

    def actor_or_400(x_demo_actor: Annotated[str, Header()] = "demo-local") -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_-]{4,64}", x_demo_actor):
            raise HTTPException(400, "Demo actor must be 4–64 safe characters")
        return x_demo_actor

    def enforce_right(action: str, scene_id: str | None = None) -> None:
        try:
            assert_permission(manifest, action, scene_id=scene_id)
        except RightsViolationError as exc:
            raise HTTPException(403, {"code": exc.code, "message": exc.reason}) from None

    @app.get("/healthz")
    def health():
        return {"status": "ok", "environment": "demo", "ai": "disabled", "billing": "disabled"}

    @app.get("/api/v1/catalog")
    def catalog():
        cot = manifest.grant.chain_of_title
        return [
            {
                "id": story["id"],
                "edition_id": manifest.grant.edition_id,
                "title": story["title"],
                "description": story["description"],
                "genre": story["genre"],
                "locale": "vi-VN",
                "mode": "interactive",
                "demo": True,
                "licensed": True,
                "attribution": cot.attribution_text,
                "voice_label": cot.voice_label,
                "rights_grant_id": manifest.grant.grant_id,
                "rights_grant_version": manifest.grant.version,
            }
        ]

    @app.get("/api/v1/works/{story_id}")
    def work(story_id: str):
        if story_id != story["id"]:
            raise HTTPException(404, "Work not found")
        return catalog()[0]

    @app.get("/api/v1/works/{story_id}/rights")
    def work_rights(story_id: str):
        if story_id != story["id"]:
            raise HTTPException(404, "Work not found")
        g = manifest.grant
        return {
            "grant_id": g.grant_id,
            "version": g.version,
            "work_id": g.work_id,
            "edition_id": g.edition_id,
            "source_type": g.source_type,
            "state": g.state,
            "verified_for_demo": g.verified_for_demo,
            "production_approval": g.production_approval,
            "granted_actions": g.granted_actions,
            "denied_actions": g.denied_actions,
            "territories": g.territories,
            "languages": g.languages,
            "valid_from": g.valid_from.isoformat(),
            "expires_at": g.expires_at.isoformat() if g.expires_at else None,
            "renewal_warning": renewal_warning_level(g),
            "takedown_active": g.takedown_active,
            "dispute_active": g.dispute_active,
            "attribution": g.chain_of_title.attribution_text,
            "voice_label": g.chain_of_title.voice_label,
            "reviewer_id": g.reviewer_id,
            "evidence_version": g.evidence.contract_version,
            "asset_count": len(manifest.assets),
        }

    @app.post("/api/v1/runs", status_code=201)
    def new_run(body: NewRun, x_demo_actor: Annotated[str, Header()] = "demo-local"):
        actor = actor_or_400(x_demo_actor)
        if body.story_id != story["id"]:
            raise HTTPException(404, "Story not found")
        enforce_right("derivative")
        return create_run(cfg.db_path, story, actor)

    @app.get("/api/v1/runs/{run_id}")
    def run(run_id: str, x_demo_actor: Annotated[str, Header()] = "demo-local"):
        actor = actor_or_400(x_demo_actor)
        try:
            return get_run(cfg.db_path, story, actor, run_id)
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None

    @app.post("/api/v1/runs/{run_id}/choices")
    def select_choice(
        run_id: str,
        body: ChoiceBody,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        actor = actor_or_400(x_demo_actor)
        enforce_right("derivative")
        try:
            return choose(
                cfg.db_path,
                story,
                actor,
                run_id,
                body.choice_id,
                body.expected_version,
                body.idempotency_key,
            )
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None
        except InvalidChoice as exc:
            raise HTTPException(422, str(exc)) from None
        except (VersionConflict, ReplayConflict) as exc:
            raise HTTPException(409, str(exc)) from None

    @app.get("/api/v1/runs/{run_id}/events")
    def events(run_id: str, x_demo_actor: Annotated[str, Header()] = "demo-local"):
        actor = actor_or_400(x_demo_actor)
        try:
            return event_history(cfg.db_path, actor, run_id)
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None

    @app.get("/api/v1/audio/{scene_id}.mp3")
    def stream_demo(scene_id: str):
        if scene_id not in story["scenes"]:
            raise HTTPException(404, "Scene not found")
        enforce_right("stream", scene_id=scene_id)
        file = cfg.media_path / f"{scene_id}.mp3"
        if not file.is_file():
            raise HTTPException(404, "Demo audio unavailable; run generate_demo_audio.py")
        return FileResponse(
            file,
            media_type="audio/mpeg",
            filename=f"{scene_id}.mp3",
            content_disposition_type="inline",
            headers={"Cache-Control": "public, max-age=300"},
        )

    @app.get("/", include_in_schema=False)
    def index():
        file = cfg.web_path / "index.html"
        return HTMLResponse(file.read_text(encoding="utf-8"))

    @app.get("/web/{name}", include_in_schema=False)
    def assets(name: str):
        # Strictly allowlisted immutable paths; no generic static directory exposure.
        if name not in {"app.js", "style.css"}:
            raise HTTPException(404, "Asset not found")
        file = cfg.web_path / name
        return FileResponse(
            file,
            media_type="text/javascript" if name.endswith(".js") else "text/css",
        )

    @app.get("/robots.txt", include_in_schema=False)
    def robots():
        return Response("User-agent: *\nDisallow: /\n", media_type="text/plain")

    return app


app = create_app()

if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        "audioverse.main:app",
        host=os.getenv("AUDIOVERSE_HOST", "127.0.0.1"),
        port=int(os.getenv("AUDIOVERSE_PORT", "8765")),
        reload=False,
    )
