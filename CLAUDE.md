# CLAUDE.md

CSC316 (University of Toronto) data-visualization team project: **Leo's Forecast**, an interactive story game about the
U.S. 10-year Treasury yield and what it can mean for a Canadian student.

**Title:** The 10-Year Treasury Yield Is Going Crazy — What Does That Mean for You?
**Team:** Bohdan Zmeul (BZ), Danyal Shenoda (DS), Humzah Ahmed (HA)
**Live site:** https://zmeulboh.github.io/csc316-final-project/ (GitHub Pages serves `main` as it is)
**Process book (source of truth for design decisions):** https://docs.google.com/document/d/1Sr4uAKbj8h2TRenuFmDX-Hdx7Ws0rbXcnyzvuotItFQ/edit

## Main message (every scene must serve this)

> "Rising interest rates aren't just Wall Street's problem. They can affect your wallet and your career, but not everyone is affected equally."

The driving question (the hook, on the title card): *"Why is everyone on Wall Street worried about a number I have
barely heard of, and what could it eventually mean for me?"* The end card closes with the main message and three
takeaways: build a money cushion, time your next step, know your industry's exposure.

## Audience: design rules

Canadian university students with little or no finance background (CS, bio, psych, engineering, humanities).

- **Know:** that interest makes loans more expensive, what mortgages are, that recessions cause layoffs, that inflation raises prices, that stocks go up and down.
- **Don't know:** Treasury securities, bond pricing, yield curves, discount rates, refinancing risk. The only theory we explain is the idea of a "risk-free rate".
- **Visualization literacy:** basic to moderate. Use line charts, bars and blocks drawn to scale, maps, sliders, and app-style graphics.
- **Never use:** candlestick charts, raw yield-curve plots, trading-style charts, or multi-axis charts.
- Focus on **consequences, not theory**. Keep wording plain and short, and explain any jargon the first time it appears.
- The U.S. 10-year yield is the starting point, but tie it back to Canada (trade, markets, borrowing conditions).

## The story (what the site is)

