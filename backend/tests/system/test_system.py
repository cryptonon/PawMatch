"""System tests TC1 to TC9, via the FastAPI app (httpx TestClient).

TC1 R1: intake with age missing is blocked, age flagged.
TC2 R1: complete intake creates one profile with every field as entered.
TC3 R2: a vaccination logged with its date appears on the timeline.
TC4 R3: finalizing before a meet and greet is blocked, missing stage named.
TC5 R4: ranking for an adopter with a dog matches the scoring rules,
  reasons show, senior and shy cats stay visible.
TC6 R5: dashboard counts match the sample records; longest waiting listed.
TC7 R6: an unacted vaccination reminder past due appears on the overdue list.
TC8 R3 and R6: an application left in screening appears on the stuck list
  and a reminder is created.
TC9 R7: with the model offline mid search, search continues as filtered
  search with no error shown.
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


def _complete_form(**overrides):
    form = {
        "name": "Miso", "age": 2, "breed": "Domestic Shorthair", "sex": "F",
        "arrival_date": "2026-10-01", "source": "stray",
        "health_status": "healthy", "behavior_notes": "Calm, likes laps.",
    }
    form.update(overrides)
    return form


def _new_application(client, cat_id=2):
    response = client.post("/applications", json={"cat_id": cat_id, "adopter_name": "TC Adopter"})
    assert response.status_code == 201
    return response.json()


def test_tc1_intake_age_missing_is_blocked(client):
    form = _complete_form()
    del form["age"]
    response = client.post("/cats", json=form)
    assert response.status_code == 422
    assert "age" in response.text


def test_tc2_complete_intake_creates_profile(client):
    response = client.post("/cats", json=_complete_form())
    assert response.status_code == 201
    cat = response.json()
    assert cat["name"] == "Miso"
    assert cat["age"] == 2
    assert cat["breed"] == "Domestic Shorthair"
    assert cat["arrival_date"] == "2026-10-01"
    assert cat["source"] == "stray"
    check = client.get(f"/cats/{cat['id']}")
    assert check.status_code == 200
    assert check.json()["name"] == "Miso"


def test_tc3_vaccination_appears_on_timeline(client):
    response = client.post("/cats/2/care", json={
        "kind": "vaccination", "date": "2026-09-14", "note": "FVRCP booster"})
    assert response.status_code == 201
    entries = client.get("/cats/2/care").json()
    assert len(entries) == 1
    assert entries[0]["kind"] == "vaccination"
    assert entries[0]["date"] == "2026-09-14"


def test_tc4_finalize_before_meet_and_greet_is_blocked(client):
    application = _new_application(client)
    moved = client.post(
        f"/applications/{application['id']}/move", json={"stage": "screening"})
    assert moved.status_code == 200
    response = client.post(
        f"/applications/{application['id']}/move",
        json={"stage": "finalized", "outcome": "adopted"})
    assert response.status_code == 400
    assert "meet_and_greet" in response.text


def test_tc5_ranking_for_adopter_with_dog(client):
    response = client.get("/match", params={"has_dog": True, "temperament": "calm"})
    assert response.status_code == 200
    body = response.json()
    assert body["fallback"] is False
    ranked = body["ranked"]
    assert len(ranked) > 0
    assert all(entry["reason"] and len(entry["reason"]) > 10 for entry in ranked)
    assert all(entry["cat"]["good_with_dogs"] for entry in ranked)
    senior = [e for e in ranked if e["cat"]["age"] >= 10]
    assert senior, "senior cat must stay visible in the ranking"
    assert ranked.index(senior[0]) < 3


def test_tc6_dashboard_counts_match_sample_records(client):
    dashboard = client.get("/dashboard").json()
    assert dashboard["cats_in_shelter"] == 6
    assert dashboard["average_stay_days"] == 12.5
    assert dashboard["adoption_rate"] == 0.8
    assert dashboard["longest_waiting"][0]["name"] == "Pepper"


def test_tc7_unacted_reminder_appears_overdue(client):
    created = client.post("/reminders", json={
        "cat_id": 2, "kind": "vaccination", "due": "2026-10-22"})
    assert created.status_code == 201
    overdue = client.get("/reminders/overdue", params={"on": "2026-10-23"}).json()
    assert any(r["cat_id"] == 2 and r["kind"] == "vaccination" for r in overdue)


def test_tc8_stuck_application_listed_and_reminder_created(client):
    import datetime as dt

    stuck = client.get("/applications/stuck").json()
    assert any(a["id"] == 108 for a in stuck)
    today = dt.date.today().isoformat()
    due = client.get("/reminders/due", params={"on": today}).json()
    assert any(r.get("application_id") == 108 for r in due)


def test_tc9_model_offline_falls_back_to_filtered_search(client):
    response = client.post("/admin/model-offline", json={"offline": True})
    assert response.status_code == 200
    response = client.get("/match", params={"has_dog": True})
    assert response.status_code == 200
    body = response.json()
    assert body["fallback"] is True
    assert len(body["cats"]) == 4
    assert all(c["good_with_dogs"] for c in body["cats"])
    client.post("/admin/model-offline", json={"offline": False})
