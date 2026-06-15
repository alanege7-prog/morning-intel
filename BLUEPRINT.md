# BLUEPRINT.md — Morning Intelligence Agent

## Product Goal
An automated pipeline that runs every Sunday at 19:00 CET, fetches content from 28 curated sources across AI, Cloud, and Cybersecurity, passes it through Claude API with a founder-focused analysis prompt, and delivers a structured weekly intelligence digest to one or more Telegram chats or groups.

---

## System Architecture

```
[SCHEDULER] (cron / Railway)
      │
      ▼
[FETCHER] — pulls from 28 sources → raw_content.json
      │
      ▼
[ANALYZER] — sends to Claude API with founder prompt → scored_brief.json
      │
      ▼
[FORMATTER] — structures into daily or weekly template
      │
      ▼
[DELIVERY] — sends via Telegram Bot to all configured chat IDs
      │
      ▼
[LOGGER] — logs run status, errors, and delivery confirmation
```

---

## Folder Structure

```
morning-agent/
│
├── .env                        ← secrets (never commit)
├── .gitignore
├── requirements.txt
├── README.md
│
├── main.py                     ← daily entry point
├── weekly.py                   ← weekly digest entry point
│
├── fetcher/
│   ├── __init__.py
│   ├── rss_fetcher.py          ← handles RSS/Atom feeds
│   ├── web_fetcher.py          ← handles non-RSS sources
│   └── source_loader.py        ← loads and validates SOURCES.md
│
├── analyzer/
│   ├── __init__.py
│   ├── daily_analyzer.py       ← daily brief prompt and Claude call
│   └── weekly_analyzer.py      ← weekly digest prompt and Claude call
│
├── formatter/
│   ├── __init__.py
│   ├── daily_formatter.py      ← formats daily brief for Telegram
│   └── weekly_formatter.py     ← formats weekly digest for Telegram
│
├── delivery/
│   ├── __init__.py
│   └── telegram_delivery.py    ← sends to all configured chat IDs
│
├── logger/
│   ├── __init__.py
│   └── run_logger.py           ← logs runs, errors, delivery status
│
├── data/
│   ├── raw_content.json        ← fetched content (overwritten daily)
│   └── run_log.json            ← persistent run history
│
├── prompts/
│   ├── daily_prompt.txt        ← Claude prompt for daily analysis
│   └── weekly_prompt.txt       ← Claude prompt for weekly digest
│
├── CLAUDE.md
├── BLUEPRINT.md
├── ALIGN.md
├── SESSION_LOG.md
├── SOURCES.md
├── AGENT_HANS.md
├── AGENT_EXO.md
└── AGENT_SCOUT.md
```

---

## Module Specs

### fetcher/source_loader.py
- Reads SOURCES.md and parses the source list
- Returns structured list of sources with name, URL, type (rss/web), category, frequency

### fetcher/rss_fetcher.py
- Takes list of RSS sources
- Returns last 24 hours of entries per source
- Handles feed errors gracefully — log and continue, never crash

### fetcher/web_fetcher.py
- Takes list of non-RSS sources
- Scrapes headline-level content only — no full article reproduction
- Respects robots.txt

### analyzer/daily_analyzer.py
- Takes raw fetched content
- Sends to Claude API with daily_prompt.txt
- Returns structured JSON with 5 sections matching brief template
- Model: claude-sonnet-4-20250514
- Max tokens: 1500

### analyzer/weekly_analyzer.py
- Takes last 7 days of run logs
- Sends to Claude API with weekly_prompt.txt
- Returns structured weekly digest JSON
- Model: claude-sonnet-4-20250514
- Max tokens: 2500

### delivery/telegram_delivery.py
- Reads TELEGRAM_CHAT_IDS from .env
- Sends formatted message to every chat ID in the list
- Handles Telegram message length limits (4096 chars) — splits if needed
- Logs delivery confirmation per chat ID

### logger/run_logger.py
- Logs every run with timestamp, sources fetched, Claude tokens used, delivery status
- Appends to data/run_log.json
- Keeps last 30 days of logs

---

## Claude Prompt Design (daily)

The daily prompt must instruct Claude to:
1. Act as a strategic intelligence analyst with a founder lens
2. Identify what is genuinely new vs noise
3. Flag market gaps and white spaces explicitly
4. Score relevance for someone building in AI/Cloud/Cyber
5. Output in structured JSON matching the 5-section brief template
6. Be semi-opinionated — provide context and recommendation signals, not just facts

---

## Scheduler Setup

### Local (development)
```bash
# Weekly digest Sunday at 19:00 CET (18:00 UTC)
0 18 * * 0 cd /path/to/morning-agent && python weekly.py
```

### Cloud (production — Railway recommended)
- Deploy repo to Railway
- Set cron schedules in Railway dashboard
- Set environment variables in Railway dashboard

---

## Build Status Checklist

### Phase 1
- [x] Project structure created
- [x] requirements.txt defined
- [x] .env template created
- [x] source_loader.py built and tested
- [x] rss_fetcher.py built and tested
- [x] web_fetcher.py built and tested
- [x] weekly_prompt.txt written
- [x] weekly_analyzer.py built and tested
- [x] weekly_formatter.py built and tested
- [x] telegram_delivery.py built and tested
- [x] weekly.py wired end to end
- [x] run_logger.py built
- [x] End to end test run completed
- [x] First real delivery confirmed on Telegram
- [x] Cron/scheduler configured (Windows Task Scheduler, every Sunday 12:00 PM CDT = 19:00 CET)

---

## Known Risks
- Some sources may block automated fetching — web_fetcher must handle 403s gracefully
- Telegram message length limit is 4096 characters — formatter must handle splitting
- Claude API token costs must be monitored — log tokens per run
- Timezone handling for CET/CEST daylight saving must be explicit in scheduler
