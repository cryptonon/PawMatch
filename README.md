# PawMatch

A smart cat adoption tracker for shelters. Version 1 tracks each cat from
intake to adoption. Version 2 ranks cats for each adopter and flags cats
likely to wait too long.

## Repository

GitHub repository URL to be added. The instructor gets read access.
One repository, one main branch, protected. All work happens on feature
branches merged by pull request. A merge needs passing tests and a
changelog entry. Releases are tagged v1.0.0 and v2.0.0.

## Stack

TypeScript and React (Vite) for the frontend, Python and FastAPI for the
backend, SQLite for development and PostgreSQL for deployment, scikit-learn
for the Version 2 stay risk model.

## Setup

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload   # API at http://localhost:8000
```

Frontend:

```sh
cd web
npm ci
npm run dev   # app at http://localhost:5173
```

## Tests

```sh
cd backend
pytest tests/unit                      # 41 unit tests across 8 units
pytest tests/unit --cov=app --cov-report=term-missing   # project gate: 90% line coverage
pytest tests/system                    # 9 system tests, TC1 to TC9
pytest tests/                          # full suite
```

See `backend/TEST_RESULTS.md` for the latest recorded run.
See `CHANGELOG.md` for what changed in each version.
