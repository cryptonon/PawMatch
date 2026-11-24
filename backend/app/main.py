"""PawMatch FastAPI app. Wires the units together over HTTP.

Run from the backend folder: uvicorn app.main:app --reload
"""
import datetime as _dt

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app import store
from app.adoptions.workflow import WorkflowError, close as close_application, move as move_application
from app.adopters.schemas import AdopterProfile
from app.adopters.search import search as filtered_search
from app.care.timeline import ValidationError, add_entry, timeline
from app.intake.schemas import IntakeForm
from app.intake.validation import validate_intake
from app.metrics.dashboard import metrics as compute_metrics
from app.models import Application, Cat
from app.reminders import scheduler

app = FastAPI(title="PawMatch")
app.state.model_offline = False


class CareEntryIn(BaseModel):
    kind: str
    date: str
    note: str = ""
    end_date: str | None = None


class ApplicationIn(BaseModel):
    cat_id: int
    adopter_name: str = "Adopter"


class MoveIn(BaseModel):
    stage: str
    outcome: str | None = None


class CloseIn(BaseModel):
    outcome: str


class ReminderIn(BaseModel):
    cat_id: int
    kind: str
    due: str


class ModelOfflineIn(BaseModel):
    offline: bool


def _cat_or_404(cat_id):
    for cat in store.cats:
        if cat.id == cat_id:
            return cat
    raise HTTPException(status_code=404, detail="cat not found")


def _application_or_404(application_id):
    for application in store.applications:
        if application.id == application_id:
            return application
    raise HTTPException(status_code=404, detail="application not found")


def _cat_dict(cat):
    return {
        "id": cat.id, "name": cat.name, "age": cat.age, "breed": cat.breed,
        "sex": cat.sex, "arrival_date": cat.arrival_date, "source": cat.source,
        "health_status": cat.health_status, "behavior_notes": cat.behavior_notes,
        "temperament": cat.temperament, "good_with_dogs": cat.good_with_dogs,
        "good_with_children": cat.good_with_children, "status": cat.status,
    }


def _application_dict(application):
    return {
        "id": application.id, "cat_id": application.cat_id,
        "adopter_name": application.adopter_name, "stage": application.stage,
        "outcome": application.outcome, "stage_since": application.stage_since,
        "stay_days": application.stay_days,
    }


def _reminder_dict(reminder):
    return {
        "id": reminder.id, "kind": reminder.kind, "due": reminder.due,
        "cat_id": reminder.cat_id, "application_id": reminder.application_id,
        "acted": reminder.acted,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/cats", status_code=201)
def create_cat(form: IntakeForm):
    data = form.model_dump()
    result = validate_intake(data)
    if not result.ok:
        raise HTTPException(status_code=422, detail=f"invalid fields: {result.errors}")
    cat_id = max([c.id for c in store.cats], default=0) + 1
    cat = Cat(id=cat_id, **data)
    store.cats.append(cat)
    return _cat_dict(cat)


@app.get("/cats")
def list_cats():
    return [_cat_dict(c) for c in store.cats]


@app.get("/cats/{cat_id}")
def get_cat(cat_id: int):
    return _cat_dict(_cat_or_404(cat_id))


@app.post("/cats/{cat_id}/care", status_code=201)
def add_care(cat_id: int, entry: CareEntryIn):
    _cat_or_404(cat_id)
    try:
        saved = add_entry(cat_id, kind=entry.kind, date=entry.date,
                          note=entry.note, end_date=entry.end_date)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"cat_id": saved.cat_id, "kind": saved.kind, "date": saved.date,
            "note": saved.note, "end_date": saved.end_date}


@app.get("/cats/{cat_id}/care")
def get_care(cat_id: int):
    _cat_or_404(cat_id)
    return [{"kind": e.kind, "date": e.date, "note": e.note, "end_date": e.end_date}
            for e in timeline(cat_id)]


