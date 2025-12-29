# Build Agent Slash Command

Build a complete vertical AI agent from a natural language description.

## Usage
```
/build-agent [vertical description]
```

## Examples
```
/build-agent personal injury law firm
/build-agent veterinary clinic
/build-agent construction contractor RFQ processing
/build-agent auto repair shop scheduling
```

---

## Instructions for Claude

When this command is invoked with a vertical description, execute the Vertical Agent Factory workflow:

### Phase 1: Discovery

1. **Parse the vertical name** from the user's input
2. **Check existing playbooks** in `verticals/` and `knowledge/industry-playbooks/`
3. **Research the market** using web search:
   - Market size (number of SMBs in US)
   - Average revenue range
   - Tech adoption level
   - Key pain points (search Reddit, industry forums)
   - Existing competitors and their pricing
4. **Identify 2-3 workflow options** ranked by automation potential:
   - What's the most repetitive task?
   - What takes the most time?
   - What's easiest to automate?
5. **Present discovery findings** and wait for user approval

### Phase 2: Specification

1. **Generate VERTICAL.md** spec using the template at `verticals/_template/VERTICAL.md`
2. **Generate persona** using Prometheus v3.3 at `core/prometheus/PROMETHEUS.md`
3. **Define tools** in MCP format based on the chosen workflow
4. **Create onboarding flow** YAML with data collection steps
5. **Save artifacts** to `verticals/[vertical-slug]/`
6. **Present specification** and wait for user approval

### Phase 3: Build

1. **Scaffold Next.js app** using factory templates
2. **Generate A2UI components**:
   - InlineChatForm (forms inside chat messages)
   - InlineSelect (pill button selection)
   - InlineSlider (range input)
   - InlineButtons (grid buttons)
3. **Create agent configuration**:
   - System prompt with persona
   - Tool definitions
   - Onboarding flow integration
4. **Generate database migrations** for Supabase
5. **Output to configured directory** (default: `~/VerticalAgents/[vertical-slug]/`)

### Phase 4: Delivery

1. **Generate Admin Dashboard** (NotebookLM-style 3-panel):
   - Left: Knowledge Base (docs, FAQs, case types)
   - Center: Agent Chat (test interface with debug mode)
   - Right: Tuning Panel (examples, tone, settings)
2. **Generate Client Landing Page**:
   - Hero section with "Start Onboarding" CTA
   - Features, How It Works, CTA sections
   - Footer with links
3. **Wire up complete flow**:
   - Landing → Chat (onboarding) → Admin Dashboard
4. **Generate deployment config**:
   - Vercel configuration
   - Docker / docker-compose
   - GitHub Actions CI/CD

### Approval Gates

- **After Discovery**: Present workflow options, get user confirmation
- **After Specification**: Present VERTICAL.md and persona, get user approval
- **After Build**: Show output directory structure
- **After Delivery**: Provide next steps for deployment

### Factory Configuration

The factory reads configuration from `factory/config/factory.config.yaml`:
- Output directory: Where generated apps are saved
- Playbook examples: Reference verticals for cross-checking
- Generation settings: Model, persona engine

### Output Structure

```
~/VerticalAgents/[vertical-slug]/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── chat/page.tsx         # Client chat with A2UI
│   │   └── admin/page.tsx        # Admin dashboard
│   ├── components/
│   │   ├── a2ui/                 # Inline chat components
│   │   ├── admin/                # Dashboard components
│   │   └── landing/              # Landing page components
│   └── agent/
│       ├── config.ts             # Agent configuration
│       └── tools/                # MCP tool definitions
├── supabase/
│   └── migrations/               # Database schema
├── package.json
├── README.md
└── .env.example
```

### Key Files to Reference

- `core/orchestrator/factory-agent.py` - Master orchestrator
- `core/orchestrator/phases/` - Phase implementations
- `core/prometheus/PROMETHEUS.md` - Persona generation
- `verticals/_template/VERTICAL.md` - Specification template
- `factory/config/factory.config.yaml` - Factory settings

---

## Example Conversation Flow

**User**: `/build-agent personal injury law firm`

**Claude (Discovery)**:
```
Researching personal injury law vertical...

Market Overview:
- ~50,000 PI law firms in the US
- Average revenue: $500K-$2M
- Tech adoption: Medium

Top Pain Points:
1. Lead intake (manual phone screening)
2. Case qualification (determining validity)
3. Document collection (chasing medical records)

Recommended Workflows:
1. [RECOMMENDED] Lead Intake Automation
   - Automation potential: 85%
   - Time savings: 15 hrs/week
   - Integrations: Clio, phone system

2. Case Qualification Assistant
   - Automation potential: 70%
   - Time savings: 10 hrs/week

3. Document Collection Bot
   - Automation potential: 60%
   - Time savings: 8 hrs/week

Approve workflow selection? [1/2/3]
```

**User**: `1`

**Claude (Specification)**:
```
Generating specification for Lead Intake Automation...

Created: verticals/personal-injury-law/
├── VERTICAL.md (specification)
├── persona.xml (Prometheus-generated)
├── tools/ (MCP definitions)
└── onboarding/ (flow.yaml)

[Shows VERTICAL.md preview]

Approve specification?
```

**User**: `yes`

**Claude (Build + Delivery)**:
```
Scaffolding application...

Output: ~/VerticalAgents/personal-injury-law/
├── src/app/ (pages)
├── src/components/a2ui/ (inline forms)
├── src/components/admin/ (dashboard)
├── supabase/ (migrations)

Next steps:
1. cd ~/VerticalAgents/personal-injury-law
2. npm install
3. Copy .env.example to .env.local
4. npm run dev
5. Open http://localhost:3000
```
