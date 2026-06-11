---
name: daily-update
description: Generates a comprehensive daily intelligence briefing by researching the company, industry, competitors, topics, and risk areas defined in .claude/skills/daily-update/assets/search_context.md, using the Perplexity Sonar Pro research model (via OpenRouter) cross-checked with WebSearch for source validity. Produces a dated markdown report covering a news summary, impact to company risk, and concrete mitigation steps. Use this skill whenever the user asks for their "daily update", "daily briefing", "morning briefing", "today's report/digest", wants to "catch up on news relevant to the company", or asks to check on competitors, industry shifts, or regulatory developments that could affect the business — even if they don't say "daily update" by name.
---

# Daily Update

Produces a daily intelligence briefing tailored to the user's company, industry,
competitors, and risk areas — defined once in
`.claude/skills/daily-update/assets/search_context.md` — by
researching recent developments via the Perplexity Sonar Pro research model
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
user's single source of truth for *what* to research: company name, business
model, product cycle, customer, industry, competitors, topics/keywords, risk
areas, and regions of concern.

- If the file is missing, or still contains bracketed placeholder text like
  `[Your Company Name]`, **stop here**. Tell the user the file needs to be
  filled in first — `assets/search_context.md` is the live config the user
  maintains, and a fresh template sits alongside it at
  `assets/search_context_template.md` if they need to start over from a blank
  copy. Running a search against an empty or templated
  context produces a generic, low-value report and burns a paid API call for
  nothing — pausing here is the right call, not a limitation to work around.
- If it looks filled in, read it fully before researching anything. Every topic
  you investigate should trace back to something the user actually told you to
  track — this keeps the report focused on what matters to *their* work, not a
  generic news roundup.

## Step 2 — Build the research prompt(s)

Translate the context file into clear research questions for Perplexity rather
than pasting the file verbatim — a model that's told *what to look for and why*
researches better than one handed a raw data dump. Ask specifically for *recent*
developments (last 24–48 hours, or "since [date of last report]" if you know
it) relevant to: the company's industry, company's products, customers industry,
the named competitors, the topics/keywords being tracked, and the regions of 
concern. Explicitly ask Perplexity to cite its sources — this is essential, 
since the user evaluates the report partly by checking sources themselves, 
and an uncited claim is much harder for them to verify.

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

**Always research in both English and the local language (Bahasa Indonesia) for
every topic.** This company operates in Indonesia, and the most timely, granular
reporting — local regulators, regional outages, domestic competitor moves, local
political/economic developments — frequently breaks first (and sometimes only) in
Indonesian-language outlets (Kompas, Kontan, Bisnis Indonesia, CNBC Indonesia,
Detik, Tempo, Tribun, Antara, etc.) before it reaches English-language wires, if
it ever does. When building Perplexity prompts, explicitly ask it to draw on
Indonesian-language sources as well as English ones. Treating English-only as
sufficient is a known blind spot that has caused this skill to miss material,
in-scope developments on the first pass — do not repeat it.

## Step 3 — Let the user pick the Perplexity model, then query via OpenRouter

**Before sending any prompt, ask the user which Perplexity model to use** with the
`AskUserQuestion` tool. This is a paid call and the right model depends on how
deep the day's situation warrants, so the choice is the user's to make — don't
silently default. Present the trade-offs and recommend Sonar Pro as the sensible
daily default (list it first, marked "(Recommended)"). Offer these options, each
mapping to a model id passed as the script's first argument:

- **Sonar Pro (Recommended)** — `perplexity/sonar-pro`. Balanced research depth
  and cost; the right default for a daily cadence.
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

Perplexity's synthesis is a strong starting point, but treat it as a lead to
verify, not a finished product — especially since the user has said validity
matters more to them than speed. Use the built-in `WebSearch` tool to:

- Corroborate Perplexity's most consequential or surprising claims with a
  source you can see directly, rather than taking its word for it
- Fill gaps — topics the context file calls out that Perplexity's response
  glossed over
- Pull in detail from sources you'd specifically vouch for; `allowed_domains`
  lets you focus on outlets like Reuters, Bloomberg, AP, official regulator
  sites, company investor-relations pages, or trade publications relevant to
  the user's industry

**Run WebSearch in both English and Bahasa Indonesia for every topic — this is
required, not optional.** `WebSearch` skews toward US/English results, so an
English-only sweep will systematically under-cover Indonesia-specific events.
For each area in the context file, run at least one English query *and* at least
one Indonesian-language query (e.g. for a Java power outage:
`"pemadaman listrik Jawa PLN gangguan [month] [year]"`; for a competitor:
the company name plus Indonesian terms like `akuisisi`, `merger`, `restrukturisasi`,
`anak usaha`, `dividen`). Indonesian-language searches reliably surface local
regulator notices, regional infrastructure disruptions, and domestic competitor
disclosures that the English pass misses. If an English and an Indonesian source
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
