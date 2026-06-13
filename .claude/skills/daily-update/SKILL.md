---
name: daily-update
description: Generates a comprehensive daily intelligence briefing by researching the company, industry, competitors, topics, and risk areas defined in .claude/skills/daily-update/assets/search_context.md, using a user-selected Perplexity Sonar research model (via OpenRouter) cross-checked with WebSearch for source validity. Produces a dated markdown report covering a news summary, impact to company risk, and concrete mitigation steps. Use this skill whenever the user asks for their "daily update", "daily briefing", "morning briefing", "today's report/digest", wants to "catch up on news relevant to the company", or asks to check on competitors, industry shifts, or regulatory developments that could affect the business — even if they don't say "daily update" by name.
---

# Daily Update

Produces a daily intelligence briefing tailored to the user's company, industry,
competitors, and risk areas — defined once in
`.claude/skills/daily-update/assets/search_context.md` — by
researching recent developments via the Perplexity Sonar research model
(through OpenRouter) and Claude's own web search, then synthesizing everything
into a dated markdown report covering news, risk impact, and mitigation steps.

## Why this workflow exists

Staying on top of news that could affect a company is tedious — it means
tracking customer industry, competitors, regulators, supply chains, and broader industry shifts
every day, then translating raw headlines into "so what does this mean for us,
and what should we do about it." This skill automates the research and the
first-draft synthesis, while keeping the user firmly in control of source
quality. The user has been explicit that **validity of sources matters more to
them than convenience** — every claim in the report should be traceable to a
real, citable source they can independently check, not just taken on faith from
a single AI-generated summary.

## Step 1 — Read and validate the context file

Look for `search_context.md` in this skill's own `assets/` folder
(`.claude/skills/daily-update/assets/search_context.md`). This file is the
user's single source of truth for *what* to research: an anonymized company
profile, business model, product cycle, customer, industry, competitors,
topics/keywords, risk areas, and regions of concern.

