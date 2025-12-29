# Vertical Agent Knowledge Base

## Structure

```
knowledge/
├── industries/               # Industry-specific playbooks
│   ├── construction/
│   │   ├── playbook.md      # Pain points, workflows, personas
│   │   ├── integrations.md  # Common tools they use
│   │   └── pricing.md       # Market rates, willingness to pay
│   ├── legal/
│   ├── dental/
│   ├── hvac/
│   └── ...
├── patterns/                 # Reusable automation patterns
│   ├── intake.md            # Client intake patterns
│   ├── scheduling.md        # Appointment scheduling
│   ├── quoting.md           # Quote/estimate generation
│   ├── dispatch.md          # Job/tech dispatch
│   └── follow-up.md         # Re-engagement patterns
├── integrations/             # Integration guides
│   ├── crm/
│   ├── calendars/
│   ├── payments/
│   └── communication/
└── pricing/                  # Pricing frameworks
    ├── value-based.md
    ├── competitor-anchoring.md
    └── tiering-strategies.md
```

---

## Industry Playbook Template

Each industry playbook follows this structure:

```markdown
# {Industry} Vertical Playbook

## Market Overview
- Market size and growth rate
- Number of businesses in target segment
- Typical company size and structure
- Technology adoption level

## Target Persona
- Decision maker role/title
- Pain points and daily frustrations
- Goals and success metrics
- Budget authority and typical spend
- How they buy (research process, decision factors)

## Current Workflow (Before AI)
- Step-by-step process description
- Time spent on each step
- Tools currently used
- Common failure points
- Cost of errors/delays

## Automation Opportunity
- Which steps can be automated
- Expected time savings
- Expected quality improvements
- ROI calculation

## Integration Requirements
- Must-have integrations
- Nice-to-have integrations
- API availability and quality
- Authentication patterns

## Competitive Landscape
- Existing solutions (software, services)
- Their pricing
- Their limitations
- Our differentiation

## Pricing Strategy
- Value delivered (quantified)
- Comparable spend (what they pay for similar)
- Recommended price point
- Tier structure
```

---

## Sample Playbook: Construction RFQ Processing

# Construction RFQ Processing Playbook

## Market Overview
- **Market size**: $1.8T US construction market
- **Target segment**: Commercial contractors, $5M-$50M annual revenue
- **Company count**: ~40,000 firms in target segment
- **Tech adoption**: Medium - uses Procore, Buildertrend, or similar; email-heavy
- **Growth**: 4% CAGR, stable demand

## Target Persona

**Role**: Estimator or Project Manager (sometimes owner at smaller firms)

**Profile**:
- Age 35-55, male-dominated but changing
- 10+ years industry experience
- Juggles 5-15 active bids at any time
- Works 50+ hours/week
- Stressed about deadlines and accuracy

**Pain Points**:
- RFQ responses take 1-2 days (competitors respond faster)
- Manual supplier comparison is tedious and error-prone
- No time to optimize pricing on every bid
- Loses bids due to slow response or missing details
- Paperwork pulls them away from job sites

**Goals**:
- Win more bids
- Spend more time on high-value projects
- Reduce estimation errors
- Improve margins through better supplier selection

**Budget**: Authorized to spend $500-1000/mo on productivity tools

## Current Workflow (Before AI)

| Step | Time | Pain Level |
|------|------|------------|
| Receive RFQ via email | - | Low |
| Review scope and requirements | 30 min | Medium |
| Identify needed materials/labor | 45 min | High |
| Request quotes from suppliers | 30 min | Medium |
| Wait for supplier responses | 4-24 hrs | High |
| Compare supplier quotes | 45 min | Very High |
| Calculate labor and overhead | 30 min | Medium |
| Apply markup and adjustments | 15 min | Low |
| Generate proposal document | 45 min | High |
| Review and send | 15 min | Low |
| **Total** | **8-24 hrs** | |

**Failure Points**:
- Missed RFQ deadlines (bid not submitted)
- Calculation errors (margin too low or bid too high)
- Wrong supplier selected (delays, quality issues)
- Missing scope items (change orders, customer friction)

## Automation Opportunity

**Automated Steps**:
1. Parse incoming RFQ → Extract requirements, deadlines, key details
2. Identify materials → Match to supplier catalog
3. Request supplier quotes → Auto-send to preferred vendors
4. Compare quotes → Score on price, lead time, quality
5. Calculate bid → Apply standard markup, labor rates
6. Generate proposal → Professional PDF with breakdown

**Time Savings**: 8-24 hrs → 1-2 hrs (with human review)

**Quality Improvements**:
- No missed scope items
- Consistent markup application
- Better supplier selection
- Faster response = more competitive

**ROI Calculation**:
- Time saved: 15 hrs/week × $75/hr (estimator cost) = $1,125/week
- Additional bids won: 2/month × $5K avg profit = $10K/month
- Total value: ~$14K/month
- Price at 5% of value: $700/month

## Integration Requirements

**Must-Have**:
- Email (Gmail/Outlook) — Receive RFQs, send proposals
- PDF parsing — Extract RFQ details

**Should-Have**:
- Procore or Buildertrend — Project data sync
- QuickBooks — Supplier pricing, invoicing
- DocuSign — Proposal signatures

**Nice-to-Have**:
- Supplier APIs — Real-time pricing (most don't have)
- Material cost databases — RSMeans, etc.

## Competitive Landscape

| Competitor | What They Do | Price | Limitation |
|------------|--------------|-------|------------|
| Procore | PM platform with some estimation | $500-2000/mo | Not AI-powered, still manual |
| BuildingConnected | Bid management | $300-1000/mo | Connects parties, doesn't automate |
| STACK | Takeoff and estimation | $200-500/mo | Focused on takeoff, not full workflow |
| Manual process | Excel, email | $0 | Slow, error-prone |

**Our Differentiation**:
- End-to-end automation (not just one step)
- AI-powered analysis (not just digitized forms)
- 10x speed improvement
- Drop-in to existing workflow (email-based)

## Pricing Strategy

| Tier | Price | Features | Target |
|------|-------|----------|--------|
| Starter | $299/mo | 10 RFQs/mo, email parsing, basic comparison | Small contractors |
| Pro | $599/mo | Unlimited RFQs, Procore integration, supplier scoring | Mid-size contractors |
| Enterprise | $999/mo | Multi-user, custom templates, API access | Large firms |

**Pricing Justification**:
- Pro tier at $599/mo = 4% of monthly value delivered
- Pays for itself with 1 additional won bid per quarter
- Lower than Procore but focused on specific problem
