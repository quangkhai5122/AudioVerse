from uuid import uuid4


def _start(client):
    r = client.post("/api/v1/runs", json={"story_id": "ben-kia-canh-cua"})
    assert r.status_code == 201, r.text
    return r.json()


def _pick(client, state, choice, key=None):
    key = key or uuid4().hex
    r = client.post(f"/api/v1/runs/{state['run_id']}/choices", json={
        "choice_id": choice, "expected_version": state["version"],
        "idempotency_key": key,
    })
    return r, key


def test_health_and_catalog(client):
    health = client.get("/healthz").json()
    assert health == {"status": "ok", "environment": "demo", "ai": "disabled", "billing": "disabled"}
    catalog = client.get("/api/v1/catalog").json()
    assert catalog[0]["mode"] == "interactive"
    assert client.get("/api/v1/works/unknown").status_code == 404
    assert client.get("/").status_code == 200
    assert client.get("/web/style.css").status_code == 200
    assert client.get("/web/secrets.txt").status_code == 404


def test_complete_story_and_event_log(client):
    state = _start(client)
    assert state["version"] == 0
    assert state["scene"]["id"] == "s0"
    for choice, to_scene in [("follow-tracks", "s1"), ("take-key", "s3"),
                             ("open-cellar", "s4"), ("archive-evidence", "s8")]:
        response, _ = _pick(client, state, choice)
        assert response.status_code == 200, response.text
        state = response.json()
        assert state["scene"]["id"] == to_scene
    assert state["version"] == 4
    assert state["scene"]["ending"] is True
    history = client.get(f"/api/v1/runs/{state['run_id']}/events").json()
    assert len(history) == 4
    assert history[-1]["to_scene"] == "s8"


def test_idempotent_replay_and_key_mismatch(client):
    state = _start(client)
    reply, key = _pick(client, state, "climb-stairs")
    assert reply.status_code == 200
    replay, _ = _pick(client, state, "climb-stairs", key)
    assert replay.status_code == 200
    assert replay.json() == reply.json()
    mismatch, _ = _pick(client, state, "follow-tracks", key)
    assert mismatch.status_code == 409
    assert len(client.get(f"/api/v1/runs/{state['run_id']}/events").json()) == 1


def test_stale_version_and_invalid_precondition(client):
    state = _start(client)
    reply, _ = _pick(client, state, "climb-stairs")
    assert reply.status_code == 200
    stale, _ = _pick(client, state, "follow-tracks")
    assert stale.status_code == 409
    state = reply.json()
    reply, _ = _pick(client, state, "read-note")
    assert reply.status_code == 200
    state = reply.json()
    invalid, _ = _pick(client, state, "open-cellar")
    assert invalid.status_code == 422
    assert client.get(f"/api/v1/runs/{state['run_id']}").json()["version"] == state["version"]


def test_demo_actor_isolation_not_real_auth(client):
    state = _start(client)
    rid = state["run_id"]
    assert client.get(f"/api/v1/runs/{rid}", headers={"X-Demo-Actor": "other-demo"}).status_code == 404
    assert client.get(f"/api/v1/runs/{rid}", headers={"X-Demo-Actor": "invalid space"}).status_code == 400


def test_audio_served_only_for_seed_scene(client):
    response = client.get("/api/v1/audio/s0.mp3")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.content[:3] == b"ID3" or response.content[:2] in [b"\xff\xfb", b"\xff\xf3"]
    assert client.get("/api/v1/audio/not-a-scene.mp3").status_code == 404


def test_malformed_payload_rejected(client):
    assert client.post("/api/v1/runs", json={"story_id": "ben-kia-canh-cua", "admin": True}).status_code == 422
    state = _start(client)
    assert client.post(f"/api/v1/runs/{state['run_id']}/choices", json={
        "choice_id": "follow-tracks", "expected_version": 0, "idempotency_key": "bad!key#",
    }).status_code == 422
