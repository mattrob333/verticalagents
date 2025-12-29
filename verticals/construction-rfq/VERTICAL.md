---
vertical: construction-rfq
status: building
created: 2025-12-28
confidence: high
---

# Construction RFQ Processing Vertical Spec

## Market Overview

The US construction industry includes approximately 750,000 general contractors and subcontractors, with the majority being SMBs (under 20 employees). These businesses handle anywhere from 5-50 RFQs per month depending on size and specialization.

**Key characteristics:**
- Revenue range: $1M-$50M for target segment
- Team size: 5-25 employees typical
- Tech adoption: Medium-low (Excel, email, basic estimating software)
- Decision maker: Owner or operations manager
- Pain tolerance: High — margins are tight, time is money

**Market timing:** Construction AI is nascent. Most contractors still use manual processes. First-mover advantage is significant.

## Target Workflow: RFQ Processing

### Current State

**Process Description:**
1. RFQ arrives (email, portal, or direct)
2. Admin/estimator reviews scope and specs
3. Breaks down into material categories
4. Contacts 3-5 suppliers per category for quotes
5. Waits for responses (1-3 days)
6. Compiles quotes into comparison spreadsheet
7. Selects suppliers based on price/relationship
8. Drafts bid response document
9. Reviews with PM/owner
10. Submits bid

**Who Does It:**
- Estimator (if they have one)
- Office manager
- Often the owner themselves

**Time Investment:**
- Hours per RFQ: 8-16 hours
- RFQs per month: 10-30
- Total time: 80-480 hours/month on RFQ processing

**Current Tools:**
- Email: Primary communication
- Excel: Quote comparison, takeoffs
- Bluebeam/PDF: Markup and review
- Estimating software: Some use Buildertrend, CoConstruct
- Supplier portals: Scattered across vendors

**Pain Points:**
1. **Time sink**: Days of work for each bid, most don't win
2. **Supplier chaos**: Chasing quotes, inconsistent responses
3. **Error-prone**: Manual data entry, missed specs
4. **No memory**: Repeat work, don't leverage past bids
5. **Opportunity cost**: Can't bid on enough projects

**Cost of Status Quo:**
- Direct cost: $50-100/hour estimator time × 100+ hours = $5K-10K/month
- Opportunity cost: Miss 3-5 bids/month = $50K-200K potential revenue

### Desired State

**What "Solved" Looks Like:**
- RFQ received → analyzed in minutes, not hours
- Supplier quotes requested automatically
- Comparison matrix generated instantly
- Bid response drafted and ready for review
- Historical data informs pricing decisions

**Success Metrics:**
- [ ] RFQ turnaround: 2 days → 2 hours
- [ ] Bids submitted: +50% more projects
- [ ] Win rate: Maintain or improve
- [ ] Staff time on RFQs: -80%

### Agent Scope

**Primary Function:**
BidMaster processes RFQs from intake to bid-ready response, automating supplier outreach, quote comparison, and proposal generation.

**Core Capabilities:**
1. **RFQ Intake & Parsing**: Extract specs, quantities, deadlines from PDF/email RFQs
2. **Supplier Matching**: Query supplier database for qualified vendors by category
3. **Quote Request Automation**: Send templated requests to relevant suppliers
4. **Quote Tracking**: Monitor responses, send follow-ups, compile as received
5. **Comparison Matrix**: Generate side-by-side analysis of all quotes
6. **Bid Response Draft**: Create professional proposal document from template
7. **Historical Learning**: Reference past bids for similar projects

**Out of Scope:**
- Actual site visits or takeoffs (still human)
- Final pricing decisions (human approval required)
- Contract negotiation
- Project management post-award

### Integration Requirements

| System | Purpose | API Available? | Complexity |
|--------|---------|----------------|------------|
| Email (Gmail/Outlook) | RFQ intake, supplier comms | Yes | Low |
| PDF Parser | Extract RFQ specs | N/A (library) | Low |
| Supplier Database | Track vendors, contacts, history | Custom build | Medium |
| Twilio/SendGrid | SMS/email automation | Yes | Low |
| Google Sheets/Airtable | Quote comparison output | Yes | Low |
| Doc Generation | Bid response PDFs | Yes (docx lib) | Medium |

**Critical Integration:**
Email inbox monitoring — must catch incoming RFQs reliably.

### Pricing Model

**Base Price:** $20,000/year

**Justification:**
- Time saved: 100 hours/month × $75/hour = $7,500/month = $90K/year value
- Additional bids: 5/month × 10% win rate × $50K avg project = $25K/month potential
- ROI: 5-10x easily demonstrated
- Comparable tools: Estimating software runs $500-2000/month

**Pricing Tiers:**

