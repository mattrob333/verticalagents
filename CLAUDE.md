# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vertical Agent Factory is Tier 4 Intelligence's internal toolkit for rapidly building, marketing, and shipping vertical AI agents to SMBs. The system takes a natural language description of an industry vertical and scaffolds a complete deployable product with onboarding UI, data collection, agent logic, and marketing assets.

**Business model**: Build niche AI agents for specific SMB workflows (RFQ processing, scheduling, intake forms), price at $200-800/month, target 10+ verticals with 10+ clients each.

## Architecture

```
Factory Input (industry description)
    ↓
Research Phase (Claude Agent SDK → VERTICAL.md spec)
    ↓
Persona Generation (Prometheus v3.3 → persona.md)
    ↓
Scaffold Phase (A2UI components, onboarding flows, tools)
    ↓
Deploy (Vercel/Railway, Stripe, email integration)
```

### Core Systems

- **Prometheus v3.3** (`core/prometheus/PROMETHEUS.md`): Meta-prompt persona builder that generates agent system prompts from vertical specs. Uses structured output format with skill chains, perspectives, and tool definitions.

- **Expert Persona Architect v2.0** (`core/persona-architect/PERSONA-ARCHITECT.md`): Creates "thinking partner" personas (not task executors). Personas have worldviews, deep/working knowledge, curiosity edges, and conversational flexibility.

- **Master Factory Prompt** (`factory/prompts/master-factory-prompt.md`): Orchestrates the full generation pipeline from input spec to deployable agent with marketing assets.

### Key Directories

- `verticals/`: Per-vertical implementations. Each vertical contains `VERTICAL.md` (spec), `persona.md` (system prompt), `onboarding/`, `integrations/`, `marketing/`
- `verticals/_template/`: Clone this to start a new vertical
- `agents/`: Deployed agent implementations (e.g., `construction-rfq/` is a complete Next.js app)
- `core/skills/`: Claude Code skills for research, building, onboarding
- `tools/`: CLI utilities for scaffolding and generation

## Commands

### Create a new vertical
```bash
# From template
python tools/new-vertical.py --name "veterinary clinics"

# Clone existing vertical
python tools/new-vertical.py --name "auto-repair" --clone "veterinary-clinics"

# With discovery mode (triggers research)
python tools/new-vertical.py --name "construction" --discover

# List all verticals
python tools/new-vertical.py --list
```

### Generate persona from spec
```bash
python tools/generate-persona.py verticals/[vertical-name]/VERTICAL.md
```

### Agent apps (Next.js)
```bash
cd agents/[agent-name]
npm install
npm run dev          # Development server
npm run build        # Production build
```

## Vertical Development Workflow

1. **Research**: Create `VERTICAL.md` using the template. Focus on ONE specific workflow to automate.

2. **Generate Persona**: Feed spec to Prometheus to get `persona.md`. The persona should be a thinking partner with opinions, not just a task executor.

3. **Define Onboarding**: What info does the agent need? What integrations connect? (see `onboarding/flow.yaml` pattern in PLAYBOOK.md)

4. **Build Agent**: Implement tools in MCP format, create system prompt with template variables (`{{company_name}}`, `{{markup_percentage}}`), wire up integrations.

5. **Ship**: Generate marketing assets, deploy to Vercel/Railway, set up Stripe billing.

## Key Concepts

### Persona Design Principles
- Personas are **thinking partners**, not task executors
- They have worldviews (opinions, things they find beautiful/cringe)
- They adapt to user intent (brainstorm vs. teach vs. build)
- Boot-up should feel like meeting someone, not activating a service

### Vertical Selection Criteria (score 1-5 each)
- Repetitive workflow (rule-based, daily/weekly)
- High time cost (10+ hours/week admin work)
- Non-technical owners (won't DIY with Zapier)
- Willingness to pay ($500+/month is normal)
- Low integration complexity (standard CRM/calendar)
- Low regulatory constraints (avoid HIPAA/finance initially)

### Pricing Formula
Price at 10-20% of value delivered. Calculate: `Time saved × Hourly rate × 52 weeks = Annual value`

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Runtime | Claude Agent SDK |
| Persona Engine | Prometheus v3.3 / Expert Persona Architect v2.0 |
| UI Framework | A2UI (Next.js 14) |
| LLM | Claude API (claude-sonnet-4-20250514 for speed) |
| Database | Supabase (pgvector for RAG) |
| Auth | Clerk / NextAuth |
| Payments | Stripe |
| Deployment | Vercel / Railway |
| Voice (optional) | ElevenLabs / Vapi |

## File Patterns

### VERTICAL.md structure
```yaml
---
vertical: slug-name
status: research | draft | building | pilot | live
created: YYYY-MM-DD
confidence: low | medium | high
---
```
Contains: Market Overview, Target Workflow (current/desired state), Agent Scope, Integration Requirements, Pricing Model, Competition, Risk Assessment, Recommendation.

### Agent system prompts
Use template variables: `{{company_name}}`, `{{labor_rate}}`, `{{markup_percentage}}`, etc. Define tools, escalation triggers, and response formats.

### Onboarding flows
YAML format with steps, fields (text, select, secret, phone), and actions. See `PLAYBOOK.md` for schema.

## Current Verticals

- `construction-rfq/`: RFQ processing for contractors (most developed example)
- Check `verticals/` for other in-progress verticals
