---
name: vertical-research
description: Research and analyze vertical markets for AI agent opportunities. Use when discovering new verticals, mapping SMB pain points, analyzing competition, sizing markets, or creating VERTICAL.md specs. Triggers on requests like "research [industry] vertical", "find automation opportunities in [industry]", "create a vertical spec for [industry]".
---

# Vertical Research Skill

Research vertical markets to identify high-value AI agent opportunities for SMBs.

## Core Workflow

### Step 1: Industry Overview

Gather baseline information:

```
- Industry size (US SMB count, revenue range)
- Typical business structure (owner-operated, small teams)
- Tech adoption level (what tools they already use)
- Key trade associations and publications
```

### Step 2: Workflow Mapping

Identify the daily/weekly workflows:

```
For each major workflow:
- What triggers it?
- Who does it?
- How long does it take?
- What tools are involved?
- What goes wrong?
```

Focus on workflows that are:
- Repetitive (happens frequently)
- Rule-based (clear decision logic)
- Time-consuming (10+ hours/week)
- Error-prone (mistakes have cost)

### Step 3: Pain Point Analysis

Score each workflow pain point:

| Criteria | Score 1-5 |
|----------|-----------|
| Frequency (how often) | |
| Time cost (hours/week) | |
| Error cost ($ when wrong) | |
| Automation potential | |
| Integration complexity | |

**Total Score = Sum × Frequency Weight**

### Step 4: Competition Analysis

Research existing solutions:

```
- Direct competitors (AI-native solutions)
- Indirect competitors (general tools like Zapier)
- Industry-specific software (practice management, etc.)
- Pricing benchmarks
- Feature gaps
```

### Step 5: Agent Opportunity Definition

Define the agent scope:

```
Primary Function: [Single sentence]
Target Workflow: [Specific process]
Time Savings: [X hours/week]
Integration Points: [Systems to connect]
Complexity Level: [Low/Medium/High]
Estimated Price Point: [$X/year]
```

## Output Format

Generate a VERTICAL.md file:

```markdown
---
vertical: [industry-slug]
status: research
created: [date]
confidence: [low/medium/high]
---

# [Industry] Vertical Spec

## Market Overview
[2-3 paragraphs on market size, dynamics, tech adoption]

## Target Workflow: [Workflow Name]

### Current State
- Process description
- Time investment
- Pain points
- Current tools

### Desired State
- What "solved" looks like
- Key capabilities needed
- Success metrics

### Agent Scope
1. [Capability 1]
2. [Capability 2]
3. [Capability 3]
...

### Integration Requirements
- [System 1]: [What/Why]
- [System 2]: [What/Why]

### Pricing Model
- Base price: $X/year
- Add-ons: [list]
- Justification: [ROI calculation]

### Competition
- [Competitor 1]: [Price] — [Strengths/Weaknesses]
- [Competitor 2]: [Price] — [Strengths/Weaknesses]
- Gap: [What's missing]

## Risk Assessment
- Technical risks: [list]
- Market risks: [list]
- Regulatory considerations: [list]

## Recommendation
[Go/No-Go with reasoning]
```

## Research Sources

### Primary Sources
- Industry trade publications
- Trade association reports
- Reddit/forums where owners discuss pain points
- LinkedIn groups
- G2/Capterra reviews of existing tools

### Secondary Sources
- IBISWorld industry reports
- Census Bureau business statistics
- SBA industry data
- Competitor pricing pages

## Example Research Prompts

### For Market Overview
```
"How many [industry] SMBs exist in the US? What's their typical revenue range and team size?"
```

### For Workflow Discovery
```
"What does a typical day look like for a [industry] office manager? What tasks take the most time?"
```

### For Pain Points
```
"What do [industry] owners complain about on Reddit/forums? What's broken about their current tools?"
```

### For Competition
```
"What software do [industry] businesses use for [workflow]? What are the top complaints in reviews?"
```

## Quality Checklist

Before finalizing a VERTICAL.md:

- [ ] Market size is quantified with sources
- [ ] Target workflow is specific (not "everything")
- [ ] Time savings are realistic and defensible
- [ ] Integration points are identified
- [ ] Pricing is benchmarked against alternatives
- [ ] Competition is researched with actual products
- [ ] Risks are honestly assessed
- [ ] Recommendation is clear

## References

See `references/` for:
- `industry-templates.md` — Pre-researched industry overviews
- `pricing-benchmarks.md` — SaaS pricing data by vertical
- `integration-catalog.md` — Common SMB tools and their APIs
