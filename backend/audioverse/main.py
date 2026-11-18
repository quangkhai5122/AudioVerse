"""AudioVerse FastAPI application with T002 rights, T003 auth/RBAC/migrations, and T004 secure media.

Supports Bearer token authentication, device sessions, guest-to-account migration,
personal data export/deletion, RBAC audit logs, deterministic event replay recovery,
and short-lived HMAC-signed media authorization & Range delivery (`T004`).
"""
import re
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from audioverse.auth import (
    STAFF_REVIEWER_ROLES,
    AuthError,
    ForbiddenError,
    Principal,
    delete_user_account,
    export_user_data,
    list_device_sessions,
    login_user,
    migrate_guest_runs,
    refresh_device_session,
    register_user,
    require_role,
    revoke_device_session,
    verify_access_token,
    verify_security_audit_chain,
)
from audioverse.content import (
    assert_permission,
    read_json,
    validate_rights_manifest,
    validate_story,
)
from audioverse.engine import InvalidChoice
from audioverse.media import (
    MediaAccessError,
    authorize_playback,
    create_offline_lease,
    deliver_signed_media,
    invalidate_media_cache,
    sync_media_registry,
    validate_offline_lease,
)
from audioverse.rights import RightsViolationError, renewal_warning_level
from audioverse.settings import Settings
from audioverse.storage import (
    ReplayConflict,
    RunNotFound,
    TamperDetectedError,
    VersionConflict,
    choose,
    create_run,
    event_history,
    get_library_items,
    get_run,
    init_db,
    list_continue_listening,
    restore_run_from_events,
    set_library_follow,
    update_playback_progress,
)


class NewRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    story_id: str


class ChoiceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice_id: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


class RegisterBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=128)
    device_name: str = Field(default="default-device", min_length=1, max_length=128)


class LoginBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    device_name: str = Field(default="default-device", min_length=1, max_length=128)


class RefreshBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(min_length=1, max_length=128)
    refresh_token: str = Field(min_length=16, max_length=256)


class MigrateGuestBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    guest_actor: str = Field(min_length=4, max_length=64, pattern=r"^[a-zA-Z0-9_-]{4,64}$")


class PlaybackAuthorizeBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    work_id: str = Field(min_length=1, max_length=128)
    scene_id: str = Field(min_length=1, max_length=128)
    edition_id: str | None = Field(default=None, min_length=1, max_length=128)
    action: Literal["stream", "offline"] = "stream"
    territory: str = Field(default="VN", min_length=2, max_length=32)
    ttl_seconds: int = Field(default=300, ge=1, le=900)


class ProgressBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scene_id: str = Field(min_length=1, max_length=128)
    position_ms: int = Field(ge=0, le=86_400_000)
    playback_speed: float = Field(default=1.0, ge=0.8, le=2.0)


class LibraryFollowBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    followed: bool = True


class OfflineLeaseBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    work_id: str = Field(min_length=1, max_length=128)
    scene_id: str = Field(min_length=1, max_length=128)
    edition_id: str | None = Field(default=None, min_length=1, max_length=128)
    territory: str = Field(default="VN", min_length=2, max_length=32)
    lease_hours: int = Field(default=48, ge=1, le=720)
    max_quota_bytes: int = Field(default=50 * 1024 * 1024, ge=1024, le=500 * 1024 * 1024)


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
    story["edition_id"] = manifest.grant.edition_id
    assert_permission(manifest, "stream")
    assert_permission(manifest, "derivative")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(cfg.db_path, initial_story=story)
        sync_media_registry(cfg.db_path, manifest, cfg.media_path)
        yield

    app = FastAPI(title="AudioVerse — Local Demo API", version="0.1.0", lifespan=lifespan)

    def resolve_principal(
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
        *,
        require_token: bool = False,
    ) -> Principal:
        if authorization is not None:
            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    401,
                    {"code": "AUTH_INVALID_HEADER", "message": "Expected Bearer token"},
                )
            raw_token = authorization.removeprefix("Bearer ").strip()
            try:
                return verify_access_token(
                    cfg.db_path,
                    secret=cfg.auth_secret,
                    token=raw_token,
                )
            except AuthError as exc:
                raise HTTPException(
                    401, {"code": exc.code, "message": exc.message}
                ) from None

        if require_token or not cfg.allow_demo_header:
            raise HTTPException(
                401,
                {"code": "AUTH_REQUIRED", "message": "Bearer authentication required"},
            )
        if not re.fullmatch(r"[a-zA-Z0-9_-]{4,64}", x_demo_actor):
            raise HTTPException(400, "Demo actor must be 4–64 safe characters")
        return Principal(actor_id=x_demo_actor, role="listener", authenticated=False)

    def enforce_right(action: str, scene_id: str | None = None) -> None:
        try:
            assert_permission(manifest, action, scene_id=scene_id)
        except RightsViolationError as exc:
            raise HTTPException(403, {"code": exc.code, "message": exc.reason}) from None

    @app.get("/healthz")
    def health():
        return {"status": "ok", "environment": "demo", "ai": "disabled", "billing": "disabled"}

    # --- Catalog & Rights (Anonymous browse permitted per ACC-01) ---

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

    # --- Authentication, Device Sessions, Migration, Export/Delete (T003) ---

    @app.post("/api/v1/auth/register", status_code=201)
    def auth_register(body: RegisterBody):
        try:
            return register_user(
                cfg.db_path,
                secret=cfg.auth_secret,
                email=body.email,
                password=body.password,
                display_name=body.display_name,
                device_name=body.device_name,
                role="listener",
            )
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/api/v1/auth/login")
    def auth_login(body: LoginBody):
        try:
            return login_user(
                cfg.db_path,
                secret=cfg.auth_secret,
                email=body.email,
                password=body.password,
                device_name=body.device_name,
            )
        except AuthError as exc:
            raise HTTPException(401, {"code": exc.code, "message": exc.message}) from None

    @app.post("/api/v1/auth/refresh")
    def auth_refresh(body: RefreshBody):
        try:
            return refresh_device_session(
                cfg.db_path,
                secret=cfg.auth_secret,
                session_id=body.session_id,
                refresh_token=body.refresh_token,
            )
        except AuthError as exc:
            raise HTTPException(401, {"code": exc.code, "message": exc.message}) from None

    @app.post("/api/v1/auth/logout")
    def auth_logout(authorization: Annotated[str | None, Header()] = None):
        principal = resolve_principal(authorization, require_token=True)
        assert principal.session_id is not None
        revoke_device_session(
            cfg.db_path,
            user_id=principal.actor_id,
            session_id=principal.session_id,
        )
        return {"status": "revoked", "session_id": principal.session_id}

    @app.get("/api/v1/me/devices")
    def me_devices(authorization: Annotated[str | None, Header()] = None):
        principal = resolve_principal(authorization, require_token=True)
        return list_device_sessions(cfg.db_path, user_id=principal.actor_id)

    @app.delete("/api/v1/me/devices/{session_id}")
    def me_revoke_device(
        session_id: str,
        authorization: Annotated[str | None, Header()] = None,
    ):
        principal = resolve_principal(authorization, require_token=True)
        ok = revoke_device_session(
            cfg.db_path,
            user_id=principal.actor_id,
            session_id=session_id,
        )
        if not ok:
            raise HTTPException(404, "Session not found")
        return {"status": "revoked", "session_id": session_id}

    @app.post("/api/v1/me/migrate-guest")
    def me_migrate_guest(
        body: MigrateGuestBody,
        authorization: Annotated[str | None, Header()] = None,
    ):
        principal = resolve_principal(authorization, require_token=True)
        try:
            return migrate_guest_runs(
                cfg.db_path,
                guest_actor=body.guest_actor,
                target_user_id=principal.actor_id,
            )
        except ForbiddenError as exc:
            raise HTTPException(409, {"code": exc.code, "message": exc.message}) from None

    @app.get("/api/v1/me/export")
    def me_export(authorization: Annotated[str | None, Header()] = None):
        principal = resolve_principal(authorization, require_token=True)
        return export_user_data(cfg.db_path, user_id=principal.actor_id)

    @app.delete("/api/v1/me")
    def me_delete(authorization: Annotated[str | None, Header()] = None):
        principal = resolve_principal(authorization, require_token=True)
        return delete_user_account(cfg.db_path, user_id=principal.actor_id)

    @app.get("/api/v1/admin/security-audit")
    def admin_security_audit(authorization: Annotated[str | None, Header()] = None):
        principal = resolve_principal(authorization, require_token=True)
        try:
            require_role(
                cfg.db_path,
                principal,
                STAFF_REVIEWER_ROLES,
                action="READ_SECURITY_AUDIT",
            )
        except ForbiddenError as exc:
            raise HTTPException(403, {"code": exc.code, "message": exc.message}) from None
        return {
            "chain_valid": verify_security_audit_chain(cfg.db_path),
            "actor_id": principal.actor_id,
            "role": principal.role,
        }

    # --- Authenticated Media Streaming & Signed Delivery (T004) ---

    @app.post("/api/v1/playback/authorize")
    def playback_authorize(
        body: PlaybackAuthorizeBody,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return authorize_playback(
                cfg.db_path,
                secret=cfg.auth_secret,
                manifest=manifest,
                principal=principal,
                work_id=body.work_id,
                scene_id=body.scene_id,
                action=body.action,
                edition_id=body.edition_id,
                territory=body.territory,
                ttl_seconds=body.ttl_seconds,
                require_entitlement=cfg.require_entitlement,
            )
        except MediaAccessError as exc:
            raise HTTPException(
                exc.status_code, {"code": exc.code, "message": exc.message}
            ) from None

    @app.get("/api/v1/media/{asset_id}")
    def serve_signed_media(
        asset_id: str,
        token: Annotated[str, Query(min_length=16)],
        range_hdr: Annotated[str | None, Header(alias="Range")] = None,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str | None, Header()] = None,
    ):
        caller_actor: str | None = None
        if authorization is not None or x_demo_actor is not None:
            principal = resolve_principal(
                authorization, x_demo_actor or "demo-local"
            )
            caller_actor = principal.actor_id

        try:
            result = deliver_signed_media(
                cfg.db_path,
                secret=cfg.auth_secret,
                manifest=manifest,
                media_dir=cfg.media_path,
                asset_id=asset_id,
                token=token,
                caller_actor_id=caller_actor,
                range_header=range_hdr,
                require_entitlement=cfg.require_entitlement,
            )
        except MediaAccessError as exc:
            raise HTTPException(
                exc.status_code,
                {"code": exc.code, "message": exc.message},
                headers={"Cache-Control": "no-store"},
            ) from None

        return Response(
            content=result.data,
            status_code=result.status_code,
            media_type=result.content_type,
            headers=result.headers,
        )

    @app.post("/api/v1/admin/media/{asset_id}/invalidate")
    def admin_invalidate_media(
        asset_id: str,
        authorization: Annotated[str | None, Header()] = None,
    ):
        principal = resolve_principal(authorization, require_token=True)
        try:
            require_role(
                cfg.db_path,
                principal,
                STAFF_REVIEWER_ROLES,
                action="INVALIDATE_MEDIA_CACHE",
                target_id=asset_id,
            )
            new_epoch = invalidate_media_cache(cfg.db_path, asset_id=asset_id)
        except ForbiddenError as exc:
            raise HTTPException(403, {"code": exc.code, "message": exc.message}) from None
        except MediaAccessError as exc:
            raise HTTPException(
                exc.status_code, {"code": exc.code, "message": exc.message}
            ) from None
        return {"asset_id": asset_id, "cache_epoch": new_epoch, "status": "invalidated"}

    # --- Player Lifecycle, Library Follow, Progress Resume & Offline Leases (T005) ---

    @app.post("/api/v1/me/library/{work_id}")
    def me_follow_work(
        work_id: str,
        body: LibraryFollowBody,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        if work_id != story["id"]:
            raise HTTPException(404, "Work not found")
        return set_library_follow(
            cfg.db_path,
            principal.actor_id,
            work_id,
            body.followed,
        )

    @app.get("/api/v1/me/library")
    def me_library(
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        return get_library_items(cfg.db_path, principal.actor_id)

    @app.get("/api/v1/me/continue-listening")
    def me_continue_listening(
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        return list_continue_listening(cfg.db_path, story, principal.actor_id)

    @app.post("/api/v1/runs/{run_id}/progress")
    def save_run_progress(
        run_id: str,
        body: ProgressBody,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return update_playback_progress(
                cfg.db_path,
                story,
                principal.actor_id,
                run_id,
                scene_id=body.scene_id,
                position_ms=body.position_ms,
                playback_speed=body.playback_speed,
            )
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None
        except VersionConflict as exc:
            raise HTTPException(409, str(exc)) from None

    @app.post("/api/v1/downloads/leases", status_code=201)
    def issue_offline_lease(
        body: OfflineLeaseBody,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return create_offline_lease(
                cfg.db_path,
                secret=cfg.auth_secret,
                manifest=manifest,
                story=story,
                principal=principal,
                work_id=body.work_id,
                scene_id=body.scene_id,
                edition_id=body.edition_id,
                territory=body.territory,
                lease_hours=body.lease_hours,
                max_quota_bytes=body.max_quota_bytes,
                require_entitlement=cfg.require_entitlement,
            )
        except MediaAccessError as exc:
            raise HTTPException(
                exc.status_code, {"code": exc.code, "message": exc.message}
            ) from None

    @app.get("/api/v1/downloads/leases/{lease_id}/validate")
    def check_offline_lease(
        lease_id: str,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return validate_offline_lease(
                cfg.db_path,
                manifest=manifest,
                principal=principal,
                lease_id=lease_id,
            )
        except MediaAccessError as exc:
            raise HTTPException(
                exc.status_code, {"code": exc.code, "message": exc.message}
            ) from None

    # --- Story Runs & Choices (Scoped per authenticated user or demo actor) ---

    @app.post("/api/v1/runs", status_code=201)
    def new_run(
        body: NewRun,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        if body.story_id != story["id"]:
            raise HTTPException(404, "Story not found")
        enforce_right("derivative")
        return create_run(
            cfg.db_path,
            story,
            principal.actor_id,
            edition_id=manifest.grant.edition_id,
        )

    @app.get("/api/v1/runs/{run_id}")
    def run(
        run_id: str,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return get_run(cfg.db_path, story, principal.actor_id, run_id)
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None

    @app.post("/api/v1/runs/{run_id}/choices")
    def select_choice(
        run_id: str,
        body: ChoiceBody,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        enforce_right("derivative")
        try:
            return choose(
                cfg.db_path,
                story,
                principal.actor_id,
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
    def events(
        run_id: str,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return event_history(cfg.db_path, principal.actor_id, run_id)
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None

    @app.post("/api/v1/runs/{run_id}/restore")
    def restore_run(
        run_id: str,
        authorization: Annotated[str | None, Header()] = None,
        x_demo_actor: Annotated[str, Header()] = "demo-local",
    ):
        principal = resolve_principal(authorization, x_demo_actor)
        try:
            return restore_run_from_events(cfg.db_path, story, principal.actor_id, run_id)
        except RunNotFound:
            raise HTTPException(404, "Run not found") from None
        except TamperDetectedError as exc:
            raise HTTPException(409, str(exc)) from None

    @app.get("/api/v1/audio/{scene_id}.mp3")
    def stream_demo(scene_id: str):
        if not cfg.allow_public_sample_audio:
            raise HTTPException(
                403,
                {
                    "code": "PUBLIC_SAMPLE_ROUTE_DISABLED",
                    "message": "Use POST /api/v1/playback/authorize for signed media delivery",
                },
            )
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
