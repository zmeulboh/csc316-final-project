# The 10-Year Treasury Yield Is Going Crazy — What Does That Mean for You?

An interactive scrollytelling story that explains, in plain language, how rising U.S. Treasury yields can reach a Canadian university student's wallet and career.

> **Rising interest rates aren't just Wall Street's problem. They can affect your wallet and your career, but not everyone is affected equally.**

**Bohdan Zmeul · Danyal Shenoda · Humzah Ahmed**

CSC316 Data Visualization · University of Toronto · Fall 2026

<!-- Live demo: add link here once deployed -->

---

## About the project

The U.S. 10-year Treasury yield is one of the most watched numbers in finance, but most students have barely heard of it. This project answers one question:

*"Why is everyone on Wall Street worried about a number I have barely heard of, and what could it eventually mean for me?"*

**Audience:** Canadian university students with little or no finance background. The story uses familiar chart types (line charts, bars, sliders) and focuses on consequences (jobs, rent, mortgages, budgets) rather than financial theory.

## What's in the prototype (V1)

The prototype has two pages, both built with D3 on real data:

- **Leo's Forecast** ([`index.html`](index.html)): a story game. You follow Leo from 2007 to 2026 while a life bar at the top tracks the real 10-year yield. In 2020 you draw your own guess of where the yield goes next in Leo's sketchbook, and the real line is then drawn over it. The end card links to Rate Weather.
- **Rate Weather** ([`prototype/rate-weather.html`](prototype/rate-weather.html)): the data side of the story, as a scrolling page:
  - "Draw what happened next" and "Ride the rollercoaster": the yield's history;
  - "The domino chain": how higher rates reach jobs;
  - "The budget box": a rate slider for a household and a business budget;
  - "Weather over the job market": which Canadian industries are more exposed or more sheltered;
  - "Four years apart": the same graduate in two different rate worlds.

## The story

The planned story (from the storyboard) has six frames, organized as hook → rising insights → main message → solution. The prototype pages above cover most of these frames. The process book explains how they map.

| # | Stage | Frame | What you do |
|---|-------|-------|-------------|
| 1 | Hook | **Will you find a job after graduation?** A graduating student faces two roads, a strong job market or a weak one. The sign that points the way is the 10-year yield. | Scroll |
| 2 | Rising insights | **What can Treasury yields tell us about the economy?** Aligned charts of the 10-year yield, unemployment, recessions, and the yield-curve "warning light" from 2000 to today. | Scroll, hover to compare years |
| 3 | Rising insights | **The economic chain reaction.** Dominoes: higher yields → costlier loans → squeezed budgets → less spending → hiring freezes → you. | Scroll |
| 4 | Rising insights | **The financial squeeze.** A household budget and a business budget side by side. | Drag the interest-rate slider; toggle fixed vs. renewing loans |
| 5 | Main message | **Not everyone is affected equally.** Industries as buildings in the rain; umbrella size shows how well each industry held up, based on real job data. | Click a building |
| 6 | Solution | **What can students do to prepare?** Three paths: build a money cushion, time your next step, know your industry's exposure. | Click a path |

## Data

All data is stored in one SQLite database, [`prototype/data/project.db`](prototype/data/project.db).

| Data | Source |
|------|--------|
| U.S. 10-year and 2-year Treasury yields (the 10-minus-2 spread is computed) | Bloomberg `USGG10YR`, `USGG2YR` |
| U.S. and Canadian unemployment rates | Bloomberg `USURTOT`, `EHUPCA` |
| U.S. 30-year and 15-year mortgage rates | Bloomberg `NMCMFR30`, `NMCMFR15` |
| S&P 500 | Bloomberg `SPX` |
| Canadian employment by industry (Labour Force Survey) | Bloomberg |
| U.S. payroll employment by industry (CES) | Bloomberg |
| Government of Canada 5- and 10-year bond yields | Bank of Canada Valet API |
| U.S. recession periods; 10-year yield and 30-year mortgage history before 1990 | FRED `USREC`, `GS10`, `MORTGAGE30US` |

