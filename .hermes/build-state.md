# Build State: Vertical Agent Factory → Hermes Vertical Forge

**Spec source:** README.md, PLAYBOOK.md, CLAUDE.md
**Repo:** https://github.com/mattrob333/verticalagents
**Workspace:** ~/verticalagents
**Status:** 🏗️ Phase 1 in progress — quality gate established, next: Hermes profile template

## Architecture: Two-Tier Build Loop
- Inner Loop (cron TBD) — every 10m: Check → Test → Advance → Repeat. Self-pauses both crons at a genuine stopping point.
- Outer Loop (cron TBD) — every 60m: active supervisor (audits + writes corrections + trivial fixes + escalation).

## Current State Assessment

### What's here (real working code):
- **Core orchestrator** (`core/orchestrator/`): Factory agent with 4 phases (discovery 9.6K, specification 30K, scaffold 28.8K, delivery 48.9K) = ~117K Python
- **Prompt generator** (`factory/generators/prompt_generator.py`): Dual-mode prompt engine with PersonaConfig, OnboardingState, DualModePromptGenerator
- **CLI tool** (`tools/new-vertical.py`): Project scaffolding
- **Dual-mode system prompt** (`core/meta-prompts/dual-mode-agent.xml`): Full XML template with identity, mode router, onboarding states, MCP tools
- **Next.js app template** (`factory/templates/agent-app/`): package.json, configs
- **Construction RFQ** (`verticals/construction-rfq/`): VERTICAL.md + persona.md (specs only, no deployed agent)
- **Construction RFQ agent** (`agents/construction-rfq/`): Has src/agent/ directory — needs inspection

### What's just documentation (stubs/plans):
- `core/a2ui-components/` — README only
- `core/prometheus/PROMETHEUS.md` — doc only
- `core/persona-architect/PERSONA-ARCHITECT.md` — doc only
- `knowledge/pricing-models/` — README only
- `.claude/commands/build-agent.md` — Claude Code slash command (stub)

### Dependencies:
- Python: `claude_agent_sdk`, `pyyaml`, `anthropic`, `firecrawl` (per imports)
- Node.js: Next.js 14, React, Tailwind, A2UI components
- No requirements.txt or package.json at repo root
- No tests anywhere

### Key insight from reconnaissance:
The **factory concept is excellent** — factory-of-factories for vertical SMB agents. But it's built entirely for the Claude Agent SDK era (2025). The opportunity is to re-imagine it as a **Hermes-native agent forge** that self-builds via the autonomous two-tier loop.

## Creative Modernization Vision: "Hermes Vertical Forge"

### Thesis
The factory should build **Hermes agent profiles**, not Claude SDK agents. Each vertical agent becomes a deployable Hermes profile with:
- Its own skills/ directory (persona expertise)
- Its own MCP tool configurations (integrations)
- Its own system prompt (dual-mode XML → Hermes system prompt format)
- Its own Telegram/Web gateway configuration
- Optional Pedigree sandbox manifest

### The meta-twist
The **factory itself becomes a Hermes agent** — the two-tier autonomous loop. You feed it a vertical description, and it autonomously discovers, specs, builds, tests, and deploys the agent. No more manual `build-agent` slash commands. The loop is the factory.

### What this repo becomes
```
HERMES VERTICAL FORGE (two-tier autonomous build loop)
├── core/                          # Factory engine (existing code, adapted)
│   ├── orchestrator/              # Phase agents → convert to skill format
│   ├── meta-prompts/              # Persona engine (keep, adapt output format)
│   └── skills/                    # Hermes-native skills for agent construction
├── hermets-profiles/              # OUTPUT: Generated Hermes agent profiles
│   ├── personal-injury-law/
│   │   ├── skills/               # Persona skills
│   │   ├── config.yaml           # Hermes agent config
│   │   ├── system-prompt.md      # Dual-mode prompt
│   │   └── mcp-config.yaml       # Tool integrations
│   └── veterinary-clinic/
│       └── ...
├── .hermes/
│   ├── build-state.md             # Builder's state (this file)
│   └── course-corrections.md      # Supervisor's channel
└── docs/
    ├── NEXT_STEPS_PLAN.md         # Phased roadmap
    └── TASKS.md                   # Task board
```

## Phases / Waves

### Phase 1: Foundation — Make it Work (current)
- [ ] Convert factory from Claude SDK to Hermes profile generation
- [ ] Port construction-rfq as first Hermes vertical agent proof-of-concept
- [ ] Create agent profile template with skills/, config.yaml, mcp-config.yaml
- [ ] Get the dual-mode persona system exporting Hermes-compatible prompts
- [x] Set up quality gate (Python tests, type checks) — pytest 5 passing, mypy+ruff functional
- [x] Reconnaissance complete

### Phase 2: Self-Building Factory
- [ ] Make the factory run as a two-tier autonomous loop
- [ ] Inner builder: vertical spec → complete Hermes profile
- [ ] Outer supervisor: validates quality, market alignment
- [ ] Auto-discover phases (web research → spec → build → test)

### Phase 3: Multi-Channel Agents
- [ ] Each generated agent gets Telegram gateway + web UI
- [ ] MCP tool integrations auto-wired
- [ ] Cron-based resident tasks per vertical (daily reminders, follow-ups)

### Phase 4: Marketplace & Scale
- [ ] Agent profile distribution format (shareable Hermes packages)
- [ ] Pedigree sandbox manifests for enterprise deployment
- [ ] Multi-tenant agent hosting

## Completed Tasks
- [x] Repo cloned and analyzed
- [x] Full structural reconnaissance completed
- [x] Creative vision documented

## Open Issues / Blockers
- Pre-existing ruff/mypy issues in legacy code (162 ruff, 6 mypy) — baseline, will be addressed during port

## Next Action
- **Task 1.6: Design the Hermes agent profile template** at `hermes-profiles/_template/` — the output format the factory will generate. Include `skills/`, `config.yaml`, `mcp-config.yaml`, `system-prompt.md`, `gateway.yaml`. This is the target structure that tasks 1.7–1.10 will produce.

## Quality Gate (established)
- `pytest` — 5 smoke tests passing (`tests/test_smoke.py`)
- `mypy` — functional, 6 pre-existing issues in core/orchestrator/ (legacy, not refactored)
- `ruff` — functional, 162 pre-existing issues (legacy code with embedded Next.js strings)
- Run: `. .venv/bin/activate && pytest && ruff check . && mypy core/orchestrator/`
- venv: `.venv/` (uv-managed), install: `uv pip install -e ".[dev]"`

## Pitfalls / Notes for Future Ticks
- The CLI tool `new-vertical.py` has full scaffolding logic — don't rewrite, adapt
- The dual-mode persona system (worldview, expertise, conversational style, flexibility) is genuinely valuable — preserve and enhance
- The factory config YAML is excellent — make Hermes-aware
- Commit each green slice before starting the next file

**Last Updated:** 2026-06-22 — Phase 1 quality gate established (commit 55c5757), all open corrections resolved