# Vertical Agent Factory

**Tier 4 Intelligence's internal toolkit for rapidly building, marketing, and shipping vertical AI agents to SMBs.**

> Build once, ship many. Each vertical agent = $10K-$50K ARR.

## The Business Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        VERTICAL AGENT FACTORY                           │
├─────────────────────────────────────────────────────────────────────────┤
│  1. DISCOVER    │  2. BUILD      │  3. SHIP       │  4. SCALE          │
│  ───────────    │  ─────────     │  ────────      │  ─────────         │
│  Research niche │  Use toolkit   │  Demo to SMBs  │  Clone & repeat    │
│  Map pain points│  Generate agent│  Onboard fast  │  Templating        │
│  Size market    │  Test flows    │  Collect $$$   │  Multi-vertical    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Repo Structure

```
vertical-agent-factory/
├── README.md                          # You are here
├── PLAYBOOK.md                        # Step-by-step guide to ship a vertical
│
├── core/                              # Shared infrastructure
│   ├── persona-architect/             # Expert Persona Architect v2.0
│   │   ├── PERSONA-ARCHITECT.md       # Thinking partner persona generator
│   │   └── examples/                  # Generated persona examples
│   │
│   ├── skills/                        # Claude Code skills
│   │   ├── vertical-research/         # Discovery & market research skill
│   │   ├── agent-builder/             # Spec → Agent generation skill
│   │   ├── onboarding-flow/           # User onboarding wizard skill
│   │   └── voice-agent/               # Voice AI integration skill
│   │
│   ├── a2ui-components/               # Reusable A2UI components
│   │   ├── chat-interface/            # Standard chat widget
│   │   ├── dashboard-shell/           # NotebookLM-style dashboard
│   │   ├── onboarding-wizard/         # Multi-step intake forms
│   │   ├── artifact-viewer/           # Rich content display
│   │   └── audio-briefing/            # Voice synthesis player
│   │
│   └── agents/                        # Claude Agent SDK patterns
│       ├── research-agent/            # Vertical discovery agent
│       ├── builder-agent/             # Spec generation agent
│       └── orchestrator/              # Multi-agent coordination
│
├── verticals/                         # Per-vertical implementations
│   ├── _template/                     # Starter template for new verticals
│   │   ├── VERTICAL.md                # Vertical spec document
│   │   ├── persona.md                 # Generated persona prompt
│   │   ├── onboarding/                # Intake flow definitions
│   │   ├── integrations/              # Tool configs (calendars, CRM, etc.)
│   │   └── marketing/                 # Landing page, pitch deck, etc.
│   │
│   ├── personal-injury-law/           # Example: Legal intake agent
│   ├── construction-rfq/              # Example: RFQ processing agent
│   ├── dental-scheduling/             # Example: Patient scheduling agent
│   └── [more verticals...]/
│
├── knowledge/                         # Reference knowledge base
│   ├── industry-playbooks/            # Per-industry research
│   ├── workflow-patterns/             # Common automation patterns
│   ├── integration-catalog/           # API/tool integration docs
│   ├── pricing-models/                # How to price vertical agents
│   └── sales-scripts/                 # Pitch templates
│
└── tools/                             # CLI and automation
    ├── new-vertical.py                # Scaffold a new vertical
    ├── generate-persona.py            # Run Prometheus on a spec
    ├── build-landing-page.py          # Marketing site generator
    └── deploy-agent.py                # Push to production
```

## Quick Start

### 1. Research a New Vertical

```bash
# Use the research agent to analyze a vertical
python tools/new-vertical.py --industry "veterinary clinics" --discover

# Output: verticals/veterinary-clinics/VERTICAL.md with:
# - Market size & dynamics
# - Top pain points (ranked by hours/cost)
# - Existing tools & gaps
# - Recommended agent scope
```

### 2. Generate the Agent Persona

```bash
# Feed the spec to Prometheus
python tools/generate-persona.py verticals/veterinary-clinics/VERTICAL.md

# Output: verticals/veterinary-clinics/persona.md
# A complete system prompt with personality, skills, tone
```

### 3. Build the Onboarding Flow

Use the A2UI components to create the intake wizard:

- What info does the agent need to start?
- What integrations need to connect?
- What does the dashboard look like?

### 4. Ship & Sell

```bash
# Generate marketing assets
python tools/build-landing-page.py verticals/veterinary-clinics/

# Deploy the agent
python tools/deploy-agent.py verticals/veterinary-clinics/ --env production
```

## The Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Agent Runtime | Claude Agent SDK | Multi-tool orchestration |
| Persona Engine | Expert Persona Architect v2.0 | Thinking partner generation |
| UI Framework | A2UI | Chat + artifacts + dashboards |
| Voice Layer | Your existing Voice AI | Phone/voice interactions |
| Skills | Claude Code Skills | Reusable capability packages |

## Target Verticals (Priority Order)

Based on the research, these verticals have:
- High pain (repetitive, rule-based work)
- Willingness to pay ($10K+ not a stretch)
- Non-technical owners (need turnkey solutions)

| Vertical | Agent Focus | Est. Time Saved | Price Point |
|----------|-------------|-----------------|-------------|
| Personal Injury Law | Client intake | 15 hrs/week | $15K/year |
| Construction | RFQ processing | 2 days → 2 hrs | $20K/year |
| Dental Practices | Scheduling | 10 hrs/week | $12K/year |
| HVAC/Plumbing | Dispatch & invoicing | 15 hrs/week | $18K/year |
| Auto Repair | Diagnostic intake | 20 hrs/week | $15K/year |
| Insurance Agencies | Policy renewals | 15 hrs/cycle | $25K/year |
| Real Estate | Listing creation | 10 hrs/listing | $18K/year |

## Revenue Model

```
Year 1 Target: 10 verticals × 10 clients each × $15K avg = $1.5M ARR

Timeline per vertical:
- Week 1: Research & spec
- Week 2: Build & test
- Week 3: Marketing & outreach
- Week 4+: Sales & onboarding
```

## Next Steps

1. [ ] Set up the GitHub repo with this structure
2. [ ] Expert Persona Architect ready in `core/persona-architect/`
3. [ ] Build the first Claude Code skill: `vertical-research`
4. [ ] Create the A2UI dashboard shell
5. [ ] Pick first vertical (Construction RFQ?) and ship it

---

*Built by Tier 4 Intelligence | tier4intelligence.com*
