# SOURCES.md — Source Registry
**Owner:** Scout
**Last updated:** 2026-06-01

This is the single source of truth for all sources the agent fetches. Only Scout updates this file, with Alan's approval.

---

## Priority Key
- 🔴 P1 — Must have, core signal, V1 required
- 🟡 P2 — High value, add in V1 if no issues
- 🟢 P3 — Nice to have, Phase 2

---

## Category 1 — Official Blogs & Changelogs (Daily)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 1 | Anthropic News | https://www.anthropic.com/news | Web | Free | 🔴 P1 | Model releases, API changes, Claude features |
| 2 | AWS What's New | https://aws.amazon.com/new/feed/ | RSS | Free | 🔴 P1 | Service launches, GA/preview signals |
| 3 | Google Cloud Blog | https://cloudblog.withgoogle.com/rss/ | RSS | Free | 🔴 P1 | Vertex AI, Gemini, platform launches |
| 4 | Azure Blog | azure.microsoft.com/en-us/blog | RSS | Free | 🔴 P1 | AI features, Copilot stack, OpenAI on Azure |
| 5 | OpenAI News | https://openai.com/blog/rss.xml | RSS | Free | 🔴 P1 | Model releases, API updates, policy shifts |
| 6 | GitHub Changelog | github.blog/changelog | RSS | Free | 🔴 P1 | Copilot, dev tooling, CI/CD, security features |

---

## Category 2 — High-Signal Newsletters (Weekly)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 7 | Import AI | importai.substack.com | RSS | Free | 🔴 P1 | Frontier research, policy, zero hype |
| 8 | The Batch | https://www.deeplearning.ai/the-batch | Web | Free | 🔴 P1 | Technical + business lens, weekly commentary |
| 9 | tl;dr sec | tldrsec.com | RSS | Free | 🔴 P1 | Security engineering digest, annotated links |
| 10 | SANS NewsBites | sans.org/newsletters/newsbites | Web | Free | 🔴 P1 | Expert-annotated cyber executive summary |
| 11 | Krebs on Security | krebsonsecurity.com | RSS | Free | 🔴 P1 | Deep breach investigations, market impact |
| 12 | TLDR AI | https://tldr.tech/api/rss/ai | RSS | Free | 🟡 P2 | Fast daily digest, major launches |
| 13 | Latent Space | latent.space | RSS | Free | 🟡 P2 | AI engineering, agent infra, pre-mainstream signals |
| 14 | Clouded Judgement | cloudedjudgement.substack.com | RSS | Free | 🟡 P2 | Cloud economics, SaaS metrics, infra demand |
| 15 | The Record | https://therecord.media/feed | RSS | Free | 🟡 P2 | Cyber policy, major incidents, intelligence focus |

---

## Category 3 — Research & Market Intelligence (Weekly/Monthly)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 16 | a16z AI | https://a16z.com/ai | Web | Free | 🔴 P1 | Market maps, enterprise adoption, capital flow |
| 17 | Wiz Research | https://www.wiz.io/blog/tag/research | Web | Free | 🔴 P1 | Cloud exposure, AI security, supply chain risk |
| 18 | Microsoft Security Blog | microsoft.com/security/blog | RSS | Free | 🟡 P2 | AI impact on attacker/defender workflows |

---

## Category 4 — Job Market Signals (Weekly)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 19 | LinkedIn Job Trends | linkedin.com/jobs | Web | Mixed | 🔴 P1 | Rising job titles = market gaps |
| 20 | CyberSeek | cyberseek.org | Web | Free | 🟡 P2 | Cyber role demand, workforce gaps |
| 21 | AWS Training & Certs | aws.amazon.com/training | Web | Free | 🟡 P2 | Certification demand, new skill proxies |

---

## Category 5 — OSS & Community Signals (Daily)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 22 | GitHub Trending | github.com/trending | Web | Free | 🔴 P1 | What developers are building — early tool signals |
| 23 | Hacker News | news.ycombinator.com | RSS | Free | 🔴 P1 | Show HN = early products, Ask HN = unmet needs |
| 24 | Product Hunt | producthunt.com | RSS | Free | 🟡 P2 | Daily AI/security launches, traction signals |
| 25 | Hugging Face Models | huggingface.co/models | Web | Free | 🟡 P2 | Open model releases, community adoption |
| 26 | Hugging Face Papers | https://huggingface.co/api/daily_papers | API | Free | 🟡 P2 | Research-to-product transition signals |

---

## Category 6 — Cybersecurity Feeds (Daily)

| # | Source | URL | Type | Cost | Priority | Signal |
|---|--------|-----|------|------|----------|--------|
| 27 | CISA KEV Catalog | https://www.cisa.gov/cybersecurity-advisories/all.xml | RSS | Free | 🔴 P1 | Actively exploited vulnerabilities — best open prioritization |
| 28 | The Hacker News | thehackernews.com | RSS | Free | 🔴 P1 | High-volume daily cyber feed |

---

## Fetch Schedule Summary

| Frequency | Sources |
|-----------|---------|
| Daily | 1,2,3,4,5,6,12,22,23,27,28 |
| Weekly | 7,8,9,10,11,13,14,15,16,17,18,19,20,21,24,25,26 |

---

## Scout's Change Protocol
1. Alan requests a source change (add, remove, or update)
2. Scout evaluates against quality bar: high-signal, free/automatable, non-duplicate
3. Scout updates this file
4. Scout logs the change in SESSION_LOG.md
5. Exo picks up the change automatically via source_loader.py on next run

---

## Sources on Watchlist (not yet added)
These sources were identified as valuable but excluded from V1 for specific reasons:

| Source | Reason excluded | Reconsider when |
|--------|----------------|-----------------|
| Stratechery | Paywalled | Phase 2 if Alan subscribes |
| Gartner | Heavily paywalled | Phase 2 |
| CB Insights | Paywalled | Phase 2 |
| Stanford AI Index | Annual report only | Pull manually each year |
| State of AI Report | Annual report only | Pull manually each year |
