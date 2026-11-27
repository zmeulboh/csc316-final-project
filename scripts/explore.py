"""Exploratory data analysis: the checks behind the story's claims, run on prototype/data/project.db.

Usage (from the repo root):
    python scripts/explore.py

Prints a short report, one section per question we asked of the data while designing the story. Every number the
story shows is exported by scripts/export_data.py; this script is where we looked at the data first (data quality,
record highs and lows, the yield curve, yields and unemployment, jobs by industry, the family's mortgage).

Only the Python standard library is needed. "Moved together" below means a correlation in the historical data, not
proof that one thing causes the other.
"""
import os
import sqlite3
from statistics import correlation, mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = sqlite3.connect(os.path.join(ROOT, "prototype", "data", "project.db"))


def q(sql, *args):
    """Run a query with ? parameters and return all its rows."""
    return con.execute(sql, args).fetchall()


def monthly(sid):
    """{'YYYY-MM': monthly average, rounded to 2 decimals as in the site's data files} for one series."""
    return {m: round(v, 2) for m, v in q("SELECT month, value FROM monthly WHERE series_id=? ORDER BY month", sid)}


def us10_monthly():
    """The monthly 10-year yield since 1962, spliced as on the site: FRED GS10 before 1990, Bloomberg after."""
    new = monthly("USGG10YR")
    old = {m: v for m, v in monthly("GS10").items() if "1962-01" <= m < min(new)}
    return {**old, **new}


def shift(m, k):
    """Move a 'YYYY-MM' month by k months."""
    y, mo = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def head(title):
    print(f"\n=== {title} " + "=" * max(0, 70 - len(title)))


# ---- 1. Data quality: coverage, duplicates and gaps (the checks we ran after build_db.py)
head("1. Data quality")
n_series, n_obs = q("SELECT count(*) FROM series")[0][0], q("SELECT count(*) FROM observations")[0][0]
print(f"{n_series} series, {n_obs:,} observations; built {q('SELECT value FROM meta WHERE key=?', 'built_at')[0][0]}")
dupes = q("SELECT count(*) FROM (SELECT series_id, date FROM observations GROUP BY 1, 2 HAVING count(*) > 1)")[0][0]
print(f"duplicate (series, date) pairs: {dupes}")
for sid in ["USGG10YR", "GS10", "USGG2YR", "CA5Y", "EHUPCA", "USURTOT", "USREC", "CANLEMPL"]:
    first, last, n = q("SELECT min(date), max(date), count(*) FROM observations WHERE series_id=?", sid)[0]
    months = sorted(monthly(sid))
    freq = q("SELECT frequency FROM series WHERE series_id=?", sid)[0][0]
    step = 3 if freq == "quarterly" else 1
    missing = [shift(a, step) for a, b in zip(months, months[1:]) if shift(a, step) != b]
    print(f"  {sid:9} {freq:9} {first} to {last}  n={n:5}  missing months: {', '.join(missing) or 'none'}")
# The US jobs export labelled Jan 1990 to Nov 1993 duplicated the next file, so US industry data starts in Nov 1993:
print("US jobs by industry start:", q("SELECT min(date) FROM observations WHERE series_id='NFP T'")[0][0])

# ---- 2. The 10-year yield: record high, record lows, and the October 2026 peak
head("2. The 10-year yield since 1962")
y10 = us10_monthly()
top = max(y10, key=y10.get)
print(f"highest month: {top} at {y10[top]:.2f}%")
low_d, low_v = q("SELECT date, value FROM observations WHERE series_id='USGG10YR' ORDER BY value LIMIT 1")[0]
print(f"lowest daily close: {low_d} at {low_v:.2f}%")
ms = sorted(y10)
for m in ["2012-07", "2016-07", "2020-07"]:
    earlier_lower = [p for p in ms if p < m and y10[p] <= y10[m]]
    print(f"{m}: {y10[m]:.2f}%, lowest since " + (earlier_lower[-1] if earlier_lower else "at least 1962 (a new low)"))
pk_d, pk_v = q("SELECT date, value FROM observations WHERE series_id='USGG10YR' AND date>='2025-11' ORDER BY value DESC LIMIT 1")[0]
prev = q("SELECT max(date) FROM observations WHERE series_id='USGG10YR' AND value>=? AND date<'2023-01-01'", pk_v)[0][0]
print(f"2026 peak: {pk_d} at {pk_v:.2f}%; last time at least that high before: {prev}")
annual = {}
for m, v in y10.items():
    annual.setdefault(m[:4], []).append(v)
print("yearly averages 2007-2026:", ", ".join(f"{y} {mean(v):.2f}" for y, v in annual.items() if y >= "2007"))

# ---- 3. The yield curve's warning light: months when the 10-year yield was below the 2-year yield
head("3. Yield curve: 10-year minus 2-year < 0")
spread = q("""SELECT a.month, a.value - b.value FROM monthly a JOIN monthly b USING(month)
              WHERE a.series_id='USGG10YR' AND b.series_id='USGG2YR' ORDER BY a.month""")
