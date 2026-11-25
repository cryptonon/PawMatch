"""System tests for the v2.1.0 features, via the FastAPI app.

Bios: draft, approve, publish, and the publish rejection for a draft.
Watchlist: ordering and content over HTTP. Dashboard: capacity fields.
Plus the API error paths (unknown cat, application, reminder, bio).
"""
import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app
from app.seed import seed_data


@pytest.fixture
def client():
    seed_data()
    with TestClient(app) as test_client:
        yield test_client
    store.reset()
    app.state.model_offline = False


def test_bio_draft_approve_publish_over_http(client):
    draft = client.post("/cats/1/bio/draft", json={"notes": "Calm and shy"})
    assert draft.status_code == 201
    assert draft.json()["state"] == "draft"
    assert "Pepper" in draft.json()["text"]
    rejected = client.post("/cats/1/bio/publish")
    assert rejected.status_code == 400
    approved = client.post("/cats/1/bio/approve")
    assert approved.status_code == 200
    assert approved.json()["state"] == "approved"
    published = client.post("/cats/1/bio/publish")
    assert published.status_code == 200
    assert published.json()["state"] == "published"
    fetched = client.get("/cats/1/bio")
    assert fetched.status_code == 200
    assert fetched.json()["state"] == "published"


def test_bio_missing_draft_returns_404_and_approve_fails(client):
    assert client.get("/cats/2/bio").status_code == 404
    assert client.post("/cats/2/bio/approve").status_code == 400
    assert client.post("/cats/999/bio/draft", json={}).status_code == 404


def test_watchlist_endpoint_is_sorted_and_flagged(client):
    body = client.get("/watchlist").json()
    assert len(body) == 6
    probs = [e["probability"] for e in body]
    assert probs == sorted(probs, reverse=True)
    assert body[0]["cat"]["name"] == "Pepper"
    assert all(e["reason"] and e["cat"]["name"] in e["reason"] for e in body)
    assert all(e["flagged"] is False for e in body)


def test_dashboard_capacity_fields(client):
    dashboard = client.get("/dashboard").json()
    assert dashboard["capacity_percent"] == 75.0
    assert dashboard["alert"] is None


def test_api_error_paths(client):
    assert client.get("/cats/999").status_code == 404
    assert client.post("/cats/999/care", json={
        "kind": "vaccination", "date": "2026-09-14"}).status_code == 404
    assert client.post("/applications", json={"cat_id": 999}).status_code == 404
    assert client.get("/applications/999").status_code == 404
    assert client.post("/applications/999/move",
                       json={"stage": "screening"}).status_code == 404
    assert client.post("/applications/999/close",
                       json={"outcome": "withdrawn"}).status_code == 404
    assert client.post("/reminders/999/acted").status_code == 404
    assert client.post("/reminders", json={
        "cat_id": 999, "kind": "vaccination",
        "due": "2026-10-22"}).status_code == 404
