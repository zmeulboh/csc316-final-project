# Data

All the data behind the project, and what every field means.

| File | What it is | Made by | Used by |
|------|------------|---------|---------|
| [`project.db`](project.db) | SQLite database with every series we collected (898 series, about 386,000 observations) | [`scripts/build_db.py`](../../scripts/build_db.py) | the export script; you can query it directly |
| [`leo.json`](leo.json) | The numbers **Leo's Forecast** shows | [`scripts/export_data.py`](../../scripts/export_data.py) | [`index.html`](../../index.html) |
| [`weather.json`](weather.json) | The numbers **Rate Weather** shows | [`scripts/export_data.py`](../../scripts/export_data.py) | [`rate-weather.html`](../rate-weather.html) |

The two JSON files are generated from the database. Never edit them by hand: change the query in `export_data.py` and
run `python scripts/export_data.py` again.

**As of:** the newest daily yield is 2026-11-06, the newest job numbers are for October 2026, and the database was
built on 2026-11-08. The newest month of a daily series is month-to-date.

---

## 1. `project.db` (SQLite)

### Tables

**`series`**: one row per data series.

| Column | Type | Meaning |
|--------|------|---------|
| `series_id` | text, key | The source's own ticker or code, e.g. `USGG10YR` (Bloomberg) or `GS10` (FRED) |
| `name` | text | Readable name, e.g. "US 10-year Treasury yield" |
| `country` | text | `United States` or `Canada` |
| `category` | text | Group: `Rates`, `Mortgage`, `Labour`, `Stocks`, `Business cycle`, `Industry - NAICS (Thousands)`, `CES Tables B-1a & B-1b` |
| `unit` | text | `%`, `thousands of jobs`, `index points` or `0/1` |
| `frequency` | text | `daily`, `weekly`, `monthly` or `quarterly` |
| `parent_id` | text | For jobs by industry: the series one level up (e.g. Construction → Goods-producing sector). Empty for other series |
| `depth` | integer | Level in the industry tree: 0 = all jobs, 1 = sector, 2 and more = industries inside it |
| `source` | text | Where it comes from (Bloomberg, FRED, Bank of Canada Valet API) |
| `source_file` | text | The raw export or URL it was read from |

**`observations`**: one row per data point.

| Column | Type | Meaning |
|--------|------|---------|
| `series_id` | text | Which series (see `series`) |
| `date` | text `YYYY-MM-DD` | The day of the observation. Monthly and quarterly data are dated as in the source (first or last day of the period) |
| `value` | real | The value, in the series' `unit` |

**`meta`**: `built_at` (when the database was built) and `raw_files` (the exports it was built from).

