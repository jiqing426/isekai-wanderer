# Git Commit Convention

## Commit Message Format

```
<type>(<scope>): <subject>

<body>
```

### Type

| Type | Description |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs` | Documentation only changes |
| `test` | Adding or correcting tests |
| `chore` | Build, CI, tooling, or dependency changes |
| `cleanup` | Code cleanup, file moves, dead code removal |

### Scope

Use the module or CR ID: `backend`, `frontend`, `admin`, `workflow`, `docs`, `CR-XXX`.

### Rules

1. **One logical change per commit** — don't mix unrelated changes.
2. **Commit early and often** — avoid giant "全量提交" commits.
3. **Subject line** — imperative mood, ≤72 chars, no period at end.
4. **Body** — explain *why*, not *what*. Use bullet points.
5. **Never commit** — `.env`, credentials, `*.db`, `login_data.json`, secrets.

### Examples

```
cleanup: move root-level test scripts to tests/legacy/

47 test_*.py, verify_*.py, qa_*.py files were scattered in the project
root. Moved to tests/legacy/ with a README explaining they are historical
scripts not part of the active test suite.

chore(security): harden mock middleware for production safety

- Mock middleware now checks APP_ENV=production in addition to DISABLE_MOCK
- mock_data.py is not imported when mock is disabled
- MockMiddleware registration in main.py is conditional
```
