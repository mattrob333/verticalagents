# Hermes Vertical Agent Profile — Template

This is the **output format** the Hermes Vertical Forge generates. Each vertical
agent becomes a self-contained Hermes profile directory that can be imported via
`hermes profile import` or copied into `~/.hermes/profiles/<name>/`.

## Directory Structure

```
<vertical-slug>/
├── README.md              # What this agent is, who it's for, how to deploy
├── config.yaml            # Hermes agent config (model, provider, gateway, tools)
├── system-prompt.md       # Dual-mode persona prompt (the crown jewel)
├── onboarding.yaml        # Onboarding state machine definition
├── mcp-config.yaml        # MCP tool server configurations
├── gateway.yaml           # Telegram / web channel configuration (overlay)
├── skills/                # Persona expertise as Hermes skills
│   └── <vertical>-persona/
│       └── SKILL.md       # Worldview, expertise, conversational style
├── cron/                  # Scheduled resident tasks (daily reminders, follow-ups)
│   └── daily-checkin.md   # Example cron job definition
└── migrations/            # Data schema (Supabase SQL or equivalent)
    └── schema.sql
```

## Design Principles

1. **Dual-mode architecture preserved** — `system-prompt.md` contains the mode
   router (onboarding state machine + consultation thinking partner). The persona
   is NOT a task executor; it's a thinking partner with worldview and opinions.

2. **Persona is the crown jewel** — `skills/<vertical>-persona/SKILL.md` carries
   the worldview (core beliefs, what they find beautiful/cringe), expertise (deep
   mastery vs working knowledge), and conversational style. This is loaded into
   every session.

3. **Template variables** — `system-prompt.md` and `config.yaml` use
   `{{company_name}}`, `{{markup_percentage}}`, etc. These are resolved at
   deployment time (per-client), not at generation time.

4. **Factory/output separation** — Generated profiles live outside the factory
   repo (in `hermes-profiles/` or a separate output dir). This template is the
   blueprint the factory's scaffold phase produces.

## How the Factory Produces This

```
Factory Phase 3 (BUILD):
  VERTICAL.md + persona.xml  →  this template structure
  - persona.xml worldview    →  skills/<vertical>-persona/SKILL.md
  - dual-mode-agent.xml      →  system-prompt.md (adapted to Hermes format)
  - onboarding/flow.yaml     →  onboarding.yaml
  - integrations/            →  mcp-config.yaml + gateway.yaml
```

## Deployment

```bash
# Import as a Hermes profile
hermes profile import <vertical-slug>.tar.gz

# Or copy manually
cp -r <vertical-slug>/ ~/.hermes/profiles/<vertical-slug>/
hermes profile use <vertical-slug>

# Set client-specific template variables
hermes config set company_name "Acme Construction"
hermes config set markup_percentage 25

# Start the gateway
hermes gateway run
```
