# PawMatch test results

Recorded from real runs. Nothing here is claimed without running it.
Run from `backend/` with the project virtual environment active.

## Commands and results

```sh
cd backend
python -m pytest tests/unit -q
python -m pytest tests/system -q
python -m pytest tests/ -q
python -m pytest tests/ --cov=app --cov-report=term-missing -q
```

| Suite | Result |
|---|---|
| Unit tests (8 units) | 41 passed in 1.67s |
| System tests (TC1 to TC9) | 9 passed, 1 warning in 0.56s |
| Full suite | 50 passed, 1 warning in 2.31s |

System tests: TC1 intake age missing blocked, TC2 complete intake creates
the profile, TC3 vaccination on the timeline, TC4 finalize before meet
and greet blocked with the missing stage named, TC5 ranking for an
adopter with a dog, TC6 dashboard counts match the seed data, TC7 unacted
reminder overdue, TC8 stuck application listed with a reminder created,
TC9 model offline falls back to filtered search with no error.

## Stay risk model, held-out check

40 fixed historical cats, never used in training: accuracy 0.625 against
a 0.550 majority-class baseline. The model beats the baseline, with a
thin margin (3 cats). The training set is 400 synthetic records, seed 7;
the held-out set uses seed 20261025.

## Coverage

Total line coverage 90 percent (556 statements, 56 missed), which meets
the project gate of 90 percent. Per file:

| File | Cover |
|---|---|
| app/adopters/schemas.py | 100% |
| app/adopters/search.py | 94% |
| app/adoptions/workflow.py | 85% |
| app/care/timeline.py | 89% |
| app/errors.py | 100% |
| app/intake/schemas.py | 100% |
| app/intake/validation.py | 93% |
| app/main.py | 85% |
| app/matching/scoring.py | 100% |
| app/matching/stay_risk.py | 96% |
| app/matching/train_model.py | 66% |
| app/metrics/dashboard.py | 100% |
| app/models.py | 100% |
| app/reminders/scheduler.py | 95% |
| app/seed.py | 89% |
| app/store.py | 100% |

Shortfall, stated honestly: workflow (85%) and timeline (89%) are below
90 percent because their defensive error branches have no specified
test, for example an invalid date format, an unknown stage, and closing
an already finalized application. The training script (66%) is run once
to produce model.pkl, not covered by the unit suite. No test was added
just to raise these numbers; the 41 unit tests are the specified set.

## Warnings

1 warning in the full run: a DeprecationWarning from Starlette's
TestClient about the anyio BlockingPortal alias. It comes from the
Starlette library, not from PawMatch code.

## Environment notes

- Python 3.12.3 here; the environment document lists 3.12.4.
- pytest-freezegun 0.4.2 is not installed: it imports `distutils`,
  removed in Python 3.12, and breaks pytest collection. Tests use the
  local `freezer` fixture in `backend/tests/conftest.py`, built on
  freezegun 1.5.1 directly, with the same `move_to` interface.

## Live smoke test (uvicorn)

Started with `uvicorn app.main:app --port 8123` and checked by curl:

- GET /health returned `{"status": "ok"}`.
- GET /dashboard returned cats_in_shelter 6, average_stay_days 12.5,
  adoption_rate 0.8, longest waiting first Pepper.
- GET /match?has_dog=true&temperament=calm returned Pepper first.
- POST /cats with the age field missing returned 422.

## Frontend

`cd web && npm install && npm run build` passes: `tsc && vite build`,
30 modules transformed, built in 1.11s. Note: `npm ci` does not work
until a lockfile exists; `npm install` created `package-lock.json`.

## Releases

- v1.0.0: 32 unit tests, system tests TC1 to TC4 and TC6 to TC8 passing.
- v2.0.0: full suite, 41 unit tests and 9 system tests passing.
- The frontend and the lifespan startup seeding were added after the
  v2.0.0 tag, on main, and are not in the tagged commit.
