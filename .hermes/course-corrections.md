# Course Corrections — Outer Loop → Inner Loop

The OUTER loop appends prioritized directives here when it detects drift, guardrail violations, quality regressions, or off-task work. The INNER loop reads this FIRST every tick and resolves OPEN corrections as top priority before normal work.

**Protocol:**
- Outer APPENDS corrections as OPEN; never edits build-state.md (avoids write races).
- Inner addresses each OPEN item, then marks it RESOLVED (commit <sha>) and moves it to Resolved.
- Severity: BLOCKER (stop normal work, fix now) · HIGH (this tick) · MEDIUM (within 2 ticks) · LOW (when convenient)

---

## Open Corrections

### [HIGH] No quality gate exists — OPEN (Phase 0 audit)
**Problem:** The repo has no tests, no type checking, no lint configuration, no requirements.txt. The builder needs a quality gate to commit against, but there's nothing to run.
**Required fix:** Add a basic Python quality gate: pyproject.toml with pytest, mypy, ruff config + a requirements.txt capturing existing imports (claude_agent_sdk, pyyaml, anthropic, etc.). Do NOT refactor code — just add the infrastructure so subsequent ticks can run checks.
**Acceptance:** `pytest --version`, `mypy --version`, `ruff --version` all work, and running `mypy core/orchestrator/` at least identifies existing issues without crashing.

### [HIGH] No requirements.txt — OPEN (Phase 0 audit)
**Problem:** Python dependencies (claude_agent_sdk, pyyaml, anthropic, firecrawl) are scattered across imports with no lockfile. New builders and CI can't install deps.
**Required fix:** Generate a `pyproject.toml` or `requirements.txt` from the existing imports discovered in Python files. Pin reasonable versions. Do NOT change any code.
**Acceptance:** `pip install -r requirements.txt` installs without errors.

### [MEDIUM] Inspect agents/construction-rfq/src/agent/ — RESOLVED (audit)
**Finding:** Contains `persona.xml` (9.3K — full BidPro persona with worldview, expertise, conversational style, quirks, flexibility) and `system-prompt.md` (6.9K — complete RFQ agent system prompt with workflow, tools, escalation triggers). This is a **spec/persona design** — NOT a running agent. No executable code, no Next.js app, no deployed runtime.
**Implication:** The port to Hermes means converting persona.xml → Hermes skill file, and system-prompt.md → Hermes system prompt + MCP tool config. The factory's specification phase is producing the right artifacts — the output format just needs to change from Claude SDK to Hermes profile.

### [LOW] .gitignore missing — OPEN (Phase 0 audit)
**Problem:** No .gitignore at repo root. Generated artifacts and __pycache__ could get committed.
**Required fix:** Add a standard Python+Node .gitignore.
**Acceptance:** `__pycache__/`, `.env`, `node_modules/`, `.venv/` are all ignored.

---

## Resolved Corrections
_(none yet — first audit)_