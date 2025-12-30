Build a complete vertical AI agent for: $ARGUMENTS

Execute the Vertical Agent Factory 4-phase workflow:

## Phase 1: Discovery

1. Parse the vertical name from "$ARGUMENTS"
2. Create a URL-friendly slug (e.g., "personal injury law firm" → "personal-injury-law")
3. Check if we have an existing persona in `core/meta-prompts/personas/[slug].yaml`
4. Research the market using web search:
   - Market size (number of SMBs in US)
   - Average revenue range
   - Key pain points
   - Existing competitors
5. Identify 2-3 workflow options ranked by automation potential
6. Present findings and WAIT for user approval before proceeding

## Phase 2: Specification

After user approves discovery:

1. Generate VERTICAL.md spec for the vertical
2. Generate dual-mode system prompt using `factory/generators/prompt_generator.py`:
   - If persona exists: `py factory/generators/prompt_generator.py [slug] --output verticals/[slug]/system-prompt.xml`
   - If no persona: Generate custom persona configuration
3. Define MCP tools based on the chosen workflow
4. Create onboarding flow with A2UI component mappings
5. Save artifacts to `verticals/[slug]/`
6. Present specification and WAIT for user approval

## Phase 3: Build

After user approves specification:

1. Determine output directory from `factory/config/factory.config.yaml` (default: ~/VerticalAgents/)
2. Scaffold Next.js app using templates from `factory/templates/agent-app/`
3. Inject the generated system prompt
4. Generate A2UI inline chat components
5. Create Supabase migrations
6. Output complete app to `[output_dir]/[slug]/`

## Phase 4: Delivery

1. Generate Admin Dashboard (3-panel NotebookLM style)
2. Generate Client Landing Page with "Start Onboarding" CTA
3. Wire up: Landing → Onboarding Chat → Dashboard
4. Generate deployment configs (Vercel, Docker)
5. Present next steps to user

## Key Files

- Factory config: `factory/config/factory.config.yaml`
- Prompt generator: `factory/generators/prompt_generator.py`
- Personas: `core/meta-prompts/personas/`
- Master template: `core/meta-prompts/dual-mode-agent.xml`
- App templates: `factory/templates/agent-app/`

## Approval Gates

IMPORTANT: Wait for explicit user approval after Discovery and Specification phases before proceeding.