**Privacy: the context file deliberately does not name the company.** The
Company section describes it generically by peer comparison (e.g. "an ICT
company comparable to Telkom Sigma, AWS, or Metrodata") so the user's identity
never leaves the machine. Don't ask the user for the real name, don't infer and
write it anywhere, and if you happen to know it from prior context, never
include it in research prompts, web searches, or the report itself — refer to
"the company" throughout.

- If the file is missing, or the **required** sections (Company, Competitors,
  Topics) still contain bracketed placeholder text like `[Generic description by peer comparison, ...]`,
  **stop here**. Tell the user the file needs to be filled in first —
  `assets/search_context.md` is the live config the user maintains, and a fresh
  template sits alongside it at `assets/search_context_template.md` if they need
  to start over from a blank copy. Running a search against an empty or templated
  context produces a generic, low-value report and burns a paid API call for
  nothing — pausing here is the right call, not a limitation to work around.
  A leftover placeholder in an *optional* section (e.g. "Notes for Claude")
  does **not** count as unfilled — don't refuse a real config over it.
- If it looks filled in, read it fully before researching anything. Every topic
  you investigate should trace back to something the user actually told you to
  track — this keeps the report focused on what matters to *their* work, not a
  generic news roundup.

Then check `.claude/daily-update-reports/` for continuity:

- **If a report for *today* already exists**, ask the user (via `AskUserQuestion`)
  whether to skip (keep the existing report), fully re-run, or deep-dive a
  specific thread — before spending a paid API call on a likely-duplicate.
- **Read the most recent prior report** before researching. Use it to (a) set
  the "since [date]" window for the research prompts, (b) carry forward any
  unresolved "monitor" items as explicit research questions for today, and
  (c) avoid re-reporting yesterday's news as if it were new — today's report
  should cover what *changed*.

## Step 2 — Build the research prompt(s)

Translate the context file into clear research questions for Perplexity rather
than pasting the file verbatim — a model that's told *what to look for and why*
researches better than one handed a raw data dump. **Never include the real
company name in any prompt sent to Perplexity/OpenRouter or in any web search**
— use the generic profile from the context file (e.g. "an Indonesian ICT company
serving banks, government, and mining customers"); the research is about the
*environment* (competitors, regulators, macro), so the company's own name adds
nothing and leaks identity to external services. Ask specifically for *recent*
developments relevant to: the company's industry, company's products, customers industry,
the named competitors, the topics/keywords being tracked, and the regions of 
concern. Explicitly ask Perplexity to cite its sources — this is essential, 
since the user evaluates the report partly by checking sources themselves, 
and an uncited claim is much harder for them to verify.

**Ask for a slightly wider window than you'll report on.** Perplexity handles
very narrow windows ("last 24–48 hours") poorly — it tends to return "no
material news" or recycle stale analysis. Ask for roughly the last 5–7 days
instead, then filter to what's genuinely new yourself, using the previous
report (read in Step 1) as the dedupe baseline. You do the windowing; don't
outsource it to the research model.

If the context spans several distinct areas (e.g. "competitor moves",
"regulatory changes", "supply chain", "customer industry"), weigh whether one combined query or a
few focused ones will surface more specific, checkable claims — focused queries
tend to produce sharper, better-sourced results than one broad sweep.

When researching the customer's industry specifically, filter for relevance to
*the company's* revenue: the user cares about developments in their customers'
industries only insofar as those developments could change how much their
customers buy. A customer segment under financial pressure, regulatory squeeze,
or a demand shift may cut or grow its spend with the company — that revenue
linkage is the lens, not customer-industry news for its own sake.

**Always research in English *and* in every language the user listed under
"News languages & preferred sources" in the context file, for every topic.**
The most timely, granular reporting — local regulators, regional outages,
domestic competitor moves, local political/economic developments — frequently
breaks first (and sometimes only) in local-language outlets before it reaches
English-language wires, if it ever does. So:

- Read the **"News languages & preferred sources"** section of `search_context.md`
  and use the languages listed there (e.g. Bahasa Indonesia, Mandarin, Japanese).
  If that section is blank or says "English only," search English only.
- When building Perplexity prompts, explicitly ask it to draw on sources in those
  languages as well as English, and to prioritize the user's named trusted outlets
  and avoid any they flagged.

Treating English-only as sufficient when the user has listed other languages is a
known blind spot that has caused this skill to miss material, in-scope
developments on the first pass — do not repeat it.

## Step 3 — Let the user pick the Perplexity model, then query via OpenRouter

**Before sending any prompt, ask the user which Perplexity model to use** with the
`AskUserQuestion` tool. This is a paid call and the right model depends on how
deep the day's situation warrants, so the choice is the user's to make — don't
silently default. Present the trade-offs and recommend Sonar Pro as the sensible
daily default (list it first, marked "(Recommended)"). Offer these options, each
mapping to a model id passed as the script's first argument:

- **Sonar Pro (Recommended)** — `perplexity/sonar-pro`. Balanced research depth
  and cost; the right default for a daily cadence.
- **Sonar Pro Search** — `perplexity/sonar-pro-search`. Sonar Pro tuned for
  heavier, agentic web retrieval — runs more searches per query, so it tends to
  surface more (and fresher) sources at somewhat higher cost/latency. A good
  pick on a busy news day when breadth of sourcing matters.
- **Sonar** — `perplexity/sonar`. Cheapest and fastest; lighter retrieval. Good
  for a quick, low-cost check on a quiet day.
- **Sonar Reasoning Pro** — `perplexity/sonar-reasoning-pro`. Adds a reasoning
  pass; better at connecting multi-step implications, at higher cost.
- **Sonar Deep Research** — `perplexity/sonar-deep-research`. Deepest multi-step
  retrieval and synthesis; slowest and most expensive. Use when the day calls for
  digging into a complex, fast-moving situation.

Use the **same chosen model for all queries in the run** (don't re-ask per query).
If the user has already named a model in their request for this run, honor that
and skip the question.

Then run the bundled script, piping the prompt in via stdin (this sidesteps
PowerShell quoting headaches with long, multi-line prompts) and passing the
chosen model id as the first argument:

```powershell
$prompt = @'
<your research prompt text here — can be multi-line>
'@
$prompt | python "<skill-path>/scripts/query_perplexity.py" "<chosen-model-id>"
```

The script reads the `OPENROUTER_API_KEY` environment variable, sends the prompt
to the model id you pass as the first argument (falling back to
`perplexity/sonar-pro` if none is given), and prints back JSON with the model's
`content` and any `citations` it returned.

If the script reports that `OPENROUTER_API_KEY` is missing or the request
failed, relay that message to the user directly rather than trying to route
around it — they'll need to fix the underlying setup (e.g. add credits, fix the
key) for the skill to work going forward.

## Step 4 — Cross-check and supplement with WebSearch

Perplexity's output is a *lead generator*, not a source of record. Real runs of
this skill have caught it returning "no material news" on days with major
in-scope developments, asserting the **opposite direction** of a central-bank
rate move, quoting a stale FX level, returning **empty citations arrays**, and
**fabricating a multi-billion-dollar acquisition** by conflating two unrelated
deals. So calibrate trust accordingly:

- **If Perplexity reports "no news," returns no citations, or you can't
  corroborate a claim via WebSearch, treat WebSearch as the primary research
  channel** — don't let a "quiet day" verdict from Perplexity end the research.
- **Never put an uncorroborated Perplexity-only claim in the report as fact.**
  Either find an independent source or omit it (or, if it's consequential
  enough that the user should know it's circulating, include it explicitly
  flagged as unverified). A confident, specific, uncited claim — especially a
  large M&A figure or a policy reversal — is a fabrication candidate, not a
  finding.
- When you correct or exclude a Perplexity claim, **say so in the report** (a
  short source-validity note) — the user values knowing what was checked and
  rejected, not just what survived.

Use the built-in `WebSearch` tool to:

- Corroborate Perplexity's most consequential or surprising claims with a
  source you can see directly, rather than taking its word for it
- Fill gaps — topics the context file calls out that Perplexity's response
  glossed over
- Pull in detail from sources you'd specifically vouch for; `allowed_domains`
  lets you focus on outlets like Reuters, Bloomberg, AP, official regulator
  sites, company investor-relations pages, or trade publications relevant to
  the user's industry

**Run WebSearch in English *and* in each language listed under "News languages &
preferred sources" in the context file, for every topic — this is required, not
optional** (unless the user listed "English only"). `WebSearch` skews toward
US/English results, so an English-only sweep systematically under-covers events
in non-English-speaking markets. For each area in the context file, run at least
one English query *and* at least one query in each configured local language,
using native-language terms. For example, in Bahasa Indonesia: a power outage →
`"pemadaman listrik Jawa PLN gangguan [month] [year]"`; a competitor → the company
name plus terms like `akuisisi`, `merger`, `restrukturisasi`, `anak usaha`,
`dividen`. (Translate the equivalent terms for whatever languages the user
configured.) Local-language searches reliably surface regulator notices, regional
infrastructure disruptions, and domestic competitor disclosures the English pass
misses. Also honor the user's preferred/avoided outlets here — focus trusted ones
via `allowed_domains` where useful. If an English and a local-language source
disagree on facts, surface the discrepancy in the report rather than picking one
silently.

Judge each source on its own merits rather than applying a blanket rule — a
wire-service report, a regulator's official notice, and a company's own press
release are about as solid as it gets, while a single blog post repeating an
unconfirmed rumor is not. When sources disagree with each other, say so in the
report instead of silently picking one side.

## Step 5 — Write the report

Save the report to `.claude/daily-update-reports/` as **both** markdown and Word,
using today's actual date in the filename and header (create the folder if it
doesn't exist yet):

- `.claude/daily-update-reports/YYYY-MM-DD-daily-update.md`
- `.claude/daily-update-reports/YYYY-MM-DD-daily-update.docx`

**and** show the same content directly in your response — the user wants both an
immediate read and a persistent archive they can refer back to later.

Write the markdown first, then convert it to Word with pandoc (installed on this
machine) — don't hand-build the `.docx`, the conversion is one deterministic
command and was being skipped on days where it was left to improvisation:

```powershell
pandoc ".claude/daily-update-reports/YYYY-MM-DD-daily-update.md" -o ".claude/daily-update-reports/YYYY-MM-DD-daily-update.docx"
```

If pandoc reports it can't write the `.docx` (a "permission denied" or "resource
busy" error usually means today's file is still open in Word), tell the user to
close it and retry rather than silently skipping the Word output. Stale Word lock
files (`~$...docx`) in the folder are harmless leftovers and can be ignored or
deleted.

Use this structure:

```markdown
# Daily Update — [Day, Month Date, Year]

## News Summary
[Organized by theme/topic from the context file. For each item: what happened,
when, and why it's relevant — explained in plain language, not copy-pasted
headlines. Cite the source inline, e.g. "(Reuters, June 8 2026)".]

## Impact to Company Risk
[Organized by the risk areas named in the context file (regulatory,
reputational, operational, financial, competitive, etc.). For each: explain
*concretely* how today's developments could affect this specific company —
connect the news to consequences rather than restating it. Include
*customer-side* risk as a first-class category: when a development threatens a
customer or a whole customer segment, trace it through to the company — a
customer that cuts budgets, loses a license, or shifts strategy is a direct
revenue risk to the company even if the company itself wasn't named in the news.]

## Mitigation Needed
[Concrete, prioritized, actionable recommendations — what someone should
actually do this week in response to each risk above. Avoid vague advice like
"monitor the situation"; say what to monitor, who should be informed, or what
decision might need revisiting.]

## Sources
[Every source used, as a markdown link with a one-line note on what kind of
source it is — e.g. "[Reuters: Title](url) — wire service" or "[Company X
investor relations](url) — primary source". This is what lets the user judge
validity for themselves, which is the thing they care about most.]
```

The "Impact to Company Risk" and "Mitigation Needed" sections are where your
judgment matters most — they require connecting external news to *this*
company's specific situation as described in the context file, not just
restating what was found. Take the time to think through second-order effects
rather than stopping at the obvious.

## Notes

- If `python` isn't on the user's PATH, try `py` (the Windows Python launcher)
  instead — both are common on Windows setups.
- The OpenRouter endpoint is OpenAI-compatible; the bundled script handles
  authentication and produces clear error messages (missing key, failed
  request) so there's no need to write custom HTTP calls from scratch.
- Keep the tone of the report direct and decision-useful. The user is using
  this to support real work, not to skim a news digest — write it the way you'd
  brief someone who needs to act on it today.
