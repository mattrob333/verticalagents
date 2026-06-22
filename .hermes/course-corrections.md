# Course Corrections — Outer Loop → Inner Loop

The OUTER loop appends prioritized directives here when it detects drift, guardrail violations, quality regressions, or off-task work. The INNER loop reads this FIRST every tick and resolves OPEN corrections as top priority before normal work.

**Protocol:**
- Outer APPENDS corrections as OPEN; never edits build-state.md (avoids write races).
- Inner addresses each OPEN item, then marks it RESOLVED (commit <sha>) and moves it to Resolved.
- Severity: BLOCKER (stop normal work, fix now) · HIGH (this tick) · MEDIUM (within 2 ticks) · LOW (when convenient)

---

## Open Corrections

_(none — all Phase 0 audit corrections resolved)_

---

## Resolved Corrections

### [HIGH] No quality gate exists — RESOLVED (55c5757)
**Fix:** Added `pyproject.toml` with pytest/mypy/ruff config (lenient legacy baseline), `tests/test_smoke.py` (5 passing smoke tests). All three tools functional: `pytest --version`, `mypy --version`, `ruff --version` work. `mypy core/orchestrator/` identifies 6 pre-existing issues without crashing. Legacy code not refactored per directive.

### [HIGH] No requirements.txt — RESOLVED (55c5757)
**Fix:** AST import analysis showed only `PyYAML` is actually imported at top level (claude_agent_sdk/anthropic/firecrawl appear only in string literals and docs). Added `requirements.txt` with PyYAML>=6.0,<7.0 and dev deps in `pyproject.toml [project.optional-dependencies.dev]`. `uv pip install -e ".[dev]"` succeeds.

### [MEDIUM] Inspect agents/construction-rfq/src/agent/ — RESOLVED (audit)
**Finding:** Contains `persona.xml` (9.3K — full BidPro persona with worldview, expertise, conversational style, quirks, flexibility) and `system-prompt.md` (6.9K — complete RFQ agent system prompt with workflow, tools, escalation triggers). This is a **spec/persona design** — NOT a running agent. No executable code, no Next.js app, no deployed runtime.
**Implication:** The port to Hermes means converting persona.xml → Hermes skill file, and system-prompt.md → Hermes system prompt + MCP tool config. The factory's specification phase is producing the right artifacts — the output format just needs to change from Claude SDK to Hermes profile.

### [LOW] .gitignore missing — RESOLVED (55c5757)
**Fix:** Added standard Python+Node `.gitignore` covering `__pycache__/`, `.env`, `node_modules/`, `.venv/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, and generated agent output dirs.