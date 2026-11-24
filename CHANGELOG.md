# Changelog

## Unreleased

- Project scaffold: shared models, error types, pinned requirements,
  environment example, README.
- CORS fix: allow the React frontend origin (localhost:5173 and
  127.0.0.1:5173) to call the API, so the cat list loads in a real
  browser instead of coming up empty.
- UI redesign, Apple style: sticky nav, hero, shelter stat cards, cat
  cards with temperament pills, and a match card with score bars and
  reasons. Temperament picker added to the match search.

## v1.0.0

- Shelter operations core: intake validation, care timeline, adoption
  workflow, adopter search, shelter metrics, reminders and follow-ups.
- FastAPI app wiring the units together, with seed data.
- 32 unit tests passing. System tests TC1 to TC4 and TC6 to TC8 passing.
  TC5 needs Version 2 matching, TC9 needs the model fallback; both are
  covered in v2.0.0.

## v2.0.0

- Compatibility scoring with plain language reasons, and stay risk
  prediction with the 0.70 flag threshold.
- Stay risk model: logistic regression trained on 400 synthetic shelter
  records (features age, shy, senior), saved as model.pkl.
- Full suite: 41 unit tests and 9 system tests passing. Held-out
  accuracy 0.625 against a 0.550 majority baseline (40 cats).
- Total line coverage 90 percent, meeting the project gate.