Coverage runs from 1990 to November 2026. The two exceptions are the Bank of Canada series, which start in 2001, and U.S. jobs by industry, which start in Nov 1993.

### Rebuilding the data

The raw Bloomberg Excel exports are not in the repo; the team keeps them in a shared cloud folder. To rebuild:

```bash
pip install -r scripts/requirements.txt
python scripts/build_db.py path/to/xlsx-folder   # Excel exports + Bank of Canada + FRED -> project.db
python scripts/export_data.py                    # project.db -> prototype/data/leo.json and weather.json
```

The pages load these JSON files with `d3.json`. Don't edit them by hand: change the queries in `export_data.py` and rerun it.

**Budget scenarios** in frame 4 are illustrative examples, not real households or companies:
- the household has a $400k mortgage with a 25-year amortization and Canadian semi-annual compounding;
- the business has a $2M interest-only loan.

**A note on interpretation:** the story shows how these indicators have moved *together* historically and what research finds about the links between them. It does not claim that rising yields always cause higher unemployment or recessions.

## Tech stack

- [D3.js](https://d3js.org/) v7 (loaded from a CDN): data loading (`d3.json`), scales, axes, shapes, and transitions
- Plain HTML, CSS, and JavaScript, with no build step and no framework
- Python 3 + SQLite for the data pipeline (`scripts/`)
- ESLint and html-validate for linting (development only)

## Running the project

The pages load their data files (`prototype/data/leo.json`, `prototype/data/weather.json`) with `d3.json`. Browsers block that when a page is opened by double-clicking it (`file://`), so serve the project folder with a local web server. Python 3 has one built in:

```bash
cd final_project
python -m http.server 8000
```

Then open **<http://localhost:8000>** in a browser:

- `index.html` (opens by default): **Leo's Forecast**, the story game
- <http://localhost:8000/prototype/rate-weather.html>: **Rate Weather**, our data prototype (the game's end card links to it)

Stop the server with `Ctrl+C`. An internet connection is needed for D3 and the Google Fonts. VS Code's Live Server extension or WebStorm's built-in server work too.

To run the linters (needs [Node.js](https://nodejs.org/)): `npm install`, then `npm run lint`.

## Project structure

```
index.html                  # Leo's Forecast: the story game (start here)
prototype/
  rate-weather.html         # Rate Weather: the data prototype
  data/
    project.db              # SQLite database with all project data
    leo.json                # data for index.html (written by export_data.py)
    weather.json            # data for rate-weather.html (written by export_data.py)
scripts/
  build_db.py               # raw exports + Bank of Canada + FRED -> project.db
  export_data.py            # project.db -> leo.json and weather.json
  requirements.txt          # Python packages for the scripts
package.json                # lint scripts (ESLint, html-validate)
CLAUDE.md                   # project context for the AI coding assistant
```

## Research

The story's explanations draw on the following research:

- Patrabansh, Doerner & Asin (2014). *The Effects of Monetary Policy on Mortgage Rates.* Federal Housing Finance Agency.
- Estrella & Mishkin (1998). *Predicting U.S. Recessions: Financial Variables as Leading Indicators.* Review of Economics and Statistics.
- Oreopoulos, von Wachter & Heisz (2012). *The Short- and Long-Term Career Effects of Graduating in a Recession.* AEJ: Applied Economics.
- Singh, Suda & Zervou (2022). *Monetary Policy, Labor Market, and Sectoral Heterogeneity.* AEA Papers and Proceedings.
- Romer & Romer (2023). *Does Monetary Policy Matter? The Narrative Approach after 35 Years.* American Economic Review.
- Sarikov & Kuprianov (2020). *The Effect of Monetary Policy on Corporate Bankruptcies: Evidence from the United States.* Applied Economics.

## Design process

The full design process (audience analysis, sketches, sketch selection, data story and storyboard) is documented in the team's process book, which is submitted separately.
<!-- TODO: add the process book link here -->


---

Built for CSC316: Data Visualization, Foundations and Advanced Programming (Prof. Carolina Nobre), University of Toronto.