A one-screen story game in [`index.html`](index.html). You follow Leo, a Toronto kid born in 2007, one year at a time.
The life bar at the top tracks the real 10-year yield (click a chapter's dot to jump there). Each line of dialogue
is one step; Next, → or Space moves on.

| Year | Scene | Interaction | Real data shown |
|------|-------|-------------|-----------------|
| 2007 | Title (lake at dawn), nursery | — | Yield 1962–2007 across the sky; the family's first mortgage |
| 2008 | Kitchen, TV news | — | The crash on the TV chart |
| 2012 | Playground | Hover the kite string | The kite string is the yield 2007–2012; mortgage renewal |
| 2016 | Grandma & Grandpa's living room → **the family album** | Open the cover, flip pages, point at the graph paper | Monthly yield since 1962, same scale on every spread |
| 2016–17 | Street of SOLD signs, moving day | — | Cheap money and house prices |
| 2020 | Bedroom → **Leo's sketchbook** | Draw your guess of the next years | The real line after you draw |
| 2022 | Kitchen → **Mom's budget pad** | Drag the renewal rate | Budget blocks drawn to scale (Canada 5-yr + 1.5 pts) |
| 2024 | Café → **dominoes** | Push the first domino | The chain from yields to Leo's shifts, a real number on each step |
| 2026 | Campus, CN Tower → **Toronto map** | Drag/zoom, click a neighbourhood or a list row | Canadian jobs by industry since Feb 2022 (linked map, ranked list, detail card) |
| 2026 | **Rate slider** | Pick the 2030 yield | Four imagined futures (2027–2030), always dashed/violet |
| 2027–30 | Family dinner (or Leo's basement room in the worst future), career fair, Robarts, convocation, offices | — | The chosen future's consequences |
| End | **Corkboard** | Choose another future / replay | One photo per chapter pinned at its yield; outcome tiles; main message and takeaways; sources; authors |

Rates are real up to October 2026. Leo, his family and every outcome after 2026 are fictional and labelled as such.
[`prototype/rate-weather.html`](prototype/rate-weather.html) is the earlier data prototype, kept as a second page (no
longer linked from the story).

How the storyboard's six frames map onto the game: hook = the title card and the life bar; history = the album and
the sketchbook; the chain reaction = the dominoes; the squeeze = the budget pad; not everyone equally = the Toronto
map; what students can do = the end card's takeaways.

## Data

**All project data lives in one SQLite database: `prototype/data/project.db`.** Query it; don't hard-code numbers.
Every table, series and JSON field is described in [`prototype/data/README.md`](prototype/data/README.md). The raw
Bloomberg `.xlsx` exports are *not* in the repo (the team keeps them in the shared cloud folder).

Key series: `USGG10YR` (daily 10-yr, Bloomberg, 1990→), `GS10` (FRED, monthly, use only before 1990), `USGG2YR`,
`CA5Y`/`CA10Y` (Bank of Canada Valet, 2001→), `NMCMFR30`/`NMCMFR15`/`MORTGAGE30US`, `USURTOT`, `EHUPCA` (Canada
unemployment, **quarterly**), `USREC`, `SPX`, Canadian jobs by industry (`CANLEMPL` + 19, monthly 1990→), US CES jobs
(`NFP T` + 865, from **Nov 1993**; use `parent_id`/`depth`).

Data notes:
- Industry data is **national (Canada)**, not Ontario. Compare Feb 2022 (the month before rate hikes began) with the latest month.
- Monthly values are averages of daily closes (the `monthly` view). The newest month is month-to-date; `LASTFULL` in the code is the newest full month.
- `USURTOT` has no value for October 2025 in the source export.
- Facts not in the DB (Canada's 2022 CPI peak, Bank of Canada policy rate, CMHC's 1981 mortgage rate) are cited on the page.

**Schema:** `series(series_id, name, country, category, unit, frequency, parent_id, depth, source, source_file)`,
`observations(series_id, date 'YYYY-MM-DD', value)`, `meta(key, value)`, view `monthly(series_id, month 'YYYY-MM', value, n)`.

**Pipeline** (Python 3.10+, `pip install -r scripts/requirements.txt` only needed for `build_db.py`):
1. `python scripts/build_db.py <folder with the .xlsx exports>`: rebuilds `project.db`, and downloads the Bank of Canada and FRED series.
2. `python scripts/export_data.py`: writes `prototype/data/leo.json` (loaded by `index.html`) and `prototype/data/weather.json` (loaded by `rate-weather.html`). Never edit the JSON by hand; change the query and rerun.
3. `python scripts/explore.py`: the exploratory analysis behind the story's claims (data quality, record highs/lows, yield-curve inversions, yields vs unemployment, jobs by industry, the mortgage math). Standard library only.

**Scenario assumptions (the family's mortgage, fictional):** $320,000 borrowed in 2007 ($400k townhouse, 20% down),
$750,000 in 2017; 25-year amortization, 5-year terms, **Canadian semi-annual compounding**; rate = Government of Canada
5-yr yield + 1.5 pts. Keep obligations locked at a fixed rate separate from borrowing that is new or being renewed.

## Accuracy guardrails (important)

- The research insights in the process book come from published studies, **not from our own analysis**. Cite them as research, never as findings from our dataset.
- Never claim that a rising 10-yr yield *always* leads to higher unemployment, bankruptcies or recessions. Use "can", "is associated with", "historically". (`explore.py` shows the yield/unemployment correlation is weak.)
- No industry is "immune"; describe industries as *more exposed* or *more sheltered*, based on the data.
- **Always compute displayed values from the data files** and show the "as of" date or month.
- Imagined futures are always dashed or violet; fictional people and numbers are labelled as fictional.
- Sources and authors are on the page (end card; Rate Weather's footer).

Key references: Patrabansh et al. 2014 (yields and mortgage rates); Estrella & Mishkin 1998 (yield curve predicts recessions); Oreopoulos, von Wachter & Heisz 2012 (graduating in a recession: about a 9% earnings loss fading over 8–10 years); Singh, Suda & Zervou 2022 (manufacturing and construction more rate-sensitive); Romer & Romer 2023 (monetary tightening and unemployment); Sarikov & Kuprianov 2020 (rates and corporate bankruptcies).

## Visual style

- A sketchbook / picture-book look: Bungee for headings, Gochi Hand for handwriting, Nunito for text, DM Mono for numbers; black ink outlines; an indigo game frame around the painted stage.
- **The red thread:** the real yield appears inside scenes as objects (bunting, kite string, string lights, TV chart, Grandpa's graph paper). Each has a tooltip naming its months.
- **Weather = rates:** each scene's light (a colour grade in `GRADES`) and weather follow that year's yield: sunny when low, storms when high. Rain on screen and rain in the sound use the same `rainOf(y)`.
- Colours: red/hatched = debt and pressure, green/dashed = money left over, violet/dashed = imagined. Story stages: hook = orange, rising insights = blue, main message = crimson, solution = green.
- Recurring objects tie chapters together (Grandma's instant photo in the 2020 bedroom, Mom's plant, the family photo).

## Tech stack & commands

**Plain HTML, CSS and JavaScript with D3 v7 (from cdnjs). No framework, no build step, no TypeScript.** Everything is
drawn in SVG; sound is generated with the Web Audio API.

- `python -m http.server 8000` from the repo root, then http://localhost:8000 (the pages load JSON with `d3.json`, so they must be served).
- `npm install` then `npm run lint` (ESLint + html-validate; CI runs it on pull requests and pushes to `main`).
- After editing `index.html`, a quick syntax check: extract the main `<script>` and run `node --check` on it.

**How `index.html` is organised** (the script starts with a map; sections are marked `/* ===== name ===== */`):
DATA (real) → the family's mortgage, cast, story (every scene as data: `{year, age, y, bg, grade, stage, cast, lines}`,
lines are `[speaker, text, mood, opts]`) → state, life ribbon → stage drawing and the scene kit (`BG[bg](g, sc, fg)`
draws a scene; helpers `A, R, P, Cc, E, L, Tt, hw, mono, sans`; `NG()` draws outside the colour grade) → characters
(`person()`), camera, depth layer, page turns → the dialogue box and its DATA chart → playback (`goScene`, `next`,
`back`) → the end card → the rate slider → sound → wiring.

Interactive scenes set `CTRL = {ready, auto, line(i, step)}`; `waitAt` holds the story on a line until the reader acts
(Next again skips, and `auto()` does the action for them).

**Performance (the team tests on an old laptop: i7 4th gen, GTX 960M).** Keep 60 fps:
- Big things that move (the album's turning page, the café and city layers) live in their own composited layers and move with CSS transforms, not SVG repaints.
- Don't use SVG `<pattern>` fills on large areas (half a second of GPU time on that card); draw textures as plain strokes.
- Prefer `fill-opacity`/`stroke-opacity` over `opacity` on single shapes inside pages that get re-rasterized.
- Pause or skip animations that are off-screen; respect `prefers-reduced-motion` (every `a-*` animation class is switched off there).

## Working conventions

- Do data cleaning in a script, not by hand, so it can be rerun when new data comes out.
- Interactions must work with mouse, touch and keyboard; scroll/click-driven steps must make sense if someone goes fast or skips.
- Check text and layout at 1280×720, 1920×1080 and phone width (412×915). Phones are read upright: a phone turned
  sideways gets a "turn your phone upright" card (CSS only); tablets and computers stay horizontal.
- When unsure about a design decision, check the process book before inventing a new direction.

## Working with the team (role of AI)

CSC316 expects the team to direct an AI coding assistant and to **read, evaluate and verify** the code it writes.
- **Team owns:** design, context, taste, aesthetics, evaluation, final decisions, responsibility. **The team commits; don't commit on your own.**
- **Claude handles:** writing code, data processing, math/statistics, quick prototypes with real data, stress-testing edge cases.
- Write readable code with short comments so the team can explain every line. Don't add hidden "magic" or unnecessary libraries.
- After any change to a chart, tell the team how to check it: what to look at and which value to compare against the source data.
- Prototypes are cheap ("code sketches"), but don't quietly change the agreed story. Propose it first.

## Course design principles (CSC316 lectures 1–8), applied to this project

- **Question, audience, data first.** "Visualize ideas, not data." Familiar forms are deliberate for this audience.
- **Channels:** the most important comparison goes on position or length (the life bar, the strip in the album, budget blocks, the ranked jobs list); area and colour only for secondary impressions (cloud and sun-patch sizes on the map, by area, with the exact % printed).
- **Graphical integrity (Tufte):** lie factor ≈ 1; bars and blocks start at 0; one scale per comparison (every album spread uses the same 0–16% scale and 9.1 years); give context ("compared to what?": all jobs +7.5% as the baseline, the 1981 record, Feb 2022). Decoration must never hide or distort the data.
- **Causation:** lines shown together read as causal; word it as "moved together", "warning sign", "linked to".
- **Interaction:** show what's possible before (cue text, handles, cursors) and what changed after (transitions, "was → now" values). Overview first, details on demand (tooltips, the detail card). Linked views: the map ↔ ranked list ↔ detail card; the rate slider ↔ campus weather, life bar and sound. The story must still make sense with no interaction (Next always moves on).
- **Data stories:** insight → message → narrative; titles state a message; text and visuals say the same thing (redundant encoding); emotion and characters are fine, added claims are not.
- **Perception:** one pop-out per scene; context muted, focus in accent colour; Gestalt grouping (enclosure, connection, similarity); one meaning per colour across the site.
