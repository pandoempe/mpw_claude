# Daily Update (Web / Desktop) — Claude Skill

A [Claude.ai](https://claude.ai/) **web and Claude Desktop** skill that generates a **daily intelligence briefing** tailored to your company, industry, competitors, and risk areas. It researches recent developments using **Claude's built-in web search** (no API keys, no external research service), then synthesizes everything into a briefing covering news, risk impact, and concrete mitigation steps — shown **in the chat first**, with an optional **Word (`.docx`) download**.

This is the web/Desktop counterpart of the [`daily-update`](../daily-update/) Claude Code skill. It assumes the constraints of the Claude.ai sandbox: **no persistent local filesystem**, **no `OPENROUTER_API_KEY`**, and **outputs that reach you as downloads** rather than saved files. If you're running in Claude Code on your own machine — with a local filesystem and an OpenRouter key — use `daily-update` instead; it adds a Perplexity research pass and a persistent dated archive.

The guiding principle is the same: **validity over convenience.** Every claim in the briefing should trace back to a real, linkable source you can check yourself — not be taken on faith from a single AI summary.

---

## What it does

When you ask for your "daily update" (or "morning briefing", "today's digest", "catch me up on competitor/industry news", etc.), the skill:

1. **Gets your search context** — your single source of truth for *what* to track. On web/Desktop there's no saved config file, so it looks for it in this order and tells you which it used:
   - an **attached/uploaded file** in the chat,
   - your **Claude Project's custom instructions**, or
   - text you **paste into the conversation**.
2. **Researches with web search** — builds focused queries from your context and runs them **in English and every language you list**, covering your industry, competitors, tracked topics, customer industries, and regions.
3. **Judges sources** — corroborates surprising or consequential claims, flags anything it can only find in one weak place as unverified, and surfaces disagreements between sources rather than silently picking one.
4. **Writes the briefing in the chat** — the primary deliverable, shown inline so you can read it immediately.
5. **Offers a Word download** — after the briefing, asks whether you'd like a `.docx` copy to download.

The briefing has four sections: **News Summary**, **Impact to Company Risk** (including customer-side revenue risk), **Mitigation Needed** (concrete, prioritized actions), and **Sources** (every link, annotated by source type).

> **Why multilingual search matters:** the most timely and granular reporting — local regulators, regional infrastructure disruptions, domestic competitor moves — often breaks first (and sometimes only) in the local-language press before it reaches English-language wires, if it ever does. English-only research is a known blind spot. So the skill searches in English **plus every language you list** in the context's *News languages & preferred sources* section, for every topic. List "English only" there if that's all you need.

---

## Requirements

| Requirement | Notes |
|---|---|
| **Claude.ai web or Claude Desktop** | This skill is built for the Claude.ai sandbox. (It also runs in Claude Code, but there the `daily-update` skill is the better fit.) |
| **Web search enabled** | The skill's only research channel is Claude's built-in web search. If it's turned off, enable it in your Claude settings — the skill will tell you rather than inventing unsourced claims. |
| **Your search context** | Have it ready as an attached file, in your project instructions, or to paste. A blank template ships at [`assets/search_context_template.md`](assets/search_context_template.md). |

No API key, Python, or Pandoc needed. The Word download uses whatever document tooling the sandbox provides.

---

## Setup

1. **Install the skill** on Claude.ai / Desktop (upload the packaged `.skill`, or add it however your workspace manages skills).

2. **Prepare your search context.** Start from the bundled [`assets/search_context_template.md`](assets/search_context_template.md) and fill in every bracketed placeholder with your company profile, competitors, topics, customer industries, risk areas, regions, and languages. **The more specific you are, the more useful the briefing.** Then make it available one of three ways:
   - **Attach it** to the chat when you run the skill, or
   - **Paste it** into your Claude **Project's custom instructions** (handy if you run the briefing in a dedicated project), or
   - **Paste it** directly into the message.

   The skill won't run on a guessed or blank context — that's by design, so you don't get an authoritative-looking briefing untethered from what you actually care about.

> **Privacy — keep the company name out.** The template deliberately describes the company *generically* (e.g. "an ICT company comparable to Telkom Sigma, AWS, or Metrodata") rather than naming it. Web searches leave the sandbox, and the research is about your *environment* (competitors, regulators, macro), so the name adds nothing and only leaks identity. The skill won't transmit your real company name in searches or the briefing.

---

## Usage

Just ask Claude naturally:

> Give me my daily update
> Morning briefing please — here's my context [attach file]
> Catch me up on anything relevant to the company today
> Any competitor or regulatory news I should know about?

The skill triggers on those intents even when you don't say "daily update" by name.

### Output

- The full briefing appears **inline in the chat** — read it immediately.
- If you say yes to the Word copy, you get a **`YYYY-MM-DD-daily-update.docx` download** (with a `.md` fallback if `.docx` can't be generated in the sandbox).
- **There is no archive.** Once the session ends, the files are gone — download the briefing or copy the chat text if you want to keep it. Each run is a standalone, fresh briefing (no day-to-day continuity).

---

## Configuration & customization

- **What to track** is driven entirely by your search context — edit that to change coverage; you never edit the skill itself for routine changes.
- **Multilingual coverage (configurable).** Research runs in English plus whatever languages you list in the context's *News languages & preferred sources* section, so local-market events aren't missed. Set it to "English only" if you don't need local-language coverage.
- **Trusted sources.** Name outlets you vouch for (Reuters, Bloomberg, AP, official regulators, company IR pages, trade press) and any to avoid in the same section; the skill favors the trusted ones.

---

## How it differs from the `daily-update` (Claude Code) skill

| | `daily-update` (Claude Code) | `daily-update-desktop` (web / Desktop) |
|---|---|---|
| **Research** | Perplexity Sonar (via OpenRouter) **+** WebSearch cross-check | **WebSearch only** |
| **Context source** | Saved `assets/search_context.md` file | Attached file, **project instructions**, or pasted text |
| **Output** | Markdown **+** Word, saved to `.claude/daily-update-reports/` | Shown **in chat first**, then optional Word **download** |
| **Continuity** | Reads prior reports to dedupe day-to-day | **None** — each run standalone |
| **Needs** | OpenRouter key, Python, Pandoc | Nothing beyond web search being enabled |

---

## File structure

```
daily-update-desktop/
├── SKILL.md                              # The skill definition / instructions Claude follows
├── README.md                             # This file
└── assets/
    └── search_context_template.md        # Blank template to fill in and supply each run
```

---

## Privacy & cost notes

- Your web search queries leave the sandbox. Don't put the real company name (the template is built to avoid it) or confidential internal data into your context beyond what you're comfortable searching the open web with.
- There's **no paid API call** — the skill uses only Claude's built-in web search. Cost is whatever your Claude plan already covers.
- Nothing is persisted server-side by the skill: the briefing lives in the chat and any download you save. When the session ends, sandbox files are cleared.

---

## License

[MIT](../LICENSE) © 2026 Pandu Wibowo. Built as a skill for Anthropic's Claude; "Claude" and "Anthropic" are trademarks of Anthropic.
