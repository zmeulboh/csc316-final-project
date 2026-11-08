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

## The story

The story has six frames, organized as hook → rising insights → main message → solution.

| # | Stage | Frame | What you do |
|---|-------|-------|-------------|
| 1 | Hook | **Will you find a job after graduation?** A graduating student faces two roads, a strong job market or a weak one. The sign that points the way is the 10-year yield. | Scroll |
| 2 | Rising insights | **What can Treasury yields tell us about the economy?** Aligned charts of the 10-year yield, unemployment, recessions, and the yield-curve "warning light" from 2000 to today. | Scroll, hover to compare years |
| 3 | Rising insights | **The economic chain reaction.** Dominoes: higher yields → costlier loans → squeezed budgets → less spending → hiring freezes → you. | Scroll |
| 4 | Rising insights | **The financial squeeze.** A household budget and a business budget side by side. | Drag the interest-rate slider; toggle fixed vs. renewing loans |
| 5 | Main message | **Not everyone is affected equally.** Industries as buildings in the rain; umbrella size shows how well each industry held up, based on real job data. | Click a building |
| 6 | Solution | **What can students do to prepare?** Three paths: build a money cushion, time your next step, know your industry's exposure. | Click a path |

## Data

| Data | Source |
|------|--------|
| 10-year Treasury yield | FRED `GS10` |
| Unemployment rate | FRED `UNRATE` |
| 10-year minus 2-year spread | FRED `T10Y2Y` |
| U.S. recession periods | FRED `USREC` |
| 30-year U.S. mortgage rate | FRED `MORTGAGE30US` |
| Ontario employment by industry | Statistics Canada, Table 14-10-0355 (seasonally adjusted) |

**Budget scenarios** in frame 4 are illustrative examples, not real households or companies:
- the household has a $400k mortgage with a 25-year amortization and Canadian semi-annual compounding;
- the business has a $2M interest-only loan.

**A note on interpretation:** the story shows how these indicators have moved *together* historically and what research finds about the links between them. It does not claim that rising yields always cause higher unemployment or recessions.

## Tech stack

- [Svelte](https://svelte.dev/): components, state, and scroll-driven steps
- [D3.js](https://d3js.org/): data loading, scales, shapes, and formatting
- HTML, CSS, JavaScript

## Getting started

Requires [Node.js](https://nodejs.org/) (LTS).

```bash
git clone <repo-url>
cd <repo-folder>
npm install
npm run dev      # start local dev server
npm run build    # production build
```

## Project structure

```
src/
  lib/
    frames/        # one Svelte component per story frame (Frame1Fork … Frame6Paths)
    components/    # shared UI: axis, tooltip, slider, stage badge, scroll step
    theme.js       # colours, fonts, stage colours
    finance.js     # mortgage and loan calculations
static/data/       # cleaned CSV data from FRED and Statistics Canada
scripts/           # data download and cleaning scripts
docs/              # process book and design documentation
CLAUDE.md          # project context for the AI coding assistant
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

The full design process (audience analysis, sketches, sketch selection, data story and storyboard) is documented in the [process book](docs/process-book.pdf).

---

Built for CSC316: Data Visualization, Foundations and Advanced Programming (Prof. Carolina Nobre), University of Toronto.
