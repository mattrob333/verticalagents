# Vertical Agent Factory

**A meta-system for rapidly building and deploying vertical AI agents for SMBs.**

> Build once, ship many. Each vertical agent = $10K-$50K ARR.

## What Is This?

Vertical Agent Factory is a **factory that builds factories**. Give it an industry vertical (like "personal injury law" or "veterinary clinic"), and it outputs a complete, deployable AI agent application with:

- Dual-mode AI agent (onboarding + consultation)
- Admin dashboard (NotebookLM-style 3-panel)
- Client-facing landing page
- Supabase database schema
- Deployment configs

**The factory stays clean. Generated agents live in separate directories.**

## Architecture

```
THIS REPO (Factory)                      OUTPUT (Generated Apps)
-------------------                      ----------------------
core/orchestrator/                       ~/VerticalAgents/
  ├── factory-agent.py                   ├── personal-injury-law/
  └── phases/                            │   ├── src/app/
      ├── discovery.py                   │   │   ├── page.tsx (landing)
      ├── specification.py               │   │   ├── admin/ (dashboard)
      ├── scaffold.py                    │   │   └── chat/ (client chat)
      └── delivery.py                    │   ├── agent/
                                         │   │   └── system-prompt.xml
core/meta-prompts/                       │   └── components/a2ui/
  ├── dual-mode-agent.xml                │
  ├── onboarding-states.yaml             └── veterinary-clinic/
  └── personas/                              └── ...
      ├── personal-injury-law.yaml
      ├── construction-contractor.yaml
      └── veterinary-clinic.yaml

factory/
  ├── config/factory.config.yaml
  ├── generators/prompt_generator.py
  └── templates/agent-app/
```

## Quick Start

### Build a Vertical Agent

The fastest way to create a new vertical agent:

```
/build-agent personal injury law firm
```

This triggers the **4-phase factory workflow**:

```
Phase 1: DISCOVERY
  - Web search for industry data
  - Cross-reference playbook examples
  - Present 2-3 workflow options
  - [APPROVAL GATE]
      ↓
Phase 2: SPECIFICATION
  - Generate VERTICAL.md spec
  - Generate dual-mode system prompt
  - Define MCP tools
  - [APPROVAL GATE]
      ↓
Phase 3: BUILD
  - Scaffold Next.js app
  - Generate A2UI components
  - Create Supabase migrations
  - Output to ~/VerticalAgents/
      ↓
Phase 4: DELIVERY
  - Generate Admin Dashboard
  - Generate Client Landing Page
  - Wire up complete flow
```

Output is saved to `~/VerticalAgents/[vertical-slug]/` (configurable in `factory/config/factory.config.yaml`).

## Dual-Mode Agent Architecture

Generated agents operate in **two distinct modes**:

### 1. Onboarding Mode (Deterministic)

When a user hasn't completed onboarding, the agent follows a **strict state machine**:

- Pre-defined steps with specific A2UI components
- Cannot deviate or get creative
- Validates required fields before advancing
- Off-topic questions: brief answer, then redirect

```xml
<onboarding_controller>
  <state name="case_type" next="incident_date">
    <message>What type of legal matter are you dealing with?</message>
    <a2ui_component>
      <InlineButtons options="['Auto Accident', 'Slip & Fall', 'Medical']" />
    </a2ui_component>
    <required>true</required>
  </state>
</onboarding_controller>
```

### 2. Consultation Mode (Flexible)

After onboarding, the agent becomes a **thinking partner**:

- Has opinions and worldview specific to the industry
- Adapts to user intent (exploring, venting, urgent, etc.)
- Can brainstorm, teach, and share perspectives
- Full personality expression

```xml
<consultation_persona>
  <worldview>
    <core_beliefs>
      - Every accident victim deserves to be heard without judgment
      - The legal process can be overwhelming - simplicity is kindness
    </core_beliefs>
  </worldview>
  <intent_reading>
    exploring: "Let them think through their situation out loud"
    urgent: "Assess true urgency, prioritize accordingly"
  </intent_reading>
</consultation_persona>
```

