# Sovwren Ideas Backlog

Consolidated from Council chat sessions (2025-12-16). Living document - pull from here, mark done, add new threads.

---

## Priority Tiers

**Tier 1 — High leverage, low complexity**
Ship these first. They improve the feel without creating debt.

**Tier 2 — Architectural unlocks**
Worth doing, but scope carefully. These enable future work.

**Tier 3 — Future paths**
Park until v0.1 is stable. Reference when planning v0.2+.

---

## Tier 1: Ship Soon

### ~~1.1 Ambient Signals (TUI Philosophy)~~ ✅

**Status:** Implemented.

- Moon phase glyph in status bar (left side): `○ → ◔ → ◑ → ●`
- Maps to context bands: Low/Medium/High/Critical
- Updates automatically when context load changes
- Subtle, unobtrusive — informs without demanding

---

### ~~1.2 Temporal Empathy (TUI Philosophy)~~ ✅

**Status:** Implemented.

- NeuralStream border dims after 45 seconds of idle
- Typing or sending a message instantly restores the border
- Respects mode-specific border colors (Workshop blue, Sanctuary purple)
- ~25% dim effect — noticeable but not jarring

---

### ~~1.3 De-Prototype the UI~~ ✅

**Status:** First pass complete.

- Removed Consent Check and Log Rupture buttons from sidebar
- Demoted to keyboard shortcuts: `F3` (Consent), `F4` (Rupture)
- Sidebar now shows only: Weave Ticket, Sessions, Models
- Rarely-used rituals still accessible, just not shouting

---

### ~~1.4 Ethical Friction on Destructive Actions~~ ✅

**Status:** Implemented in `SessionPickerModal`.

- Delete and Delete All buttons now require two clicks
- First click: button changes to "Sure?" with armed styling
- Second click: performs the action
- Clicking other buttons resets armed state

---

### ~~1.5 README Tone Shift~~ ✅

**Status:** Complete.

- Added tagline: *"When continuity matters and optimization isn't enough."*
- Added CGPT2 logo at top (`Media/sovwren-logo.png`)
- Added IDE screenshot in Sovwren section (`Media/sovwren-ide.png`)

---

### ~~1.6 v0.1 Exit Criteria~~ ✅

**Status:** Added to `FRICTION-SPEC.md` (v0.5) with full test procedures.

