# Changelog

## Unreleased

- Project scaffold: shared models, error types, pinned requirements,
  environment example, README.

## v1.0.0

- Shelter operations core: intake validation, care timeline, adoption
  workflow, adopter search, shelter metrics, reminders and follow-ups.
- FastAPI app wiring the units together, with seed data.
- 32 unit tests passing. System tests TC1 to TC4 and TC6 to TC8 passing.
  TC5 needs Version 2 matching, TC9 needs the model fallback; both are
  covered in v2.0.0.

## v2.0.0 (to be tagged when the Version 2 system test passes)

- Compatibility scoring with plain language reasons, and stay risk
  prediction with the 0.70 flag threshold.
