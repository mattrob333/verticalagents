# Course Corrections — Outer Loop → Inner Loop

The OUTER loop appends prioritized directives here when it detects drift, guardrail violations, quality regressions, or off-task work. The INNER loop reads this FIRST every tick and resolves OPEN corrections as top priority before normal work.

**Protocol:**
- Outer APPENDS corrections as OPEN; never edits build-state.md (avoids write races).
- Inner addresses each OPEN item, then marks it RESOLVED (commit <sha>) and moves it to Resolved.
- Severity: BLOCKER (stop normal work, fix now) · HIGH (this tick) · MEDIUM (within 2 ticks) · LOW (when convenient)

---

## Open Corrections

(none — all resolved 2026-06-22)

---

## Resolved Corrections

### [HIGH] Persona SKILL.md emits every section duplicated — RESOLVED (bf7125e)
**Fix:** Template `hermes-profiles/_template/skills/persona-template/SKILL.md` had both full-block placeholders (rendered with sub-headings) AND hardcoded sub-headings with granular placeholders, causing every persona subsection to appear twice. Fixed by removing hardcoded sub-headings + granular placeholders from the template, leaving only the three full-block placeholders (`{{persona_worldview_core_beliefs}}`, `{{persona_expertise_deep}}`, `{{persona_style_how_they_talk}}`). Added 10 parametrized regression tests asserting each subsection heading appears exactly once. Regenerated construction-rfq profile on disk. All 79 tests pass.

### [MEDIUM] build-state.md is stale — RESOLVED (a4d8eb0)
**Fix:** Refreshed build-state.md: status line now reflects Tasks 1.1–1.10 complete, test count corrected to 79, ruff count corrected to 0, Next Action updated to Task 1.11. Phase 1 checkboxes updated. All values verified against `git log`, `pytest -q`, and `ruff check .`.

### [LOW] Ruff errors increased 162 → 169 — RESOLVED (a4d8eb0)
**Fix:** Ran `ruff check --fix .` which auto-fixed 172 issues. 3 remaining F841 (unused local variables) in legacy `specification.py` suppressed with targeted `# noqa: F841` + justification. `ruff check .` now passes clean (0 errors, down from 169).

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