runs = []                                   # inverted stretches; ones less than 6 months apart count as one
for m, s in spread:
    if s >= 0:
        continue
    if runs and shift(runs[-1][1], 6) >= m:
        runs[-1][1] = m
    else:
        runs.append([m, m])
rec = [m for (m,) in q("SELECT substr(date, 1, 7) FROM observations WHERE series_id='USREC' AND value=1 AND date>='1990' ORDER BY date")]
for a, b in runs:
    after = [m for m in rec if m > a]
    nxt = f"next US recession began {after[0]}" if after else "no recession in the data since (as of the latest month)"
    print(f"  inverted {a} to {b}: {nxt}")
print("(Estrella & Mishkin 1998 find the curve helps predict recessions; the 2022-24 inversion had none by late 2026.)")

# ---- 4. Yields and unemployment: did they move together?
head("4. Yields and unemployment (US, monthly since 1990)")
un = monthly("USURTOT")
common = [m for m in sorted(un) if m in y10 and shift(m, 24) in un and shift(m, -12) in y10]
d_yield = [y10[m] - y10[shift(m, -12)] for m in common]             # 12-month change in the 10-year yield
d_unemp = [un[shift(m, 24)] - un[m] for m in common]                # unemployment change over the next 24 months
print(f"correlation of the 12-month yield change with the next 24 months' unemployment change: {correlation(d_yield, d_unemp):+.2f}")
print(f"correlation of the levels (same month): {correlation([y10[m] for m in common], [un[m] for m in common]):+.2f}")
print("(Weak and noisy: one reason the story says 'can' and 'is associated with', never 'always'.)")
ca = monthly("CA5Y")
both = [m for m in ca if m in y10]
print(f"US 10-year vs Canada 5-year yield, monthly since 2001: correlation {correlation([y10[m] for m in both], [ca[m] for m in both]):+.2f}")
mort = monthly("NMCMFR30")
both = [m for m in mort if m in y10]
gap = mean(mort[m] - y10[m] for m in both)
print(f"US 30-year mortgage vs 10-year yield: correlation {correlation([y10[m] for m in both], [mort[m] for m in both]):+.2f}, "
      f"mortgage {gap:.2f} points higher on average")

# ---- 5. Canadian jobs by industry since February 2022 (the CN Tower map and the "know your industry" takeaway)
head("5. Canadian jobs by industry, Feb 2022 to the latest month")
latest = q("SELECT max(month) FROM monthly WHERE series_id='CANLEMPL'")[0][0]
inds = {"CADEPSTS": "Professional, scientific & technical", "CAIEFIRE": "Finance, insurance & real estate",
        "CAIEPUBL": "Public administration", "CAIECONS": "Construction", "CAIETRDE": "Retail & wholesale trade",
        "CADEEDUS": "Educational services", "CAIEMANU": "Manufacturing", "CADEACFS": "Accommodation & food services",
        "CADEHCSA": "Health care & social assistance"}
jobs = {sid: monthly(sid) for sid in list(inds) + ["CANLEMPL"]}
pct = lambda sid: 100 * (jobs[sid][latest] / jobs[sid]["2022-02"] - 1)
total = pct("CANLEMPL")
print(f"all Canadian jobs: {total:+.1f}% (Feb 2022 to {latest})")
for sid in sorted(inds, key=pct):
    print(f"  {inds[sid]:38} {pct(sid):+6.1f}%   gap to all jobs {pct(sid) - total:+6.1f} pts")
print("(Ordered from more exposed to more sheltered, as on the map. Singh, Suda & Zervou 2022 find manufacturing and")
print(" construction more rate-sensitive; the recent numbers also reflect other causes, so the site says 'more exposed'.)")

# ---- 6. The family's mortgage (fictional family, real rates): the budget pad's numbers
head("6. The family's mortgage: Government of Canada 5-year yield + 1.5 points")
ca5_year = lambda y: mean(v for m, v in ca.items() if m.startswith(y))


def payment(loan, rate, months):
    """Monthly payment with Canadian semi-annual compounding."""
    r = (1 + rate / 200) ** (1 / 6) - 1
    return loan * r / (1 - (1 + r) ** -months)


def balance(loan, rate, months, paid):
    """What is still owed after `paid` monthly payments."""
    r, p = (1 + rate / 200) ** (1 / 6) - 1, payment(loan, rate, months)
    return loan * (1 + r) ** paid - p * ((1 + r) ** paid - 1) / r


m17, m22 = round(ca5_year("2017") + 1.5, 2), round(ca5_year("2022") + 1.5, 2)
p17 = payment(750_000, m17, 300)
b22 = balance(750_000, m17, 300, 60)
p22 = payment(b22, m22, 240)
print(f"2017: $750,000 over 25 years at {m17:.2f}% -> ${p17:,.0f}/month")
print(f"2022 renewal: ${b22:,.0f} left, 20 years at {m22:.2f}% -> ${p22:,.0f}/month ({p22 - p17:+,.0f})")