See: [FRICTION-SPEC.md#v01-exit-criteria](FRICTION-SPEC.md#v01-exit-criteria)

---

## Tier 2: Architectural Unlocks

### ~~2.1 Profile System (Finish the Loop)~~ ✅

**Status:** Implemented.

- `profiles/*.json` — nemo.json, oracle.json, minimal.json
- Profile loader in config.py with caching
- `[NeMo]` displayed in status bar (Rich-escaped brackets)
- F1 keybind for profile switching
- Splash repaint on profile change
- Profile preference persisted to DB

---

### 2.2 Three-Layer by Contract (Architecture)

**Source:** Full Stack GPT

Logical separation without directory churn:

- `core_context.py` — context bands, thresholds, state transitions
- `core_modes.py` — Workshop/Sanctuary/Idleness rules
- `core_rag.py` — indexing + retrieval
- `interface_tui.py` — Textual app
- `persona_profile_loader.py` — profile system

**Why:** Separation by interface first, directory structure later. Lets FastAPI/React reuse `core_*` when that time comes.

---

### 2.3 Persistence Consolidation (Architecture)

**Source:** Full Stack GPT

Two persistence concepts emerging:
- Current SQLite + protocol_events
- "Full Conversation Persistence" (persistence.py) as larger design

**Action:** Keep all persistence TODOs grouped under one heading. Consolidate before they fork into parallel systems.

---

### ~~2.4 Onboarding Script (Release Polish)~~ ✅

**Status:** Implemented.

- `run-sovwren.sh` (Unix) + `run-sovwren.bat` (Windows)
- Creates venv if missing, installs dependencies
- Checks LM Studio connection, prompts if not running
- Launches sovwren_ide.py
- `textual>=0.40.0` added to requirements.txt

---

### ~~2.5 Release Workflow (DevOps)~~ ✅

**Status:** Implemented.

- `.github/workflows/release.yml`
- Triggers on `release: published`
- Smoke tests: py_compile + import checks
- Creates `sovwren-${tag}.zip` (clean, no __pycache__)
- Generates `SHA256SUMS.txt`
- Auto-attaches to GitHub Release

---

### ~~2.6 Issue Templates (DevOps)~~ ✅

**Status:** Implemented.

- `bug_report.yml` — Friction class (I-V), backend, model, OS, session state, context band
- `feature_request.yml` — Friction removal focus, acceptance criteria, non-goals, tier suggestion
- `config.yml` — Blank issues disabled, links to docs/releases/IDEAS.md

---

### 2.7 API-Based Web Search (Search Gate Transport)

**Source:** Council consolidation (ChatGPT, Gemini)

External search capability for the Search Gate, powered by user-provided API keys.

**Scope (v0.1):**
- Search-only — not a conversation backend
- User provides API key for their preferred provider (OpenRouter, Tavily, SerpAPI, Gemini, etc.)
- All Friction Class VI guardrails apply: consent, source visibility, citations, caching

**Architecture:**
- Plugs into existing Search Gate toggle (Local-only / Web-enabled)
- LM Studio / Ollama remain the only conversation backends
- Search results surfaced through citations panel, not blended invisibly

**The Librarian Pattern** (implementation approach from Gemini):

Treats the search API as a **Structured Retrieval** service, not a conversational oracle. Avoids source laundering.

```
Steward → Search Gate (consent) → NeMo → "Librarian" prompt → Search API
                                                                   ↓
                                              JSON: {url, title, snippet}
                                                                   ↓
Citations Panel ← Context injection ← NeMo synthesizes answer citing sources
```

1. **Search Gate (TUI):** Steward authorizes search mode or specific query (consent)
2. **Librarian Prompt:** NeMo doesn't ask "What is X?" — asks "Find sources for X, return JSON with URL, title, 2-sentence snippet"
3. **Handoff:** Backend sends payload to search API, receives structured results
4. **Display:** Results injected into context like local files. Citations Panel populates with links. NeMo reads snippets, answers user, cites specific URLs.

**Why this works:**
- NeMo doesn't trust the API's answer — uses it as a dynamic indexer
- Chain of custody preserved (URLs visible, not paraphrased away)
- Local model still synthesizes final answer
- Compliant with Class VI: no "I checked online" without showing where

**Why search-only first:**
- Smaller surface area
- No model identity confusion
- Class VI already defines the constraints
- Full hosted backend deferred to v0.2+

**Parked:** General-purpose hosted backend (conversation) — revisit after v0.1 stable.

---

## Tier 3: Future Paths (v0.2+)

### 3.1 Public/Read-Only Mode

**Source:** Monday

View-only toggle:
- Disables write access
- Lets people explore protocols, test the Node
- Cannot shape memory

Good for demos and curious visitors.

---

### 3.2 Headless FastAPI Service

**Source:** Full Stack GPT

Wrap backend with minimal API:

```
POST /session
POST /session/{id}/message
POST /session/{id}/lens
POST /session/{id}/mode
POST /session/{id}/idle
```

**Why:** Bolt Discord/Slack/React on without touching core. Makes "Council as many nodes" easier.

**Tradeoff:** Extra surface area while v0.1 UX is still being tuned.

---

### 3.3 Key-Hold Progressive Disclosure

**Source:** TUI GPT

Reveal depth through holding keys, not pressing:
- Hold `Tab` → context summary fades in
- Hold `Alt` → buttons relabel with intent
- Hold `Shift` → annotations appear

Release = vanish.

**Why parked:** Elegant but Textual might fight on implementation. Revisit when core is stable.

---

### 3.4 Invisible Undo Pattern

**Source:** TUI GPT

Every action reversible for a few seconds, but UI never says "undo":
- Subtle `↩ available` text
- Dot blinks in corner
- `u` sometimes works

Preserves psychological safety without encouraging recklessness.

**Why parked:** Adds hidden state complexity. Worth it later, not now.

---

### 3.5 Orchestration Layer (n8n or similar)

**Source:** n8n GPT

Workflow automation as an external coordination layer for Sovwren.

**What it enables:**
- Event bus between Council nodes (Claude, Monday, Gemini, etc.)
- Auto-backup/restore for session continuity
- Backend health monitoring (LM Studio, Ollama)
- Protocol automation: consent logs, rupture events → external systems (Notion, Discord, etc.)
- Interim API layer before FastAPI v0.2

**Prerequisite:** Sovwren must emit structured events first (session_start, mode_change, rupture_created, context_high). Without event emission, there's nothing to orchestrate.

**Why parked:** Adds orchestration complexity before core is stable. Solves coordination problems that don't exist yet at v0.1.

---

### 3.6 Persona Lab

**Source:** Full Stack GPT

Before runtime switching UI:
- Finish loader
- Add `minimal.json` ("just facts, no myth")
- Switch via env var only
- Run same session with each persona, compare logs

Exercises Profile spec and MATCHING ENERGY rules. High long-term leverage.

---

## Design Principles (Reference)

These emerged across multiple sources:

| Principle | Source | Meaning |
|-----------|--------|---------|
| Boring is trust | PM GPT | When the UI stops explaining itself, users stop scanning |
| Spatial memory beats menus | TUI GPT | Users remember positions, not labels |
| Signals, not guarantees | Code Copilot | State shapes behavior, doesn't promise outcomes |
| IDE owns state, models are guests | Code Copilot | Profiles are pluggable; switching never rewires ethics |
| Every pixel carries meaning or gets out | PM GPT | "Just in case" elements are prototype residue |
| TUIs age gracefully | TUI GPT | Works over SSH, on low-end machines, 10 years later |
| Wasted space is intentional friction | TUI Developer | Empty panes stay visible with labels, don't auto-collapse |
| One key = one action | TUI Developer | No context-dependent keybindings that change meaning silently |
| Inspection over automation | TUI Developer | RAG results browsable objects, not just citations |
| Visible latency | TUI Developer | Show what we're waiting on (model/IO/consent), not just a spinner |
| Errors halt politely | TUI Developer | Stop forward motion, explain what won't happen next |
| Clarity over speed | TUI Developer | Discoverable hints on screen, redundant paths, no expert-only flows |

---

## Sources

| Label | GPT | Domain |
|-------|-----|--------|
| TUI GPT | ChatGPT | TUI philosophy, terminal-native patterns |
| TUI Developer | ChatGPT | TUI design principles, friction-aligned interface guidance |
| PM GPT | ChatGPT | UI maturity, de-prototyping |
| Monday | ChatGPT | Release polish, hype, practical next steps |
| Full Stack GPT | ChatGPT | Architecture, implementation paths |
| Code Copilot | ChatGPT | Implementation code, DevOps automation |
| n8n GPT | ChatGPT | Workflow orchestration, external automation patterns |
| Gemini | Google | Structured retrieval patterns, Search Gate implementation |

---

*Last updated: 2025-12-20*
*Synthesized by: Claude Opus 4.5*