## Industry-Specific Personas

Each vertical gets a **fully customized personality**:

| Vertical | Persona Style | Energy |
|----------|--------------|--------|
| Personal Injury Law | Compassionate advocate | Calm, reassuring, unhurried |
| Construction Contractor | No-nonsense estimator | Direct, efficient, confident |
| Veterinary Clinic | Warm animal lover | Caring, patient, gentle |

Personas are defined in `core/meta-prompts/personas/` and include:
- Worldview (core beliefs, aesthetics, pet peeves)
- Expertise map (deep mastery, working knowledge, honest limits)
- Conversational style (when exploring, teaching, building)
- Flexibility rules (intent reading, boot-up behavior)

## A2UI Inline Chat Components

Forms appear **inside the chat message stream**:

```
┌─────────────────────────────────────────┐
│ What type of accident?                  │
│ [Auto] [Slip & Fall] [Medical] [Other]  │
│                                         │
│ Rate injury severity (1-10)             │
│ ═══════════●══════════ 7                │
│                                         │
│ [Continue]                              │
└─────────────────────────────────────────┘
```

Available components:
- `InlineSelect` - Button-style single selection
- `InlineButtons` - Grid multi-select buttons
- `InlineSlider` - Range input with labels
- `InlineTextarea` - Multi-line text input
- `InlineFileUpload` - Document upload
- `InlineChatForm` - Wrapper for form submission

## Configuration

Edit `factory/config/factory.config.yaml`:

```yaml
output:
  default_dir: "~/VerticalAgents"

generation:
  prompt_engine: "dual-mode"

  dual_mode:
    onboarding_strictness: "high"
    allow_tangents: true
    personality_depth: "full"
    intent_reading: true
    persona_variation: "fully_customized"
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Runtime | Claude Agent SDK |
| Persona Engine | Dual-Mode Prompt Generator |
| UI Framework | A2UI (Next.js 14) |
| LLM | Claude API (claude-sonnet-4-20250514) |
| Database | Supabase (pgvector for RAG) |
| Auth | Clerk / NextAuth |
| Payments | Stripe |
| Deployment | Vercel / Railway |

## Target Verticals

| Vertical | Agent Focus | Est. Time Saved | Price Point |
|----------|-------------|-----------------|-------------|
| Personal Injury Law | Client intake | 15 hrs/week | $15K/year |
| Construction | RFQ processing | 2 days → 2 hrs | $20K/year |
| Veterinary Clinics | Scheduling & triage | 10 hrs/week | $12K/year |
| Auto Repair | Diagnostic intake | 20 hrs/week | $15K/year |
| HVAC/Plumbing | Dispatch & invoicing | 15 hrs/week | $18K/year |

## Project Status

- [x] Factory foundation (orchestrator, phases, config)
- [x] Dual-mode meta-prompt architecture
- [x] Industry persona templates (3 verticals)
- [x] Prompt generator with CLI
- [x] A2UI component templates
- [ ] Discovery phase web search integration
- [ ] Scaffold phase template injection
- [ ] Admin dashboard generation
- [ ] End-to-end vertical generation test

## Manual Commands

```bash
# Generate a system prompt for a vertical
python factory/generators/prompt_generator.py personal-injury-law --output prompt.xml

# Create a new vertical from template
python tools/new-vertical.py --name "auto repair shop"

# Generate persona from spec
python tools/generate-persona.py verticals/[vertical]/VERTICAL.md
```

## Revenue Model

```
Year 1 Target: 10 verticals × 10 clients × $15K avg = $1.5M ARR

Timeline per vertical:
- Week 1: Research & spec
- Week 2: Build & test
- Week 3: Marketing & outreach
- Week 4+: Sales & onboarding
```

---

*Built by Tier 4 Intelligence*
