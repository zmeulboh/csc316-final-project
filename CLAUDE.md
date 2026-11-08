# CLAUDE.md

CSC316 (University of Toronto) data-visualization team project: a scrollytelling site.

**Title:** The 10-Year Treasury Yield Is Going Crazy — What Does That Mean for You?
**Team:** Bohdan Zmeul (BZ), Danyal Shenoda (DS), Humzah Ahmed (HA)
**Source of truth for design decisions:** the team process book (`docs/process-book.pdf`; the live version is the team's Google Doc).

## Main message (every frame must serve this)

> "Rising interest rates aren't just Wall Street's problem. They can affect your wallet and your career, but not everyone is affected equally."

The driving question: *"Why is everyone on Wall Street worried about a number I have barely heard of, and what could it eventually mean for me?"*

## Audience: design rules

Canadian university students with little or no finance background (CS, bio, psych, engineering, humanities).

- **Know:** that interest makes loans more expensive, what mortgages are, that recessions cause layoffs, that inflation raises prices, that stocks go up and down.
- **Don't know:** Treasury securities, bond pricing, yield curves, discount rates, refinancing risk. The only theory we explain is the idea of a "risk-free rate".
- **Visualization literacy:** basic to moderate. Use bar charts, line charts, simple maps, sliders, and app-style graphics.
- **Never use:** candlestick charts, raw yield-curve plots, trading-style charts, or multi-axis charts.
- Focus on **consequences, not theory**. Keep wording plain and short, and explain any jargon the first time it appears.
- The U.S. 10-year yield is the starting point, but tie it back to Canada (trade, markets, borrowing conditions).

## Story structure: 6 frames

The story follows 4 stages. Each stage has a colour: Hook = orange, Rising Insights = blue, Main Message = crimson, Solution = green.

| # | Stage | Frame | Visualization & interaction | Origin sketch |
|---|-------|-------|-----------------------------|---------------|
| 1 | Hook | **Will you find a job after graduation?** | A graduating student reaches a fork in the road: a strong job market (hiring, raises, first home) or a weak one (hiring freeze, layoffs, competition). *Scroll* to walk the student to the fork. *Reveal*: the sign that picks the road is the 10-yr yield and its current value. | 11 (BZ) |
| 2 | Rising Insights | **What can Treasury yields tell us about the economy?** | Aligned line charts from 2000 to today: the 10-yr yield (shown as a "coaster" the student rides), the unemployment rate, recession bands, and a "warning light" strip that turns on when the long-term yield is below the short-term yield (T10Y2Y < 0). *Scroll* to ride along; *hover* over a year to compare. Point out that the warning light also turned on in 2022–24, but no recession (yet). | 12 (BZ) |
| 3 | Rising Insights | **The economic chain reaction** | Dominoes, each with a one-line caption: yields rise → loans cost more → budgets squeezed → less spending/investment → hiring freezes and layoffs → YOU. *Scroll* to tip each domino in turn. | 2 (HA) |
| 4 | Rising Insights | **The financial squeeze: households vs. businesses** | Side-by-side stacked blocks: a household budget per month (debt payments, food/bills/transport, money left over) and a business budget per year (loan interest, rent/wages/supplies, cash left to hire and grow). An **interest-rate slider** sits between them (about 2–7%). Hatched debt blocks grow and dashed "left over" blocks shrink. A *toggle* switches between a locked fixed rate and a loan renewing at today's rate. | 13 (BZ) |
| 5 | Main Message | **Not everyone is affected equally** | Industry buildings (retail & wholesale, construction, manufacturing, health care, and so on) in the rain. Rain = pressure from higher rates; umbrella = resilience. Rain and umbrella sizes come from **real job data, not guesses**. *Click* a building to see its job trend. Order from "more exposed" to "more sheltered". | 7 + 8 (DS), merged |
| 6 | Solution | **What can students do to prepare?** | Back to the student from frame 1. Three branching paths, each with 2–3 tips on click: (1) build a money cushion, (2) time your next step (more school or skills; recovery isn't guaranteed), (3) know your industry's exposure (link back to frame 5). | — |

Narrative flow: personal worry → economic indicators → mechanism → personal squeeze → uneven impact → practical takeaways.

## Data

**All project data lives in one SQLite database: `prototype/data/project.db`.** Query it; don't hard-code numbers. The raw Bloomberg `.xlsx` exports it was built from are *not* in the repo (the team keeps them in the shared cloud folder).

| Use | Source | `series_id` in the DB | Coverage |
|-----|--------|------------------------|----------|
| US 10-yr Treasury yield (daily closes) | Bloomberg | `USGG10YR` | 1990-01 → latest |
| US 10-yr yield before 1990 (monthly) | FRED | `GS10` | 1960 → latest; use only before 1990 |
| US 2-yr Treasury yield (month-end) | Bloomberg | `USGG2YR` | 1990 → latest |
| 10-yr minus 2-yr spread (warning light) | computed | `USGG10YR` − `USGG2YR` (monthly view) | 1990 → latest |
| US unemployment rate | Bloomberg | `USURTOT` | monthly, 1990 → latest |
| Canada unemployment rate | Bloomberg | `EHUPCA` | **quarterly** (Mar/Jun/Sep/Dec), 1990 → latest |
| US 30-yr / 15-yr fixed mortgage rate (weekly) | Bloomberg | `NMCMFR30`, `NMCMFR15` | 1990 / 1991 → latest |
| US 30-yr mortgage rate, long history | FRED (Freddie Mac) | `MORTGAGE30US` | 1971 → latest |
| S&P 500 (daily close) | Bloomberg | `SPX` | 1989-12 → latest |
| US recession months (NBER) | FRED | `USREC` | 1960 → latest |
| Government of Canada 5-yr / 10-yr bond yield (daily) | Bank of Canada Valet | `CA5Y`, `CA10Y` | 2001 → latest |
| **Canada** jobs by industry (Labour Force Survey, thousands) | Bloomberg | `CANLEMPL` (total), `CAIECONS`, `CAIEMANU`, `CAIETRDE`, `CAIEFIRE`, `CADEPSTS`, `CADEEDUS`, `CADEHCSA`, `CADEACFS`, `CAIEPUBL`, … | monthly, 1990-01 → latest |
| US payroll jobs by industry (CES, thousands) | Bloomberg | `NFP T` (total) and ~870 sub-series; use `parent_id` / `depth` | monthly, **1993-11** → latest |

Data notes:
- Industry data is **national (Canada)**, not Ontario. Compare Feb 2022 (the month before rate hikes began) with the latest month.
- The US jobs export labelled "Jan 1990 – Nov 1993" was a duplicate of the Nov 1993 – Jun 2000 file, so US industry data starts in Nov 1993.
- Monthly yield values are averages of daily closes (the `monthly` view). The newest month is month-to-date; say so on the page.
- Things not in the DB (e.g. CPI inflation, the Bank of Canada policy rate, Toronto rent) are cited facts from Statistics Canada / Bank of Canada / CMHC. Cite them on the page, and add them to `scripts/build_db.py` if a chart needs the full series.

**Schema:** `series(series_id, name, country, category, unit, frequency, parent_id, depth, source, source_file)`, `observations(series_id, date 'YYYY-MM-DD', value)`, `meta(key, value)`, view `monthly(series_id, month 'YYYY-MM', value, n)`.

```sql
-- example: monthly 10-yr minus 2-yr spread
SELECT a.month, round(a.value - b.value, 2) AS spread
FROM monthly a JOIN monthly b USING(month)
WHERE a.series_id = 'USGG10YR' AND b.series_id = 'USGG2YR' ORDER BY a.month;
```

**Pipeline** (Python 3.10+, `pip install -r scripts/requirements.txt`):
1. `python scripts/build_db.py <folder with the .xlsx exports>`: rebuilds `project.db` from the exports, and downloads the Bank of Canada and FRED series.
2. `python scripts/export_data.py`: queries the DB, writes `prototype/data/bundle.json`, and rewrites the inlined data block between `/* @data:begin */ … /* @data:end */` in each prototype page. Never edit that block by hand; change the query in `export_data.py` and rerun.

**Scenario assumptions (frame 4):**
- Household: $400k mortgage, 25-year amortization, **Canadian semi-annual compounding**.
- Business: $2M loan, interest-only.
- Keep obligations already locked at a fixed rate separate from borrowing that is new or being renewed.

**Fictional personas** may be used to make scenarios relatable: Lydia (27, buying her first home), Jacob (recent grad, budget squeezed), Matthew (parent with a mortgage and a car payment). Use realistic values.

## Accuracy guardrails (important)

- The six research insights in the process book come from published studies, **not from our own analysis**. Don't present them as findings calculated from our dataset.
- Never claim that a rising 10-yr yield *always* leads to higher unemployment, bankruptcies or recessions. Use wording like "can", "is associated with", "historically".
- No industry is "immune"; describe industries as *more exposed* or *more sheltered*, based on the data.
- Numbers shown in the storyboard sketches (e.g. "5.3% now", "4.2% now") are placeholders. **Always compute displayed values from the database** (`prototype/data/project.db`, via `scripts/export_data.py`), and show the "as of" date.
- Put source citations on the page (footer per frame or a sources section).

Key references: Patrabansh et al. 2014 (FHFA, yields and mortgage rates); Estrella & Mishkin 1998 (yield curve predicts recessions); Oreopoulos, von Wachter & Heisz 2012 (graduating in a recession: about a 9% earnings loss that takes 8–10 years to fade); Singh, Suda & Zervou 2022 (sector differences: manufacturing and construction are more sensitive); Romer & Romer 2023 (monetary tightening and unemployment); Sarikov & Kuprianov 2020 (rates and corporate bankruptcies).

## Visual style

- Hand-drawn, sketchbook look: marker-style display font for headings, a clean hand-lettered body font, off-white paper background, black ink outlines.
- Use the stage colours as accents (see the story structure section); red/hatched = debt and pressure, green/dashed = money left over.
- Recurring characters: a stick-figure graduate (cap on), the dominoes, buildings, rain clouds, umbrellas.
- Each frame has a stage badge (number + stage name), a title, and a one-line instruction for the interaction ("Scroll:", "Drag the rate slider:", "Click a building:").

## Tech stack & commands

**Svelte + D3, with HTML, CSS and JavaScript (no TypeScript).**

- **Svelte** handles page structure, components, state and the DOM (frames, slider, toggle, tooltips, scroll steps).
- **D3** handles the data work: loading and parsing (`d3.csv`, `d3.timeParse`), scales, axes, shapes/paths (`d3.line`, `d3.area`, `d3.stack`), formatting (`d3.format`), and transitions where Svelte's own aren't enough.
- **Pattern:** let Svelte render the SVG elements from data, e.g. `{#each}` → `<rect>` / `<path d={line(data)}>`, and use D3 to compute the scales and path strings. Avoid having D3 and Svelte both control the same DOM nodes. If D3 must control an element directly (axes, brushes), give it its own `<g bind:this={el}>` and update it in a reactive block or `$effect`.
- Reactive values (current rate, scroll step, selected industry) live in Svelte state; charts recompute from them. Shared state across frames goes in a small store/module.
- Plain JavaScript, readable over clever. Check the `package.json` before using a Svelte 5–only feature (runes like `$state` and `$derived`) or Svelte 4 syntax (`$:`, `export let`), and match the version the project already uses.
- Scrollytelling: use an `IntersectionObserver`-based step tracker (or Scrollama if it's already installed) that sets the active step for each frame.

**Commands** (TODO: confirm against `package.json`):
- `npm install`: install dependencies
- `npm run dev`: start the local dev server
- `npm run build`: production build

**Suggested layout:**
- `src/lib/frames/`: one component per frame (`Frame1Fork.svelte`, `Frame2History.svelte`, `Frame3Dominoes.svelte`, `Frame4Squeeze.svelte`, `Frame5Industries.svelte`, `Frame6Paths.svelte`)
- `src/lib/components/`: shared pieces (axis, tooltip, slider, stage badge, scroll step)
- `src/lib/theme.js`: shared colours, fonts and stage colours (one source of truth)
- `src/lib/finance.js`: mortgage/loan math, with Canadian semi-annual compounding for the household mortgage
- `static/data/` (or `public/data/`): JSON/CSV exported from `project.db` by a script (extend `scripts/export_data.py`), never hand-edited
- `scripts/`: `build_db.py` (raw exports → SQLite) and `export_data.py` (SQLite → page data)

## Working conventions

- Keep each frame self-contained so team members can work in parallel; shared colours and fonts live in `src/lib/theme.js`.
- Do data cleaning in a script, not by hand, so it can be rerun when new data comes out.
- Interactions must work with mouse and touch; scroll-driven steps should still make sense if someone scrolls fast.
- When unsure about a design decision, check the process book before inventing a new direction.

## Working with the team (role of AI)

CSC316 expects the team to direct an AI coding assistant and to **read, evaluate and verify** the code it writes.
- **Team owns:** design, context, taste, aesthetics, evaluation, final decisions, responsibility.
- **Claude handles:** writing code, data processing, math/statistics, quick prototypes with real data, stress-testing edge cases.
- Write readable code with short comments so the team can explain every line. Don't add hidden "magic" or unnecessary libraries.
- After any change to a chart, tell the team how to check it: what to look at and which value to compare against the source data.
- Prototypes are cheap ("code sketches"). It's fine to try a quick variant, but don't quietly change the agreed storyboard design. Propose it first.

## Course design principles (CSC316 lectures 1–8), applied to this project

### Design sprint (Map → Sketch → Decide → build)
- Every visualization starts from **a question, an audience, and data**. Each frame answers specific question IDs from the process book; keep it that way.
- "Visualize ideas, not data." Know what a chart is *for* before choosing its form.
- Avoid design fixation (always reaching for the same pie/bar). But for *this* audience, familiar forms are deliberate.

### Data types → encodings
- Nominal (industry, persona), ordinal (rate sensitivity, scenario), quantitative (yield, rates, $, %). Choose channels to match the type.
- **Channel effectiveness ranking:**
  - For quantities: position on a common scale > length > angle/slope > area > intensity.
  - For categories: distinct hue > shape.
- Put the most important comparison on **position or length**. Use area or colour intensity only for secondary or approximate impressions.
- Choose the chart by the relationship you need to show (FT Visual Vocabulary):
  - change over time → line (frame 2);
  - part-to-whole → stacked bar/blocks (frame 4);
  - deviation (+/−) or ranking → diverging/ordered bar (frame 5 job changes).

### Effective visualization & graphical integrity (Tufte)
- **Effective = the distinctions and comparisons needed for the task are easy to see.**
- **Tell the truth:** marks must be drawn in proportion to the values (Lie Factor ≈ 1).
  - Bar, column and block lengths start at **0**.
  - In frame 4, block heights and areas must be proportional to the dollar amounts.
  - In frame 5, size umbrellas and rain by **area, not radius**, and also print the exact % next to each one.
- No truncated or stretched scales to make a change look dramatic. Aligned charts in frame 2 share the same x-axis and time range.
- **Give context ("compared to what?"):** recession bands, the "record low" annotation, the 2022 baseline, the "was $X" values.
- Maximize the data-ink ratio and avoid chartjunk. The hand-drawn style and illustrations are allowed because they help a general audience engage and remember. But decoration must never hide or distort the data, and gridlines and frames should stay light.
- Readers assume that lines shown together are causally related. In frame 2, word it as "moved together" or "warning sign", never "caused".

### Interaction
- **Discoverability:**
  - *Before* an action, show what's possible: cue text ("Drag the rate slider", "Click a building"), visible handles, cursor changes.
  - *After* an action, show clearly what changed: animated transitions, updated labels, highlighted "was → now" values.
- Seven interaction intents (Yi et al.):
  - Select = frame 2 hover;
  - Encode/Reconfigure = frame 4 slider and toggle;
  - Elaborate = frame 5 click for details;
  - Connect = linked highlights across the frame 2 charts.
- **Overview first, zoom and filter, details on demand** (Shneiderman). Show the summary by default and put the details in tooltips or click panels.
- Use smooth transitions (D3 `transition`) and keep each mark the same object through a change (object constancy), so readers can follow a bar or block as it moves.
- Interaction should let readers explore *their own* questions (e.g. "what if rates hit 7%?"), but the story must still make sense with no interaction at all.

### Data stories
- **Insight** (a finding supported by data) → **Message** (why it matters to *this* audience) → **Narrative** (the order of context and evidence).
- Frame titles should state a **message**, not a topic label. Compare the insight against something students care about and use an evaluative word ("Same degree, different risk", not "Industry employment").
- Framing must not add new claims: no added causes, no exaggerated severity, no over-generalizing. This matches the accuracy guardrails above.
- **Redundant encoding:** pair each visual with short text that says the same point (text is sequential and precise; visuals are fast and intuitive). Don't write text-heavy frames.
- It's fine to use emotion and relatable characters (the student and the personas) to make the message stick.

### Storyboard & narrative arc (Dykes)
- The arc is Setting/Hook → Rising Insights → Aha (main message) → Solution / next steps, which matches frames 1–6.
- **One question per frame.** Each rising insight answers the previous question and raises the next one. If a frame doesn't move the story forward, cut it.
- Every frame should be substantial: leaving it out would change the story.
- The order we tell it in ≠ the order we analyzed it in. Start from the aha and work backwards.
- End with something the audience can *do* (frame 6).

### Perception
- **Pre-attentive pop-out** (colour, size, orientation, motion): use it for the one thing each frame wants noticed first, like the "now" dot, the student, or the most exposed industry. Pop-out only works if just one thing pops.
- **Visual hierarchy through contrast and layering:** draw context in muted greys and the focus in a stage accent colour or red. Urgent > normal > context.
- **Gestalt grouping** (strongest to weakest): enclosure > connection > proximity / similarity. Use them as follows:
  - enclosure to separate household from business (frame 4);
  - connection for the domino chain (frame 3) and the branching paths (frame 6);
  - similarity (same colour) to link the same variable across charts.
- When combining channels, use **separable** pairs (position + hue, or position + shape). Avoid integral pairs (width + height, or two colour dimensions) for two independent variables.
- Use colour consistently: one meaning per colour across the whole site (debt/pressure = red, money left over = green, stage colours only for stage UI).
