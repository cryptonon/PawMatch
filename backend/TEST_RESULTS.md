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
| Unit tests (original 8 units) | 41 passed |
| New unit tests (bios, watchlist, capacity, training) | 16 passed |
| System tests (TC1 to TC9) | 9 passed |
| System tests (new features) | 9 passed |
| Full suite | 75 passed, 2 warnings in 5.80s |

System tests: TC1 intake age missing blocked, TC2 complete intake creates
the profile, TC3 vaccination on the timeline, TC4 finalize before meet
and greet blocked with the missing stage named, TC5 ranking for an
adopter with a dog, TC6 dashboard counts match the sample records, TC7 unacted
reminder overdue, TC8 stuck application listed with a reminder created,
TC9 model offline falls back to filtered search with no error.
New system tests: bio draft, approve, publish, and the publish rejection
for a draft over HTTP; watchlist ordering over HTTP; dashboard capacity
fields; API error paths for unknown cat, application, reminder, and bio.

## Stay risk model, held-out check

The model is now trained on the real Austin Animal Center data
(69,309 stays, long stay over 30 days), not on synthetic records.
Logistic regression with balanced class weights, 25 percent stratified
holdout, seed 7. Holdout AUC 0.610, holdout accuracy 0.544, long-stay
rate 0.257. The Austin AUC is below the thesis logistic regression
AUC of 0.673 because PawMatch uses only features a PawMatch cat
carries. Gradient boosting scored higher on Austin (AUC about 0.74)
but its probabilities sit below the 0.5 decision point, so it scored
0.550 on the project's own held-out gate, no better than the baseline,
and was not used.

The specified Unit 6 gate still passes with the Austin model: the
fixed 40-cat held-out fixture scores accuracy 0.575 against a 0.550
majority-class baseline, a thin margin of 1 cat. The old synthetic
model scored 0.625 against the same baseline (3 cats). The Austin
data has no behavior notes, so shyness is not a model input anymore;
that is a stated limit, not a hidden one.

## Coverage

Total line coverage 93 percent (729 statements, 50 missed), which
meets the project gate of 90 percent. Per file:

| File | Cover |
|---|---|
| app/adopters/schemas.py | 100% |
| app/adopters/search.py | 94% |
| app/adoptions/workflow.py | 85% |
| app/bios/drafting.py | 94% |
| app/care/timeline.py | 89% |
| app/errors.py | 100% |
| app/intake/schemas.py | 100% |
| app/intake/validation.py | 93% |
| app/main.py | 91% |
| app/matching/scoring.py | 100% |
| app/matching/stay_risk.py | 97% |
| app/matching/train_model.py | 86% |
| app/metrics/dashboard.py | 100% |
| app/models.py | 100% |
| app/reminders/scheduler.py | 96% |
| app/seed.py | 89% |
| app/store.py | 100% |
| app/watchlist.py | 94% |

Shortfall, stated honestly: workflow (85%) and timeline (89%) are
below 90 percent because their defensive error branches have no
specified test, for example an invalid date format, an unknown stage,
and closing an already finalized application. The remaining gap in
train_model.py is the `__main__` block (lines 155-164), which runs
only when the script is run directly.

## Warnings

2 warnings in the full run, both from libraries, not from PawMatch
code: a DeprecationWarning from Starlette's TestClient about the
anyio BlockingPortal alias, and an OptimizeWarning from scikit-learn
when the tiny-CSV training test runs.

## Environment notes

- Python 3.12.3 here; the environment document lists 3.12.4.
- pytest-freezegun 0.4.2 is not installed: it imports `distutils`,
  removed in Python 3.12, and breaks pytest collection. Tests use the
  local `freezer` fixture in `backend/tests/conftest.py`, built on
  freezegun 1.5.1 directly, with the same `move_to` interface.
- The Austin CSV (16 MB) is read from `~/workspace/thesis/data/` by
  the training script; it is not copied into this repository. Only
  the trained model.pkl is shipped.

## Live smoke test (uvicorn, port 8000)

Started the backend and the built frontend and checked by curl and in
a real browser (Playwright chromium):

- GET /health returned `{"status": "ok"}`.
- GET /dashboard returned cats_in_shelter 6, average_stay_days 12.5,
  adoption_rate 0.8, longest waiting first Pepper, capacity_percent
  75.0, alert null.
- GET /match?has_dog=true&temperament=calm returned Pepper first.
- POST /cats with the age field missing returned 422.
- GET /watchlist returned 6 cats, highest first: Pepper 48%, Oliver
  46%, Bella 45%, Simba 40%, Miso 38%, Luna 37%. No cat is flagged
  on the seed data, which is correct: the highest score is 0.483,
  below the 0.70 flag.
- POST /cats/1/bio/draft, approve, and publish returned draft,
  approved, published in order; publishing a draft returned 400.
- The UI was checked in a real browser: home, match, watchlist, and
  bios sections all render with real data. Screenshots are in
  `~/workspace/your_files/pawmatch-config-management/screenshots/`.
- Two real bugs were caught this way and fixed on their own branches:
  the backend had no CORS rule, so the cat list stayed empty in a
  browser; and the watchlist reason and score disagreed by one point
  for Miso (38% vs 37%) because the API rounded after the reason was
  built. Both are fixed and covered by tests.

## Frontend

`cd web && npm run build` passes: `tsc && vite build`, 31 modules
transformed, built in about 1.2s.

## Releases

- v1.0.0: 32 unit tests, system tests TC1 to TC4 and TC6 to TC8 passing.
- v2.0.0: full suite, 41 unit tests and 9 system tests passing.
- The frontend and the lifespan startup seeding were added after the
  v2.0.0 tag, on main, and are not in the tagged commit.
- v2.1.0: Austin-trained stay risk model, AI-drafted bios, long-stay
  watchlist, capacity alerts. Full suite 75 passed, coverage 93%.
