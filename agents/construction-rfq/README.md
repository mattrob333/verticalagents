# Construction RFQ Agent

An AI-powered assistant that processes Requests for Quotation (RFQs) for construction contractors, cutting response time from days to hours.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/tier4/agent-construction-rfq.git
cd agent-construction-rfq

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
npm run dev
```

## Features

- **RFQ Parsing** — Extract requirements, deadlines, and scope from RFQ documents
- **Supplier Matching** — Identify materials and match to preferred suppliers
- **Quote Comparison** — Compare supplier bids on price, lead time, and quality
- **Proposal Generation** — Create professional PDF proposals with detailed breakdowns
- **Email Integration** — Receive RFQs and send proposals via email

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Email Inbox                             │
│                    (rfq@yourcompany.agent.ai)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RFQ Parser Agent                           │
│  • Extract project details                                       │
│  • Identify materials and quantities                             │
│  • Parse deadlines and requirements                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supplier Matching Agent                       │
│  • Match materials to supplier catalog                           │
│  • Request quotes from preferred vendors                         │
│  • Track responses and follow up                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Quote Analysis Agent                          │
│  • Compare supplier quotes                                       │
│  • Score on price, lead time, reliability                        │
│  • Recommend optimal selection                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Proposal Generator Agent                       │
│  • Calculate labor and overhead                                  │
│  • Apply markup and adjustments                                  │
│  • Generate professional PDF                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Review Dashboard                            │
│  • Human review (optional)                                       │
│  • Edit and approve                                              │
│  • Send to client                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Email Integration
EMAIL_PROVIDER=gmail  # or outlook
EMAIL_CLIENT_ID=...
EMAIL_CLIENT_SECRET=...

# Supabase (Database & Storage)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# Integrations (Optional)
PROCORE_CLIENT_ID=...
PROCORE_CLIENT_SECRET=...
QUICKBOOKS_CLIENT_ID=...
QUICKBOOKS_CLIENT_SECRET=...

# Stripe (Payments)
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Agent Configuration

```typescript
// src/agent/config.ts

export const agentConfig = {
  name: "RFQ Processor",
  model: "claude-sonnet-4-20250514",
  
  // Processing settings
  defaultMarkup: 0.25,           // 25% default markup
  laborRate: 75,                  // $/hour for labor calculations
  overheadRate: 0.15,            // 15% overhead
  
  // Response settings
  autoSend: false,               // Require human review by default
  maxResponseTime: "4h",         // Target response time
  reminderFrequency: "2h",       // Reminder for pending reviews
  
  // Supplier settings
  maxSuppliersPerMaterial: 3,    // Quote from top 3 suppliers
  quoteWaitTime: "4h",           // Wait for supplier quotes
  
  // Email settings
  inboxAddress: "rfq@yourcompany.agent.ai",
  replyFromName: "RFQ Assistant",
};
```

## API Reference

### Endpoints

```
POST /api/rfq/parse
  - Parse an RFQ document
  - Input: { file: File } or { emailId: string }
  - Output: { rfq: ParsedRFQ }

POST /api/rfq/analyze
  - Analyze parsed RFQ and get supplier recommendations
  - Input: { rfqId: string }
  - Output: { analysis: RFQAnalysis, suppliers: SupplierRecommendation[] }

POST /api/rfq/generate-proposal
  - Generate a proposal from analysis
  - Input: { rfqId: string, supplierSelections: Record<string, string> }
  - Output: { proposal: Proposal, pdfUrl: string }

POST /api/rfq/send
  - Send proposal to client
  - Input: { rfqId: string, recipientEmail: string }
  - Output: { sent: boolean, messageId: string }
```

### Webhooks

```
POST /webhooks/email/incoming
  - Called when new email arrives
  
POST /webhooks/supplier/quote-received
  - Called when supplier responds with quote
  
POST /webhooks/stripe/subscription
  - Called on subscription changes
```

## Database Schema

```sql
-- Users and accounts
CREATE TABLE accounts (
  id UUID PRIMARY KEY,
  company_name TEXT NOT NULL,
  subscription_tier TEXT DEFAULT 'starter',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RFQ Processing
CREATE TABLE rfqs (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  status TEXT DEFAULT 'pending', -- pending, analyzing, ready, sent
  source_email_id TEXT,
  parsed_data JSONB,
  analysis JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  due_at TIMESTAMPTZ
);

CREATE TABLE proposals (
  id UUID PRIMARY KEY,
  rfq_id UUID REFERENCES rfqs(id),
  total_amount DECIMAL(12,2),
  markup_percentage DECIMAL(5,2),
  pdf_url TEXT,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Supplier Management
CREATE TABLE suppliers (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  name TEXT NOT NULL,
  contact_email TEXT,
  categories TEXT[],
  reliability_score DECIMAL(3,2),
  avg_response_time INTERVAL
);

CREATE TABLE supplier_quotes (
  id UUID PRIMARY KEY,
  rfq_id UUID REFERENCES rfqs(id),
  supplier_id UUID REFERENCES suppliers(id),
  material_id TEXT,
  unit_price DECIMAL(10,2),
  quantity INTEGER,
  lead_time_days INTEGER,
  received_at TIMESTAMPTZ
);
```

## Deployment

### Vercel

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "ANTHROPIC_API_KEY": "@anthropic-api-key",
    "SUPABASE_URL": "@supabase-url",
    "SUPABASE_ANON_KEY": "@supabase-anon-key"
  }
}
```

### Railway

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "npm start"
healthcheckPath = "/api/health"
healthcheckTimeout = 30

[[services]]
name = "web"
```

## Pricing

| Tier | Price | RFQs/Month | Features |
|------|-------|------------|----------|
| Starter | $299/mo | 10 | Email parsing, basic comparison |
| Pro | $599/mo | Unlimited | Procore integration, supplier scoring |
| Enterprise | $999/mo | Unlimited | Multi-user, custom templates, API |

## Support

- Documentation: https://docs.yourcompany.com/rfq-agent
- Email: support@yourcompany.com
- Discord: https://discord.gg/yourcompany

## License

Proprietary - Tier 4 Intelligence
