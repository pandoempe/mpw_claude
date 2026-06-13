---
name: daily-update-desktop
description: Generates a daily intelligence briefing for a company using Claude's built-in web search only — the web/Desktop counterpart of the daily-update skill, for environments with no local filesystem and no API keys. It takes the user's search context (an attached file, the project's instructions, or text pasted into the chat), researches recent competitor/regulatory/industry/macro developments with WebSearch, and writes a briefing covering a news summary, impact to company risk, and concrete mitigation steps — shown in the chat first, then optionally exported to a downloadable Word document. Use this skill whenever a Claude.ai web or Claude Desktop user asks for their "daily update", "daily briefing", "morning briefing", "today's report/digest", wants to "catch up on news relevant to the company", or asks to check on competitors, industry shifts, or regulatory developments that could affect the business — even if they don't say "daily update" by name.
---

# Daily Update (Web / Desktop)

Produces a daily intelligence briefing tailored to a company's industry,
competitors, customers, and risk areas, using **Claude's built-in web search as
the only research channel**. This is the Claude.ai-web / Claude-Desktop sibling
of the `daily-update` skill. It assumes the constraints of that environment:

- **No persistent local filesystem** — there's no `.claude/` folder to read a
  saved config from or to archive reports into. Files you create live in the
  session's sandbox and reach the user as **downloads**.
- **No OpenRouter / Perplexity** — there's no API key and no bundled script, so
  research is done entirely with the `web_search` tool.
- **No cross-day continuity** — each run is a standalone briefing.

If you are running in Claude Code with a real local filesystem and an
`OPENROUTER_API_KEY`, use the `daily-update` skill instead — it adds a Perplexity
research pass and a persistent dated archive.

## Why this workflow exists

Staying on top of news that could affect a company is tedious — it means
tracking competitors, regulators, supply chains, customer industries, and
macro/FX shifts, then translating raw headlines into "so what does this mean for
us, and what should we do about it." This skill does the research and the
first-draft synthesis. The guiding value is that **validity of sources matters
more than convenience**: every claim in the briefing should trace to a real,
linkable source the user can check themselves, not a confident-sounding summary.

## Step 1 — Get the search context

The search context is the user's source of truth for *what* to research: a
company profile, business model, competitors, topics/keywords, customer
industries, risk areas, regions, and which languages/outlets to use. On
web/Desktop there's no saved file to read, so find it in this order and **tell
the user which source you used**:

1. **An attached/uploaded file** in the conversation (e.g. a `search_context.md`
   the user dragged in). If present, use it.
2. **The project's custom instructions** — if this is running inside a Claude
   Project whose instructions contain the company profile/competitors/topics,
   use those.
3. **Pasted into the chat** — if neither of the above is present, ask the user to
   paste their context. Offer them the choice plainly, e.g.: *"I can take your
   search context as an attached file, from your project instructions, or pasted
   here. Which would you like? If it's easier, here's a short template to fill
   in,"* and offer the template from `assets/search_context_template.md`.

Do **not** invent a context or run a generic news sweep if none is provided — a
briefing built on a guessed profile is worse than no briefing, because it looks
authoritative while being untethered from what the user actually cares about.
If the context is clearly a blank/unfilled template (bracketed placeholders in
the Company, Competitors, or Topics sections), pause and ask the user to fill it
in before researching.

Once you have it, read it fully before searching. Every topic you investigate
should trace back to something the context actually names — that's what keeps
the briefing about *their* business rather than a generic roundup.

### Privacy — never transmit the company's real name

The context is written to be **anonymized**: it describes the company
generically (e.g. "an Indonesian ICT company comparable to Telkom Sigma, AWS, or
Metrodata") rather than naming it. Honor that. Don't ask for the real name,
don't write it into any web search query, and if you happen to know it, keep it
out of both your searches and the briefing — refer to "the company" throughout.
Web searches leave your machine; the research is about the company's
*environment* (competitors, regulators, macro), so the name adds nothing and
only leaks identity.

## Step 2 — Research with web search

Plan focused searches from the context rather than one broad sweep — narrow,
specific queries ("competitor X acquisition / restructuring [month] [year]",
"[regulator] new rule [topic]", "[currency] rate [central bank] this week")
surface checkable, dated claims; vague ones return generic filler. Cover each
area the context calls out: the company's industry and products, the named
competitors, the tracked topics/keywords, the customer industries, and the
regions of concern.

**Window:** target roughly the **last 5–7 days** and then keep only what's
genuinely recent in the briefing. Very narrow phrasings ("last 24 hours") tend
to under-return; search a little wider and filter yourself. Use today's date to
frame "this week."

**Customer-industry lens — tie it to revenue.** Developments in the customers'
industries matter only insofar as they could change how much those customers buy
from the company. A customer segment under financial pressure, a regulatory
squeeze, or a demand shift may cut or grow its spend — that revenue linkage is
the lens, not customer-industry news for its own sake.

**Languages — search English *and* every language the context lists, for every
topic.** Web search skews toward US/English results, so an English-only pass
systematically under-covers non-English markets. Read the "News languages &
preferred sources" section: if it lists languages (e.g. Bahasa Indonesia,
Mandarin), run at least one English query *and* at least one native-language
query per area, using local terms. For example in Bahasa Indonesia: a power
outage → `pemadaman listrik PLN gangguan [bulan] [tahun]`; a competitor → its
name plus `akuisisi`, `merger`, `restrukturisasi`, `anak usaha`, `dividen`.
Local-language outlets reliably break regional regulator notices, infrastructure
disruptions, and domestic competitor disclosures the English pass misses. If the
section says "English only," search English only.

**Honor preferred/avoided outlets.** Favor the trusted outlets the context names
(use `allowed_domains` to focus on them where it helps — wire services,
official regulator sites, company IR pages, named local outlets) and don't lean
on sources the user flagged to avoid.

If web search is unavailable or returns nothing usable, say so plainly and ask
the user to enable web search rather than filling the gap with unsourced claims.

## Step 3 — Judge sources before you write

The briefing's value rests on source quality, so weigh what you find:

- **Corroborate the consequential or surprising.** A big M&A figure, a policy
  reversal, or a central-bank move should be confirmed against a source you can
  link directly before it goes in as fact. A confident, specific claim you can
  only find in one weak place is a fabrication candidate — omit it, or include it
  **explicitly flagged as unverified** if it's important enough that the user
  should know it's circulating.
- **Judge each source on its merits.** A wire-service report, a regulator's
  official notice, and a company's own release are about as solid as it gets; a
  single blog repeating a rumor is not.
- **Surface disagreement instead of hiding it.** If two credible sources (or an
  English and a local-language one) conflict on a fact, say so in the briefing
  rather than silently picking one.

## Step 4 — Write the briefing in the chat

Show the full briefing **directly in the chat first** — that's the primary
deliverable; the user reads it immediately. Use today's actual date in the
title. Use this structure:

```markdown
# Daily Update — [Day, Month Date, Year]

## News Summary
[Organized by theme/topic from the context. For each item: what happened, when,
and why it's relevant — in plain language, not copy-pasted headlines. Cite the
source inline, e.g. "(Reuters, June 8 2026)".]

## Impact to Company Risk
[Organized by the risk areas the context names (regulatory, reputational,
operational, financial, competitive, etc.). For each: explain *concretely* how
today's developments could affect this specific company — connect news to
consequences rather than restating it. Treat *customer-side* risk as a
first-class category: a customer that cuts budgets, loses a license, or shifts
strategy is a direct revenue risk even if the company itself wasn't named.]

## Mitigation Needed
[Concrete, prioritized, actionable recommendations — what someone should
actually do this week. Avoid "monitor the situation"; say what to monitor, who
to inform, or which decision to revisit.]

## Sources
[Every source as a markdown link with a one-line note on its type — e.g.
"[Reuters: Title](url) — wire service" or "[Regulator notice](url) — primary
source". This is what lets the user judge validity, which is what they care
about most.]
```

The "Impact to Company Risk" and "Mitigation Needed" sections are where your
judgment matters most: connect external news to *this* company's situation as
described in the context, and think through second-order effects rather than
stopping at the obvious. Keep the tone direct and decision-useful — write it the
way you'd brief someone who has to act on it today.

## Step 5 — Offer the Word download

After the briefing is in the chat, **ask the user whether they'd like a Word
(`.docx`) copy to download** — don't generate it unprompted, since on web/Desktop
the file is an extra artifact they may not need. If they say yes:

- Write the markdown briefing to the session's output folder (e.g.
  `/mnt/user-data/outputs/YYYY-MM-DD-daily-update.md`) and produce a
  `YYYY-MM-DD-daily-update.docx` from it.
- Generate the `.docx` with whatever document tooling the environment provides —
  the `docx` skill if it's available, otherwise `python-docx`, otherwise convert
  the markdown with `pandoc` if present. Don't hand-assemble Word XML.
- Give the user the download link(s). If `.docx` generation isn't possible in the
  sandbox, fall back to offering the `.md` file and say why, rather than silently
  skipping it.

## Notes

- There is no archive on web/Desktop — once the session ends the files are gone.
  If the user wants to keep the briefing, they should download it (or copy the
  chat text). Mention this only if relevant.
- Each run is standalone; don't claim to be comparing against "yesterday's"
  report unless the user actually attached one.
