# CLAUDE.md — Morning Intelligence Agent

## Project Overview
An automated weekly research agent that fetches, analyzes, and delivers a founder-focused intelligence brief every week via Telegram. Covers AI, Cybersecurity, and Cloud industries.

## The Team

| Agent | Role |
|-------|------|
| Alan | CEO and sole decision-maker. All final calls belong to Alan. |
| Hans | Head of Architecture and Challenger. Designs blueprints, challenges assumptions. |
| Exo | CTO and Implementer. Builds what Hans designs and Alan approves. |
| Scout | Head of Sources. Owns and maintains the source registry. |

## Decision Rule
Nothing gets built without Alan's approval. Hans designs, Exo challenges and builds, Scout maintains sources. No agent acts outside their role.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| AI Brain | Claude API (claude-sonnet-4-20250514) |
| Delivery | Telegram Bot API |
| Scheduler | Cron job (local) or Railway (cloud) |
| Source fetching | feedparser, requests, beautifulsoup4 |
| Environment | python-dotenv for secrets |

## Environment Variables Required
```
ANTHROPIC_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_IDS=id1,id2,id3
```

---

## Project Phases

### Phase 1 — V1 (current)
- [x] Fetch content from 28 curated sources
- [x] Score and analyze with Claude API (founder lens)
- [x] Format weekly digest
- [x] Deliver weekly digest via Telegram every Sunday 7pm CET

### Phase 2 — V2 (future, do not build yet)
- Velocity Signal scoring
- Weekly pattern synthesis
- Additional source layers

---

## Delivery Schedule

| Brief | Time | Day |
|-------|------|-----|
| Weekly digest | 19:00 CET/CEST | Sunday |

---

## Daily Brief Structure

Every daily brief must follow this exact structure:

```
🌅 MORNING INTEL — [DATE]

🔥 WHAT'S MOVING FAST
[2-3 items with context — what it is and why it matters for a founder]

💡 OPPORTUNITY GAPS
[2-3 underserved problems or white spaces emerging today]

⚠️ WATCH OUT
[1-2 things that could kill ideas or shift the landscape]

🛠️ NEW TOOLS & SKILLS
[Relevant tool drops, Claude features, certifications worth knowing]

📌 FOUNDER ACTION
[One concrete thing to research or decide today]
```

## Weekly Digest Structure

```
📊 WEEKLY INTEL DIGEST — [WEEK OF DATE]

🏆 TOP 3 SIGNALS OF THE WEEK
[Most important developments across AI, Cloud, Cyber]

🗺️ MARKET GAPS SPOTTED
[White spaces and opportunities that appeared this week]

📈 VELOCITY WATCH
[What is moving fastest right now]

🎯 WEEKLY FOUNDER FOCUS
[One strategic recommendation for the week ahead]
```

---

## Output Tone
Semi-opinionated. Provide context and flag what matters, but leave final judgment to Alan. Never just summarize — always add the founder lens: why does this matter for someone building in this space?

---

## Core Files

| File | Owner | Purpose |
|------|-------|---------|
| CLAUDE.md | All agents | Project rules and constraints |
| BLUEPRINT.md | Hans | Full technical spec and build status |
| ALIGN.md | Hans | Locked decisions |
| SESSION_LOG.md | Hans + Exo | Session history |
| SOURCES.md | Scout | Live source registry |
| AGENT_HANS.md | Hans | Hans identity and protocol |
| AGENT_EXO.md | Exo | Exo identity and protocol |
| AGENT_SCOUT.md | Scout | Scout identity and protocol |

---

## Hard Rules
- Never build Phase 2 features during Phase 1
- Never store API keys in code — always use .env
- Never add new sources without Scout's approval and SOURCES.md update
- All sessions must end with updated project files
- If anything is unclear, ask Alan before proceeding
