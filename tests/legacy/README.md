# Legacy Test Scripts

This directory contains historical test and verification scripts from early development (CR-008 through CR-024).

These scripts were moved here from the project root during engineering cleanup on 2026-09-20. They are **not part of the active test suite** — the current tests live in:

- `backend/tests/unit/` — backend unit tests
- `backend/tests/integration/` — backend integration tests
- `tests/e2e/` — Playwright browser E2E tests
- `tests/api/` — API contract tests
- `tests/db/` — database migration tests

These legacy scripts are retained for reference but should not be run as part of CI.
