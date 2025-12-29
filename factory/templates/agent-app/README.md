# Agent App Template

This directory contains the base template for generated vertical AI agent applications.

## Structure

```
agent-app/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/    # React components
│   │   ├── a2ui/      # Inline chat form components
│   │   ├── admin/     # Admin dashboard components
│   │   ├── landing/   # Landing page components
│   │   └── chat/      # Chat interface components
│   ├── lib/           # Utility libraries
│   │   ├── supabase/  # Database client
│   │   ├── claude/    # Claude API integration
│   │   └── utils/     # Helper functions
│   └── agent/         # Agent configuration
│       ├── config.ts  # Agent settings
│       ├── tools/     # MCP tool definitions
│       └── prompts/   # System prompts
├── supabase/
│   └── migrations/    # Database migrations
└── public/            # Static assets
```

## Template Variables

The scaffold phase replaces these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{VERTICAL_NAME}}` | Human-readable name | "Personal Injury Law" |
| `{{VERTICAL_SLUG}}` | URL-friendly slug | "personal-injury-law" |
| `{{PERSONA_XML}}` | Prometheus-generated persona | Full XML content |
| `{{TOOL_DEFINITIONS}}` | MCP tool array | Tool JSON |
| `{{ONBOARDING_FLOW}}` | Onboarding YAML content | Step definitions |

## Generated Apps

When the factory scaffolds an app, it:

1. Copies this template to the output directory
2. Replaces template variables with vertical-specific values
3. Generates A2UI components based on onboarding flow
4. Creates database migrations for the vertical's data model
5. Generates admin dashboard with knowledge base panels
6. Creates landing page with vertical branding

## A2UI Components

Forms appear inline within chat messages:

```tsx
<ChatMessage role="assistant">
  Let me gather some information.

  <InlineChatForm onSubmit={handleSubmit}>
    <InlineSelect
      name="case_type"
      options={["Option A", "Option B", "Option C"]}
    />
    <InlineSlider
      name="severity"
      min={1}
      max={10}
    />
    <InlineButtons
      name="status"
      options={["Yes", "No", "Maybe"]}
    />
  </InlineChatForm>
</ChatMessage>
```

## Admin Dashboard

NotebookLM-style 3-panel layout:

```
┌──────────────┬─────────────────────┬───────────────┐
│ KNOWLEDGE    │ AGENT CHAT          │ TUNING        │
│ BASE         │ (Test Interface)    │ PANEL         │
├──────────────┼─────────────────────┼───────────────┤
│ • Docs       │ • Live testing      │ • Examples    │
│ • FAQs       │ • Debug mode        │ • Tone        │
│ • Cases      │ • Tool calls        │ • Settings    │
└──────────────┴─────────────────────┴───────────────┘
```

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Database**: Supabase (PostgreSQL + pgvector)
- **Auth**: Clerk
- **Payments**: Stripe
- **AI**: Claude API via Claude Agent SDK