| Tier | Price | Includes |
|------|-------|----------|
| Starter | $15K/year | Up to 20 RFQs/month, core features |
| Growth | $25K/year | Unlimited RFQs, priority support, custom templates |
| Enterprise | $40K+/year | Multi-location, API access, custom integrations |

**Add-ons:**
- Supplier database seeding: $2K one-time (we research & load their vendors)
- Custom bid templates: $1K per template
- Voice follow-ups: $500/month

### Competition

| Competitor | Price | Strengths | Weaknesses |
|------------|-------|-----------|------------|
| Buildertrend | $500-800/mo | Full PM suite | Overkill, no AI, manual RFQ |
| CoConstruct | $400-600/mo | Good for residential | No RFQ automation |
| PlanHub | $200-500/mo | Bid management | Portal only, no AI processing |
| Manual/Excel | Free | Familiar | Time-intensive, error-prone |

**Market Gap:**
No AI-native solution specifically for RFQ processing. Existing tools are either full PM suites (expensive, complex) or simple bid boards (no automation).

**Differentiation:**
- AI-first: Actually processes and understands RFQs
- Speed: Hours not days
- ROI-focused: Clear, measurable time savings
- Simple: Does one thing extremely well

## Risk Assessment

### Technical Risks
- [x] **PDF parsing variability**: RFQs come in many formats — Mitigation: Train on diverse examples, human fallback for edge cases
- [ ] **Supplier response rates**: Can't force vendors to reply — Mitigation: Track reliability, suggest alternatives

### Market Risks
- [ ] **Sales cycle length**: Construction decisions can be slow — Mitigation: Pilot program, quick demos
- [ ] **Tech resistance**: "We've always done it this way" — Mitigation: ROI calculator, easy onboarding

### Regulatory Considerations
- [ ] **Bid accuracy**: Must be clear AI assists but human approves — Mitigation: Approval workflow, disclaimers

## Go-to-Market

### Target Customer Profile

**Ideal Customer:**
- Business size: 10-50 employees
- Revenue: $5M-$30M
- Location: Any US metro
- Tech savviness: Medium (uses email, basic software)
- Current tools: Excel, email, maybe basic estimating
- RFQ volume: 15-40/month
- Specialty: GC or major sub (electrical, plumbing, HVAC)

**Buyer Persona:**
- Title: Owner, Operations Manager, or Lead Estimator
- Pain level: High — drowning in RFQs, missing opportunities
- Budget authority: Yes (owner) or can influence (manager)
- Decision timeline: 2-4 weeks with demo

### Sales Motion

**Lead Generation:**
- LinkedIn targeting construction owners/estimators
- Trade show presence (local builder associations)
- Partnerships with estimating software vendors
- Content: "How AI is changing construction bidding"

**Sales Cycle:**
- Average length: 3-4 weeks
- Key objections: "We tried software before and it didn't work"
- Closing triggers: Demo showing their actual RFQ processed in minutes

### Marketing Assets Needed

- [x] Landing page
- [ ] Demo video (screen recording of RFQ processing)
- [ ] Case study template
- [x] ROI calculator
- [ ] Email sequences (cold outreach)
- [ ] LinkedIn content calendar

## Recommendation

**Decision:** [x] GO / [ ] NO-GO / [ ] NEED MORE INFO

**Confidence Level:** High

**Key Reasons:**
1. Clear, quantifiable pain point (hours per RFQ)
2. High willingness to pay (used to expensive software)
3. Low competition in AI-native space
4. Replicable workflow (RFQ structure is similar across projects)
5. Strong ROI story

**Next Steps:**
1. [x] Generate BidMaster persona
2. [ ] Build RFQ parser prototype
3. [ ] Create supplier database schema
4. [ ] Design onboarding flow
5. [ ] Find pilot customer (Matt's network?)

---

## Implementation Checklist

### Phase 1: Build (Target: Week 1-2)
- [x] Generate persona with Prometheus
- [ ] Define onboarding flow
- [ ] Build RFQ parser (PDF extraction)
- [ ] Create supplier database
- [ ] Implement quote request automation
- [ ] Build comparison matrix generator
- [ ] Create bid response template system
- [ ] Internal testing with sample RFQs

### Phase 2: Pilot (Target: Week 3-4)
- [ ] Identify pilot customer
- [ ] Deploy pilot instance
- [ ] Process first 5 real RFQs together
- [ ] Weekly check-ins
- [ ] Iterate based on feedback

### Phase 3: Launch (Target: Week 5+)
- [ ] Build landing page
- [ ] Create demo video
- [ ] Set up billing (Stripe)
- [ ] Launch LinkedIn campaign
- [ ] First paying customer
- [ ] Case study from pilot

---

*Construction RFQ Vertical — Tier 4 Intelligence*
