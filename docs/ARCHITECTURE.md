# Vertical Agent Factory — Architecture

## Overview

A meta-system for rapidly building, deploying, and selling vertical AI agents to SMBs. You describe a scenario → the system scaffolds a deployable product with onboarding UI, data collection, and agent logic.

**Goal**: Ship point solutions fast. Sell direct. Stack revenue.

---

## System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VERTICAL AGENT FACTORY                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  1. DESCRIBE                                                         │
│  ────────────                                                        │
│  Natural language scenario description                               │
│  "Build an agent for HVAC contractors that handles dispatch..."      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. RESEARCH (Claude Agent SDK)                                      │
│  ─────────────────────────────────                                   │
│  • Industry workflow analysis                                        │
│  • Pain point mapping                                                │
│  • Integration requirements (what tools they use)                    │
│  • Pricing research (what they pay for similar)                      │
│  • Competitive landscape                                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. GENERATE (Artifacts + A2UI)                                      │
│  ──────────────────────────────                                      │
│  • Agent specification (system prompt, tools, behaviors)             │
│  • Onboarding flow (generative UI components)                        │
│  • Data schemas (what to collect from user)                          │
│  • Landing page / marketing copy                                     │
│  • Pricing model                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. DEPLOY                                                           │
│  ─────────                                                           │
│  • GitHub repo created                                               │
│  • Deployed to cloud (Vercel/Railway/Cloudflare)                     │
│  • Agent live and accepting users                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. SELL                                                             │
│  ─────                                                               │
│  • LinkedIn campaign assets generated                                │
│  • Landing page live                                                 │
│  • Stripe integration for payments                                   │
│  • Product added to portfolio                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Factory Dashboard (NotebookLM-style)

The user-facing interface for YOU to create and manage vertical agents.

**Features:**
- Chat interface for describing new vertical scenarios
- Knowledge base explorer (industry playbooks, patterns)
- Artifact generation (specs, code, copy)
- Audio briefings for each vertical (NotebookLM-style podcasts)
- Portfolio view of all deployed agents
- Revenue tracking per agent

**Tech:**
- Next.js + A2UI components
- Claude API for chat
- Vector store for knowledge base (Pinecone/Supabase)
- Audio synthesis for briefings (ElevenLabs/OpenAI TTS)

### 2. Agent SDK Orchestrator

Uses Claude Agent SDK to run multi-step research and generation.

**Agents:**
- `ResearchAgent` — Analyzes vertical, maps workflows, identifies pain points
- `SpecAgent` — Generates agent specifications from research
- `UIAgent` — Creates A2UI onboarding components
- `CopyAgent` — Writes landing pages, LinkedIn posts, email sequences
- `DeployAgent` — Scaffolds repo, pushes to GitHub, triggers deployment

### 3. Knowledge Repository

Structured knowledge base for rapid agent development.

**Contents:**
- Industry playbooks (pain points, workflows, personas)
- Integration catalog (CRMs, calendars, payment systems)
- UI component library (onboarding patterns)
- Pricing models (by vertical, by value delivered)
- System prompt templates

### 4. Agent Template

Each vertical agent follows a standard structure:

```
agent-{vertical}/
├── README.md                 # Agent documentation
├── package.json              # Dependencies
├── .env.example              # Required env vars
├── src/
│   ├── agent/
│   │   ├── system-prompt.md  # Core agent prompt
│   │   ├── tools.ts          # MCP tools for this vertical
│   │   └── config.ts         # Agent configuration
│   ├── onboarding/
│   │   ├── flows/            # A2UI flow definitions
│   │   ├── schemas/          # Data collection schemas
│   │   └── components/       # Custom UI components
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── onboard/          # Onboarding flow
│   │   ├── dashboard/        # User dashboard
│   │   └── api/              # API routes
│   └── lib/
│       ├── integrations/     # Third-party integrations
│       └── storage/          # Data persistence
├── marketing/
│   ├── landing-copy.md       # Website copy
│   ├── linkedin-posts/       # Social content
│   └── email-sequences/      # Nurture campaigns
└── deploy/
    ├── vercel.json           # Deployment config
    └── scripts/              # Deployment automation
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 + A2UI | Dashboard, agent UIs, onboarding flows |
| **Generative UI** | A2UI SDK | Dynamic form generation, file collection |
| **Agent Runtime** | Claude Agent SDK | Multi-agent orchestration |
| **LLM** | Claude API (claude-sonnet-4-20250514) | Fast agent responses |
| **Vector Store** | Supabase pgvector | Knowledge base, RAG |
| **Auth** | Clerk / NextAuth | User authentication |
| **Payments** | Stripe | Subscriptions, one-time payments |
| **Storage** | Supabase / S3 | User files, agent data |
| **Deployment** | Vercel / Railway | Auto-deploy from GitHub |
| **Voice** | ElevenLabs / Vapi | Voice agents (optional) |

---

## Revenue Model

Each vertical agent is priced based on:

1. **Value delivered** (time saved × hourly rate)
2. **Market standard** (what they pay for alternatives)
3. **Pain severity** (how bad is the problem)

**Typical pricing tiers:**

| Tier | Price/year | Target | Features |
|------|------------|--------|----------|
| Starter | $2,400 | Solopreneurs | Core automation, 100 tasks/mo |
| Pro | $6,000 | Small teams | Unlimited tasks, integrations |
| Enterprise | $12,000+ | Multi-location | Custom workflows, API access |

---

## First Sprint: MVP

**Goal**: Ship 3 vertical agents in 2 weeks.

**Week 1:**
1. Set up factory infrastructure (repo, deployment pipeline)
2. Build first agent: Construction RFQ Processor
3. Create onboarding flow template
4. Deploy and test

**Week 2:**
1. Build agent 2: Dental Scheduling Assistant
2. Build agent 3: Personal Injury Intake
3. LinkedIn campaign for all 3
4. Stripe integration

**Success metrics:**
- 3 agents deployed and functional
- Landing pages converting to trials
- First paying customer within 30 days

---

## Scaling Strategy

**Phase 1 (Month 1-2):** 3-5 agents, validate pricing, find PMF
**Phase 2 (Month 3-4):** 10 agents, hire sales, optimize funnels
**Phase 3 (Month 5-6):** 20+ agents, explore partnerships (trade associations, software vendors)
**Phase 4 (Month 7+):** Agent marketplace, white-label to agencies
