# Hermes Vertical Forge — Modernization Plan

## The Vision

Transform `verticalagents` from a Claude Agent SDK era factory into a **self-building Hermes agent forge** — a two-tier autonomous loop that takes a vertical description and outputs a complete, deployable Hermes agent profile.

### Why Hermes?
- **Hermes profiles** are self-contained agent configurations with skills, tools, MCP servers, cron jobs, and gateways
- The **two-tier autonomous build loop** makes the factory itself a working product — it builds while you sleep
- **Telegram gateways** give each vertical agent its own direct communication channel with SMBs
- **Pedigree manifests** let enterprise clients run agents in sandboxed environments

### What stays
- The **dual-mode persona architecture** (onboarding state machine + consultation thinking partner)
- The **Prometheus/Persona Architect** philosophy (personas have worldviews, opinions, curiosity edges)
- The **SMB vertical selection criteria** and pricing model
- The **4-phase workflow** (Discover → Specify → Build → Deliver)
- The **factory/output separation** (this repo doesn't contain generated agents)

### What transforms
- **Output format**: Claude SDK agents → Hermes agent profiles (skills/ + config.yaml + MCP config)
- **Build mechanism**: Manual slash commands → autonomous two-tier cron loop
- **Runtime**: Claude API → Hermes (multi-provider, multi-channel)
- **Components**: Next.js A2UI → Telegram gateway + optional web UI
- **Distribution**: Standalone apps → shareable Hermes profile packages

---

## Phase 1: Foundation — Make It Work

**Goal**: Modernize the existing codebase with Hermes-native output while preserving the working factory engine.

### Tasks

1. **Inspect agents/construction-rfq/src/agent/**
   - What's actually there (code vs stub)?
   - Port it as the first Hermes vertical agent profile proof-of-concept

2. **Add quality gate infrastructure**
   - `pyproject.toml` with pytest, mypy, ruff config
   - `requirements.txt` from discovered imports
   - `.gitignore`
   - First passing test

3. **Design Hermes agent profile format**
   - Template: `hermes-profiles/_template/` with:
     - `skills/` — persona prompting, business rules
     - `config.yaml` — Hermes agent profile config (model, provider, system prompt)
     - `mcp-config.yaml` — MCP tool integrations
     - `gateway.yaml` — Telegram/web channel config
   - Generate this from the factory instead of Next.js + Claude SDK

4. **Adapt the prompt generator**
   - `factory/generators/prompt_generator.py` — output Hermes system prompt format instead of Claude SDK agents
   - Keep the dual-mode XML → Hermes-compatible markdown system prompt

5. **Adapt the scaffold phase**
   - `core/orchestrator/phases/scaffold.py` (28.8K) — output Hermes profiles instead of Next.js apps
   - Keep A2UI concept but render via Telegram inline components

6. **Adapt the delivery phase**
   - `core/orchestrator/phases/delivery.py` (48.9K) — generate gateway configs, deployment manifests

### Test: First vertical agent profile built and runnable via Hermes

---

## Phase 2: Self-Building Factory

**Goal**: The factory runs autonomously via the two-tier loop.

### Tasks

1. **Seed the factory-agent.py with Hermes-aware phase agents**
   - Discovery phase: web research → VERTICAL.md
   - Specification phase: VERTICAL.md → Full agent spec + persona
   - Build phase: Spec → Complete Hermes profile
   - Delivery phase: Profile → Deployable (gateway config, deployment manifest)

2. **Inner loop prompt** (see .hermes/build-state.md)
   - Reads current state, advances one phase per tick
   - TDD-first (test the persona, test the tools, test the profile)

3. **Outer loop prompt** (see .hermes/course-corrections.md)
   - Audits generated profiles for quality
   - Checks persona depth, tool definition, market fit
   - Writes corrections when quality slips

---

## Phase 3: Multi-Channel Agents

**Goal**: Generated agents can be deployed and interacted with across channels.

### Tasks

1. **Telegram gateway per profile** — each vertical agent gets its own Telegram chat
2. **Web gateway** — optional web interface for non-Telegram users
3. **Cron-based resident tasks** — daily reminders, follow-ups, check-ins per vertical
4. **MCP tool integrations** — auto-wire common SMB tools (Twilio, SendGrid, Google Calendar, etc.)

---

## Phase 4: Marketplace & Scale

**Goal**: Vertical agents are distributable, deployable to enterprise clients.

### Tasks

1. **Hermes profile package format** — zip up a profile for sharing/selling
2. **Pedigree manifests** — optional sandbox config for clients who want isolation
3. **Multi-tenant hosting** — run N vertical agents from one Hermes gateway
4. **Agent update channel** — push persona improvements to deployed agents
5. **Usage analytics** — track which verticals get traction

---

## Immediate Next Action
**Inspect agents/construction-rfq/src/agent/ for actual code** to understand the state of the only "built" agent and use it as the first Hermes port target.