@app.post("/applications", status_code=201)
def create_application(data: ApplicationIn):
    _cat_or_404(data.cat_id)
    application_id = max([a.id for a in store.applications], default=100) + 1
    application = Application(
        id=application_id, cat_id=data.cat_id, adopter_name=data.adopter_name,
        stage="submitted", stage_since=_dt.date.today().isoformat(),
    )
    store.applications.append(application)
    scheduler.register_application(application)
    return _application_dict(application)


@app.get("/applications")
def list_applications():
    return [_application_dict(a) for a in store.applications]


@app.get("/applications/stuck")
def stuck_applications():
    today = _dt.date.today()
    stuck = []
    for application in store.applications:
        if application.stage != "screening" or not application.stage_since:
            continue
        days = (today - _dt.date.fromisoformat(application.stage_since)).days
        if days > scheduler.STALL_LIMIT_DAYS:
            stuck.append(application)
    scheduler.due_reminders(on=today.isoformat())
    return [_application_dict(a) for a in stuck]


@app.get("/applications/{application_id}")
def get_application(application_id: int):
    return _application_dict(_application_or_404(application_id))


@app.post("/applications/{application_id}/move")
def move_application_endpoint(application_id: int, data: MoveIn):
    application = _application_or_404(application_id)
    try:
        move_application(application, data.stage, outcome=data.outcome)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _application_dict(application)


@app.post("/applications/{application_id}/close")
def close_application_endpoint(application_id: int, data: CloseIn):
    application = _application_or_404(application_id)
    try:
        close_application(application, outcome=data.outcome)
    except WorkflowError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _application_dict(application)


@app.get("/search")
def search_cats(has_dog: bool = False, has_children: bool = False):
    profile = AdopterProfile(has_dog=has_dog, has_children=has_children)
    return [_cat_dict(c) for c in filtered_search(store.cats, profile)]


@app.get("/match")
def match_cats(has_dog: bool = False, has_children: bool = False,
               temperament: str | None = None):
    """Ranked matches. When the model is offline, fall back to filtered
    search with no error, per requirement R7."""
    profile = AdopterProfile(
        has_dog=has_dog, has_children=has_children,
        preferred_temperament=temperament,
    )
    if app.state.model_offline:
        return {"fallback": True,
                "cats": [_cat_dict(c) for c in filtered_search(store.cats, profile)]}
    from app.matching.scoring import rank
    try:
        ranked = rank(profile, store.cats)
    except Exception:
        return {"fallback": True,
                "cats": [_cat_dict(c) for c in filtered_search(store.cats, profile)]}
    return {"fallback": False, "ranked": [
        {"cat": _cat_dict(entry.cat), "score": entry.score, "reason": entry.reason}
        for entry in ranked
    ]}


@app.get("/dashboard")
def dashboard():
    result = compute_metrics(store.shelter())
    return {
        "cats_in_shelter": result.cats_in_shelter,
        "average_stay_days": result.average_stay_days,
        "adoption_rate": result.adoption_rate,
        "longest_waiting": [_cat_dict(c) for c in result.longest_waiting],
    }


@app.post("/reminders", status_code=201)
def create_reminder(data: ReminderIn):
    cat = _cat_or_404(data.cat_id)
    reminder = scheduler.schedule(cat, kind=data.kind, due=data.due)
    return _reminder_dict(reminder)


@app.get("/reminders/due")
def reminders_due(on: str):
    return [_reminder_dict(r) for r in scheduler.due_reminders(on=on)]


@app.get("/reminders/overdue")
def reminders_overdue(on: str):
    return [_reminder_dict(r) for r in scheduler.overdue_reminders(on=on)]


@app.post("/reminders/{reminder_id}/acted")
def reminder_acted(reminder_id: int):
    try:
        reminder = scheduler.mark_acted(reminder_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="reminder not found")
    return _reminder_dict(reminder)


@app.post("/admin/model-offline")
def set_model_offline(data: ModelOfflineIn):
    app.state.model_offline = data.offline
    return {"model_offline": app.state.model_offline}
