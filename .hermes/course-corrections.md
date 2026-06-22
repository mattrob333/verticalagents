# Course Corrections — Outer Loop → Inner Loop

The OUTER loop appends prioritized directives here when it detects drift, guardrail violations, quality regressions, or off-task work. The INNER loop reads this FIRST every tick and resolves OPEN corrections as top priority before normal work.

**Protocol:**
- Outer APPENDS corrections as OPEN; never edits build-state.md (avoids write races).
- Inner addresses each OPEN item, then marks it RESOLVED (commit <sha>) and moves it to Resolved.
- Severity: BLOCKER (stop normal work, fix now) · HIGH (this tick) · MEDIUM (within 2 ticks) · LOW (when convenient)

---

## Open Corrections

### [HIGH] Persona SKILL.md emits every section duplicated — OPEN (audit 2026-06-22T14:30Z)
**Problem:** The generated `hermes-profiles/construction-rfq/skills/construction-rfq-persona/SKILL.md` (commit 28d78bd, produced by `ScaffoldPhase.scaffold_hermes_profile` → `DualModePromptGenerator.generate_hermes_persona_skill`) contains every persona subsection TWICE. Evidence from the file on disk:
- `### Core Beliefs` appears at lines 35 AND 58; `### What They Find Beautiful` at lines 42 AND 51; `### What Makes Them Cringe` at 45 AND 54; `### Influences` at 48 AND 57.
- `### Deep Mastery` at lines 64 AND 65; `### Working Knowledge` at 71 AND 82; `### Curiosity Edges` at 77 AND 88.
- `### How They Talk` at lines 97 AND 98; `### Quirks` at 101 AND 114; `### Flexibility` appears THREE times (lines 107, 120, 123).

This is the crown-jewel persona output (guardrail #1: "Persona system must never be damaged or removed"). The system-prompt.md is NOT affected — only SKILL.md.

**Root cause:** `factory/generators/prompt_generator.py` `_inject_persona_sections` (line 679) replaces `{{persona_worldview_core_beliefs}}` with `self._render_hermes_worldview(persona)`, which returns the FULL worldview block INCLUDING all four sub-headings (`### Core Beliefs`, `### What They Find Beautiful`, `### What Makes Them Cringe`, `### Influences`). But the template `hermes-profiles/_template/skills/persona-template/SKILL.md` already has those four sub-headings hardcoded, EACH followed by its own granular placeholder (`{{persona_worldview_beautiful}}`, `{{persona_worldview_cringe}}`, `{{persona_worldview_influences}}`) — which `_inject_persona_sections` ALSO fills. Same collision for expertise (`_render_hermes_expertise` returns full block incl. `### Deep Mastery`/`Working Knowledge`/`Curiosity Edges` headings, but template already has those headings + granular placeholders) and style (`_render_hermes_style` returns `### How They Talk`/`### Quirks`/`### Flexibility` block, template already has them). Net: each block is emitted once by the full-render placeholder and again by the granular placeholders.

**Required fix:** Pick ONE rendering strategy and make template + injector consistent. Recommended: make the template use ONLY the three full-block placeholders (`{{persona_worldview_core_beliefs}}`, `{{persona_expertise_deep}}`, `{{persona_style_how_they_talk}}`) and REMOVE the hardcoded sub-headings + granular placeholders from the template. Then `_inject_persona_sections` only needs to fill those three (the granular replacements become dead code — remove them). Do NOT touch `_render_hermes_worldview`/`_render_hermes_expertise`/`_render_hermes_style` themselves. After fixing, regenerate the construction-rfq profile (re-run `tools/build_hermes_profile.py`) so the on-disk SKILL.md is corrected.

**Acceptance:**
- Each of `### Core Beliefs`, `### What They Find Beautiful`, `### What Makes Them Cringe`, `### Influences`, `### Deep Mastery`, `### Working Knowledge`, `### Curiosity Edges`, `### How They Talk`, `### Quirks`, `### Flexibility` appears EXACTLY ONCE in `hermes-profiles/construction-rfq/skills/construction-rfq-persona/SKILL.md`.
- Add a regression test in `tests/test_hermes_prompt_generator.py` `TestHermesPersonaSkillGeneration` asserting each subsection heading appears exactly once (use `result.count("### Core Beliefs") == 1`, etc.). Current tests only assert substring presence, which is why this shipped green — the test gap must be closed.
- `pytest` stays green (currently 69 passing).

### [MEDIUM] build-state.md is stale — OPEN (audit 2026-06-22T14:30Z)
**Problem:** `.hermes/build-state.md` self-report diverges from reality (drift, criterion 3):
- Line 6: "Status: Task 1.8 done, next: delivery.py adaptation" — but commits 96630bb (Task 1.9) and 28d78bd (Task 1.10) are already on main. `docs/TASKS.md` shows 1.9 and 1.10 checked off.
- Line 113: "pytest — 49 tests passing" — actual is **69 passed** (verified `pytest -q` this audit).
- Line 110 "Next Action: Task 1.9" — already done.
- Line 115: "ruff — 162 pre-existing issues" — actual is **169** (verified this audit; +7 regression, see LOW below).
The builder must not be trusted to self-report; the supervisor verifies. But the builder owns build-state.md, so update it to reflect: Phase 1 tasks 1.1–1.10 complete, 69 tests, 169 ruff / 6 mypy baseline, next action = Task 1.11 (test profile loads in Hermes CLI) or 1.12 (README branding).

**Required fix:** On the next builder tick, refresh build-state.md: correct the status line, test count (69), ruff count (169), and Next Action (Task 1.11). Do not back-date.

**Acceptance:** build-state.md status line, test count, ruff count, and Next Action match what `git log`, `pytest -q`, and `ruff check .` actually report.

### [LOW] Ruff errors increased 162 → 169 — OPEN (audit 2026-06-22T14:30Z)
**Problem:** Baseline was 162 ruff errors (commit 55c5757). Current `ruff check .` reports **169** (+7). The +7 was introduced by the new Hermes-port code in commits 6cc9a55–28d78bd (prompt_generator.py / scaffold.py / delivery.py / build_hermes_profile.py). Not a blocker — 155 are auto-fixable — but the quality gate should not silently drift upward.

**Required fix:** Run `ruff check --fix .` (155 auto-fixable), review the diff, commit as `chore(ruff): auto-fix lint`. For the remaining ~14, either fix manually or add targeted `# noqa` with justification. Re-baseline the ruff count in build-state.md.

**Acceptance:** `ruff check .` error count ≤ 162 (the original baseline) and build-state.md ruff count matches reality.

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