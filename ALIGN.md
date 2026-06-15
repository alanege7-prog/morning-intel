# ALIGN.md — Locked Decisions

This file records all decisions that have been made and approved by Alan. Nothing here changes without Alan's explicit sign-off.

---

## Decision Log

### Session Zero — Project Foundation

**Decision 1: Project purpose**
This agent is built for Alan personally as an internal strategy and opportunity scouting tool. It is not a product, newsletter, or client-facing tool. All design decisions serve a solo founder in early exploration stage.

**Decision 2: Industries covered**
AI, Cybersecurity, and Cloud. No other industries added without Alan's approval.

**Decision 3: Output style**
Semi-opinionated. The agent provides context and flags what matters with a founder lens, but leaves final judgment to Alan. Not fully opinionated, not purely factual.

**Decision 4: Delivery channel**
Telegram. WhatsApp was considered and rejected due to setup complexity. Telegram chosen for zero cost, free bot API, rich formatting, and ability to send to multiple chats and groups.

**Decision 5: Delivery schedule**
- Daily brief: 19:00 CET/CEST every day Monday through Saturday
- Weekly digest: 19:00 CET/CEST every Sunday
Timezone must auto-adjust for daylight saving.

**Decision 6: Multi-recipient delivery**
The agent sends to multiple Telegram chat IDs and group chats simultaneously. Chat IDs are managed via .env file. Scout owns the source registry but Alan owns the recipient list.

**Decision 7: AI model**
Claude API only. claude-sonnet-4-20250514 for all analysis. OpenAI Codex was considered and rejected — keeping stack clean and consistent with Claude Code build environment.

**Decision 8: Agent team**
Three agents serve this project:
- Hans — Head of Architecture and Challenger
- Exo — CTO and Implementer
- Scout — Head of Sources (new agent, owns SOURCES.md)
Alan remains CEO and sole decision-maker.

**Decision 9: V1 scope**
Phase 1 only. The three features locked for V1 are:
1. Daily news with White Space scoring
2. Early Adopter Advantage flagging
3. Skill/tool tracker
Velocity Signal and Weekly Synthesis pattern analysis are Phase 2. Do not build Phase 2 during Phase 1.

**Decision 10: Source count**
28 curated sources across 6 categories. Full list lives in SOURCES.md and is owned by Scout. No source added or removed without Scout updating SOURCES.md and Alan approving.

**Decision 11: Tech stack**
Python + Claude API + Telegram Bot API. No additional AI tools or APIs in V1.

**Decision 12: Development environment**
VS Code with Claude Code running in integrated terminal. Local development first, Railway for cloud deployment if needed.

---

## What Is NOT Decided Yet
- Whether to deploy to cloud (Railway) or keep local cron — Exo to recommend after V1 is working
- Exact Telegram chat IDs — Alan provides these during setup
- Whether to add a simple web dashboard in Phase 2 — deferred

---

## Change Protocol
Any change to a locked decision must be:
1. Proposed by Hans or Alan
2. Discussed with the relevant agent
3. Approved explicitly by Alan
4. Recorded here with the session date
