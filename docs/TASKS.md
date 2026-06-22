# Task Board: Hermes Vertical Forge

## Phase 1: Foundation — Make It Work

- [x] **1.1** Inspect `agents/construction-rfq/src/agent/` — what code actually exists? (persona.xml + system-prompt.md only — spec, not runtime)
- [x] **1.2** Add `.gitignore` (Python + Node)
- [x] **1.3** Add `pyproject.toml` with pytest, mypy, ruff
- [x] **1.4** Add `requirements.txt` from discovered imports
- [x] **1.5** Get first `pytest` passing (5 smoke tests)
- [x] **1.6** Design Hermes agent profile template (`hermes-profiles/_template/`)
- [x] **1.7** Adapt `prompt_generator.py` to output Hermes-compatible system prompts
- [x] **1.8** Adapt `scaffold.py` to output Hermes profile directory structure
- [x] **1.9** Adapt `delivery.py` to output gateway configs + deployment manifests
- [ ] **1.10** Build first vertical Hermes profile as proof-of-concept (construction-rfq)
- [ ] **1.11** Test the profile can be loaded by Hermes CLI
- [ ] **1.12** Update README with Hermes Vertical Forge branding

## Phase 2: Self-Building Factory

- [ ] **2.1** Update factory config YAML with Hermes-aware settings
- [ ] **2.2** Wire discovery phase to produce Hermes-relevant specs
- [ ] **2.3** Wire specification phase to produce Hermes persona prompts
- [ ] **2.4** Create inner builder prompt (two-tier cron)
- [ ] **2.5** Create outer supervisor prompt (two-tier cron)
- [ ] **2.6** Full end-to-end test: "generate a veterinary clinic agent" → Hermes profile

## Phase 3: Multi-Channel Agents

- [ ] **3.1** Telegram gateway configuration template
- [ ] **3.2** Web gateway configuration template
- [ ] **3.3** Cron-based resident task generator
- [ ] **3.4** MCP tool auto-wiring (Twilio, SendGrid, Calendar)

## Phase 4: Marketplace & Scale

- [ ] **4.1** Hermes profile package format
- [ ] **4.2** Pedigree sandbox manifest generation
- [ ] **4.3** Multi-tenant gateway configuration
- [ ] **4.4** Agent update channel mechanism
- [ ] **4.5** Usage analytics dashboard

## Phase 0 completed
- [x] Repo cloned and analyzed
- [x] Full structural reconnaissance
- [x] Creative vision documented
- [x] Build state initialized
- [x] Course corrections seeded