**`monthly`** (a view): every series as monthly averages: `series_id`, `month` (`YYYY-MM`), `value` (average of the
month's observations, rounded to 4 decimals), `n` (how many observations were averaged).

```sql
-- example: the monthly 10-year minus 2-year spread (the yield curve's "warning light" when it is below 0)
SELECT a.month, round(a.value - b.value, 2) AS spread
FROM monthly a JOIN monthly b USING(month)
WHERE a.series_id = 'USGG10YR' AND b.series_id = 'USGG2YR' ORDER BY a.month;
```

### Series

| `series_id` | Series | Unit | Frequency | Coverage | Source | On the site |
|-------------|--------|------|-----------|----------|--------|-------------|
| `USGG10YR` | US 10-year Treasury yield (daily close) | % | daily | 1990-01-02 to 2026-11-06 | Bloomberg | yes, both pages |
| `GS10` | US 10-year Treasury yield, monthly average | % | monthly | 1960-01 to 2026-10 | FRED | yes, before 1990 only |
| `USGG2YR` | US 2-year Treasury yield (month end) | % | monthly | 1990-01 to 2026-10 | Bloomberg | no (analysis) |
| `CA5Y` | Government of Canada 5-year bond yield | % | daily | 2001-01-02 to 2026-11-05 | Bank of Canada Valet API (`BD.CDN.5YR.DQ.YLD`) | yes |
| `CA10Y` | Government of Canada 10-year bond yield | % | daily | 2001-01-02 to 2026-11-05 | Bank of Canada Valet API (`BD.CDN.10YR.DQ.YLD`) | no (analysis) |
| `NMCMFR30` | US 30-year fixed mortgage rate | % | weekly | 1990-01-04 to 2026-11-05 | Bloomberg | Rate Weather |
| `NMCMFR15` | US 15-year fixed mortgage rate | % | weekly | 1991-08-29 to 2026-11-05 | Bloomberg | no (analysis) |
| `MORTGAGE30US` | US 30-year fixed mortgage rate (Freddie Mac) | % | weekly | 1971-04-02 to 2026-11-05 | FRED | Rate Weather (its record high) |
| `USURTOT` | US unemployment rate | % | monthly | 1990-01 to 2026-10 | Bloomberg | no (analysis) |
| `EHUPCA` | Canada unemployment rate | % | quarterly | 1990 Q1 to 2026 Q3 | Bloomberg | yes |
| `USREC` | US recession months (NBER dates; 1 = recession) | 0/1 | monthly | 1960-01 to 2026-10 | FRED | Rate Weather |
| `SPX` | S&P 500 index | index points | daily | 1989-12-29 to 2026-11-06 | Bloomberg | no (analysis) |
| `CANLEMPL` and 19 more | Canadian jobs, in total and by industry (Labour Force Survey, NAICS) | thousands of jobs | monthly | 1990-01 to 2026-10 | Bloomberg (Statistics Canada LFS) | yes, 9 industries |
| `NFP T` and 865 more | US payroll jobs, in total and by industry (CES), down to 9 levels deep | thousands of jobs | monthly | 1993-11 to 2026-09 | Bloomberg (BLS CES) | no (analysis) |

The Canadian industries the site shows (story id → series): `tech` = `CADEPSTS` professional, scientific and technical
services; `fin` = `CAIEFIRE` finance, insurance, real estate and leasing; `pub` = `CAIEPUBL` public administration;
`con` = `CAIECONS` construction; `ret` = `CAIETRDE` trade (wholesale and retail); `edu` = `CADEEDUS` educational
services; `man` = `CAIEMANU` manufacturing; `food` = `CADEACFS` accommodation and food services; `health` = `CADEHCSA`
health care and social assistance; `all` = `CANLEMPL` all jobs.

Notes:
- The US jobs export labelled "Jan 1990 to Nov 1993" was a duplicate of the next file, so US jobs by industry start in
  November 1993.
- Job numbers are national (all of Canada), not Ontario or Toronto.
- `USURTOT` (US unemployment) has no value for October 2025 in the source export. No other series used here has a
  missing month ([`scripts/explore.py`](../../scripts/explore.py) checks this).

---

## 2. `leo.json` (Leo's Forecast)

Dates are `YYYY-MM-DD` (days) or `YYYY-MM` (months). Yields and rates are in percent.

| Field | Type | Meaning |
|-------|------|---------|
| `asof.yield` | date | Date of the newest daily 10-year yield |
| `asof.jobs` | month | Newest month of job data |
| `asof.built` | date | When `project.db` was built |
| `us10.last` | `{d, v}` | Newest daily close of the US 10-year yield |
| `us10.peak` | `{d, v}` | Highest daily close in the last 12 months (the story's "today", October 2026) |
| `us10.prevAbovePeak` | date | The last earlier day the yield closed at least that high (before the current run-up) |
| `us10.low` | `{d, v}` | Lowest daily close on record (since 1990) |
| `us10Annual` | `{year: %}` | Yearly average of the monthly 10-year yield, 2007 to 2026 (2026 = year to date) |
| `us10AnnualMin` | `[year, %]` | The lowest yearly average from 1962 to 2012 (the playground scene checks whether 2012 was it) |
| `us10Monthly` | `[[month, %], ...]` | The monthly 10-year yield since January 1962: FRED `GS10` before 1990, monthly averages of Bloomberg `USGG10YR` after. Used by Grandpa's album, Leo's sketchbook and every "red thread" |
| `ca5Annual` | `{year: %}` | Yearly average of the Government of Canada 5-year yield, 2007 to 2026. The family's mortgage rate is this plus 1.5 points (an assumption, stated on the page) |
| `ca5Monthly` | `[[month, %], ...]` | Monthly Government of Canada 5-year yield since January 2019 (the dominoes) |
| `canUnemp` | `{d, v}` | Newest Canadian unemployment rate |
| `canUnempQ` | `[[month, %], ...]` | Quarterly Canadian unemployment rate since 2019 (the dominoes) |
| `ind.<id>` | object | Canadian jobs in one industry (ids above), in thousands: |
| `ind.<id>.name` | text | The industry's name |
| `ind.<id>.now` | number | Jobs in the newest month (`asof.jobs`) |
| `ind.<id>.feb22` | number | Jobs in February 2022, the last month before rate hikes began (the comparison point) |
| `ind.<id>.yr` | number | Jobs 12 months before the newest month |
| `ind.<id>.dec21` | number | Jobs in December 2021 |
| `ind.<id>.series` | `[[month, thousands], ...]` | Monthly jobs since January 2019 |

## 3. `weather.json` (Rate Weather)

It has the same `asof`, `us10` and `ind` fields as `leo.json`, plus:

| Field | Type | Meaning |
|-------|------|---------|
| `gs10` | `[[month, %], ...]` | The monthly 10-year yield since 1962 (the same as `leo.json`'s `us10Monthly`) |
| `daily` | `[[date, %], ...]` | Daily 10-year closes for the last 12 months |
| `rec` | `[month, ...]` | US recession months since 1962 (NBER, via FRED `USREC`) |
| `boc` | `[[month, %], ...]` | Monthly Government of Canada 5-year yield since 2019 |
| `mort` | `[[month, %], ...]` | Monthly US 30-year fixed mortgage rate since 2019 (`NMCMFR30`) |
| `mortPeak` | `{d, v}` | The highest US 30-year mortgage rate on record (Freddie Mac, October 1981) |

---

## What is not in the data

- **Cited facts, not series:** Canada's 2022 inflation peak (Statistics Canada CPI), Bank of Canada policy-rate facts,
  and Canada's 5-year mortgage rate in 1981 (CMHC) are quoted on the page with their source, not stored here.
- **Fictional:** Leo, his family, their budget and mortgage amounts, and everything after October 2026 (the four
  futures are scenarios the reader picks, drawn with dashed lines). The rates they use are real up to October 2026.
- **Raw exports:** the Bloomberg `.xlsx` exports `project.db` was built from are not in the repository (the team keeps
  them in a shared folder). `meta.raw_files` lists them. To rebuild the database from them, see the main
  [README](../../README.md#rebuilding-the-data).
