# Daily Update — Claude Code Skill

A [Claude Code](https://claude.com/claude-code) skill that generates a **daily intelligence briefing** tailored to your company, industry, competitors, and risk areas. It researches recent developments using the **Perplexity Sonar Pro** research model (via [OpenRouter](https://openrouter.ai/)), **cross-checks the findings with Claude's own web search** for source validity, and synthesizes everything into a dated Markdown + Word report covering news, risk impact, and concrete mitigation steps.

The guiding principle is **validity over convenience**: every claim in the report should trace back to a real, citable source you can check yourself — not be taken on faith from a single AI summary. In practice the cross-check step routinely catches stale figures and recycled old news that the research model alone would have reported as current.

---

## What it does

When you ask for your "daily update" (or "morning briefing", "today's digest", "catch me up on competitor/industry news", etc.), the skill:

1. **Reads your context file** (`.claude/skills/daily-update/assets/search_context.md`) — your single source of truth for *what* to track.
2. **Builds focused research questions** from that context and queries **Perplexity Sonar Pro** through OpenRouter.
3. **Cross-checks** the most consequential claims with `WebSearch`, corroborating surprising findings, filling gaps, and discarding stale or unsourced material.
4. **Writes a dated report** to `.claude/daily-update-reports/` as both Markdown and Word, and shows it to you inline.

The report has four sections: **News Summary**, **Impact to Company Risk** (including customer-side revenue risk), **Mitigation Needed** (concrete, prioritized actions), and **Sources** (every link, annotated by source type).

---

## Requirements

| Requirement | Notes |
|---|---|
| **Claude Code** | This is a Claude Code skill (lives under `.claude/skills/`). |
| **OpenRouter API key** | Set as the `OPENROUTER_API_KEY` environment variable. Get one at [openrouter.ai](https://openrouter.ai/). The skill uses `perplexity/sonar-pro` by default; each run is a paid API call. |
| **Python 3** | Runs the bundled `query_perplexity.py` (standard library only — no `pip install` needed). Falls back to the `py` launcher on Windows. |
| **Pandoc** | Used to convert the Markdown report to `.docx`. Install from [pandoc.org](https://pandoc.org/installing.html). If you don't need Word output, you can skip this and ask for Markdown only. |

---

## Setup

1. **Copy the skill** into your project (or user) skills directory so the path looks like:

   ```
   <your-project>/.claude/skills/daily-update/
   ```

2. **Set your OpenRouter key** (PowerShell example — persists for your user):

   ```powershell
   [System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', '<your-key>', 'User')
   ```

   Then restart your terminal so the variable is picked up. On macOS/Linux, export it in your shell profile instead.

3. **Create your context file.** Copy the bundled template alongside it inside the skill's `assets/` folder and fill it in:

   ```
   .claude/skills/daily-update/assets/search_context.md
   ```

   A starter template lives next to it at [`assets/search_context_template.md`](assets/search_context_template.md) — copy it to `assets/search_context.md` and replace every bracketed placeholder with your real company, competitors, topics, risk areas, and regions. **The more specific you are, the more useful the report.** The skill will refuse to run against an unfilled template — that's by design, to avoid burning a paid API call on a generic report.

---

## Usage

Just ask Claude Code naturally:

```
/daily-update
```

or simply:

> Give me my daily update
> Catch me up on anything relevant to the company today
> Any competitor or regulatory news I should know about?

The skill triggers on those intents even when you don't say "daily update" by name.

### Output

Reports are saved to:

```
.claude/daily-update-reports/YYYY-MM-DD-daily-update.md
.claude/daily-update-reports/YYYY-MM-DD-daily-update.docx
```

and shown inline in the conversation. Filenames are date-based, so **re-running on the same day overwrites that day's report** (the latest run wins). If you prefer versioned same-day files, that's a small change to Step 5 of `SKILL.md`.

---

## Configuration & customization

- **Deeper research on complex days.** Pass `perplexity/sonar-deep-research` as a second argument to the script for slower, multi-step retrieval on fast-moving situations. The skill decides when this is warranted, or you can ask for it.
- **Trusted sources.** The cross-check step can be focused on outlets you vouch for (Reuters, Bloomberg, AP, official regulators, company IR pages, trade press) via `WebSearch`'s `allowed_domains`.
- **What to track.** All of it is driven by `search_context.md` — edit that file to change coverage; you never edit the skill itself for routine changes.

---

## File structure

```
daily-update/
├── SKILL.md                              # The skill definition / instructions Claude follows
├── README.md                             # This file
├── LICENSE                               # MIT
├── scripts/
│   └── query_perplexity.py               # Sends the research prompt to Perplexity via OpenRouter
└── assets/
    ├── search_context_template.md        # Blank template — safe to publish
    └── search_context.md                 # YOUR filled-in config — do NOT publish (see below)
```

> ⚠️ **Heads-up:** your filled-in `assets/search_context.md` now lives **inside** the skill folder. Since it contains your real business context, **exclude it before publishing** (the `.gitignore` below handles this). The generated reports land in `.claude/daily-update-reports/` (outside the skill) and should also be kept private.

---

## Privacy & cost notes

- Your research prompts are sent to **OpenRouter → Perplexity**. Don't put secrets or confidential internal data into `search_context.md` beyond what you're comfortable sending to a third-party API.
- Each run makes at least one **paid** OpenRouter call (plus Claude's web searches). Sonar Pro is inexpensive for a daily cadence; `sonar-deep-research` costs more.
- Before publishing this skill to a public GitHub repo, make sure you're only sharing `SKILL.md`, `scripts/`, `assets/search_context_template.md`, `README.md`, and `LICENSE` — **not** your filled-in `assets/search_context.md` or any generated reports. The bundled `.gitignore` excludes `assets/search_context.md` for exactly this reason.

---

## License

[MIT](LICENSE) © 2026 Pandu Wibowo. Built as a skill for Anthropic's Claude Code; "Claude" and "Anthropic" are trademarks of Anthropic. Perplexity and OpenRouter are trademarks of their respective owners.
