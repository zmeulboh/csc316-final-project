"""Query prototype/data/project.db and push the numbers into the prototypes.

Usage (from the repo root):
    python scripts/export_data.py

Writes prototype/data/bundle.json and replaces the inlined data block in each
page between the markers

    /* @data:begin */ ... /* @data:end */

The pages stay single files (they are published as standalone artifacts), so
the data is inlined rather than fetched. Never edit the inlined block by hand:
change the queries here and rerun.
"""
import datetime as dt
import json
import os
import re
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "prototype", "data", "project.db")
PAGES = {
    "prototype/rate-weather.html": "B",
    "prototype/leos-forecast.html": "DATA",
}

# Story ids -> Canadian Labour Force Survey industry series (Bloomberg tickers)
INDUSTRIES = {
    "tech": "CADEPSTS",   # Professional, scientific and technical services
    "fin": "CAIEFIRE",    # Finance, insurance, real estate and leasing
    "pub": "CAIEPUBL",    # Public administration
    "con": "CAIECONS",    # Construction
    "ret": "CAIETRDE",    # Trade (wholesale + retail)
    "edu": "CADEEDUS",    # Educational services
    "man": "CAIEMANU",    # Manufacturing
    "food": "CADEACFS",   # Accommodation and food services
    "health": "CADEHCSA", # Health care and social assistance
    "all": "CANLEMPL",    # Total employment
}
RATE_HIKES_BEGAN = "2022-02"  # last month before the Bank of Canada / Fed started raising rates

con = sqlite3.connect(DB)


def rows(sql, *args):
    return con.execute(sql, args).fetchall()


def r2(v):
    return round(v, 2)


def month_shift(m, k):
    y, mo = int(m[:4]), int(m[5:7]) - 1 + k
    return f"{y + mo // 12:04d}-{mo % 12 + 1:02d}"


def monthly(sid, start="0000"):
    return [[m, r2(v)] for m, v in rows("SELECT month, value FROM monthly WHERE series_id=? AND month>=? ORDER BY month", sid, start)]


def latest(sid):
    d, v = rows("SELECT date, value FROM observations WHERE series_id=? ORDER BY date DESC LIMIT 1", sid)[0]
    return {"d": d, "v": r2(v)}


def us10_monthly():
    """FRED GS10 before 1990, then monthly averages of Bloomberg's daily USGG10YR."""
    old = monthly("GS10", "1962-01")
    new = monthly("USGG10YR")
    first = new[0][0]
    return [x for x in old if x[0] < first] + new


def build():
    last = latest("USGG10YR")
    year_ago = (dt.date.fromisoformat(last["d"]) - dt.timedelta(days=366)).isoformat()
    daily = [[d, r2(v)] for d, v in rows(
        "SELECT date, value FROM observations WHERE series_id='USGG10YR' AND date>=? ORDER BY date", year_ago)]
    pd, pv = max(daily, key=lambda x: x[1])
    # Last time the yield was at least this high before the current run-up
    prev = rows("SELECT max(date) FROM observations WHERE series_id='USGG10YR' AND value>=? AND date<?",
                pv, f"{int(pd[:4]) - 3}-01-01")[0][0]
    low_d, low_v = rows("SELECT date, value FROM observations WHERE series_id='USGG10YR' ORDER BY value, date LIMIT 1")[0]
    gs10 = us10_monthly()
    annual = {}
    for m, v in gs10:
        annual.setdefault(m[:4], []).append(v)
    annual = {y: r2(sum(v) / len(v)) for y, v in annual.items()}
    mort_peak = rows("SELECT date, value FROM observations WHERE series_id='MORTGAGE30US' ORDER BY value DESC LIMIT 1")[0]

    jobs_month = rows("SELECT max(month) FROM monthly WHERE series_id='CANLEMPL'")[0][0]
    ind = {}
    for key, sid in INDUSTRIES.items():
        s = dict(rows("SELECT month, value FROM monthly WHERE series_id=?", sid))
        ind[key] = {
            "name": rows("SELECT name FROM series WHERE series_id=?", sid)[0][0],
            "now": s[jobs_month], "feb22": s[RATE_HIKES_BEGAN], "yr": s[month_shift(jobs_month, -12)],
            "dec21": s["2021-12"],
            "series": [[m, s[m]] for m in sorted(s) if m >= "2019-01"],
        }

    common = {
        "asof": {"yield": last["d"], "jobs": jobs_month, "built": rows("SELECT value FROM meta WHERE key='built_at'")[0][0][:10]},
        "us10": {"last": last, "peak": {"d": pd, "v": pv}, "prevAbovePeak": prev, "low": {"d": low_d, "v": r2(low_v)}},
    }
    rate_weather = {
        **common,
        "gs10": gs10,
        "daily": daily,
        "rec": [d[:7] for (d,) in rows("SELECT date FROM observations WHERE series_id='USREC' AND value=1 AND date>='1962' ORDER BY date")],
        "boc": monthly("CA5Y", "2019-01"),
        "mort": monthly("NMCMFR30", "2019-01"),
        "mortPeak": {"d": mort_peak[0], "v": r2(mort_peak[1])},
        "ind": ind,
    }
    ca5 = {}
    for m, v in monthly("CA5Y"):
        ca5.setdefault(m[:4], []).append(v)
    leo = {
        **common,
        "us10Annual": {y: v for y, v in annual.items() if y >= "2007"},
        "us10AnnualMin": min(((y, v) for y, v in annual.items() if y <= "2012"), key=lambda x: x[1]),
        "ca5Annual": {y: r2(sum(v) / len(v)) for y, v in ca5.items() if y >= "2007"},
        "canUnemp": latest("EHUPCA"),
        # the Yield Coaster and Leo's sketchbook: the monthly 10-year yield since 1962
        "us10Monthly": gs10,
        "mortPeak": rate_weather["mortPeak"],
    }
    return {"B": rate_weather, "DATA": leo}


def inject(path, name, obj):
    full = os.path.join(ROOT, path)
    html = open(full, encoding="utf-8").read()
    block = f"/* @data:begin */ const {name} = {json.dumps(obj, separators=(',', ':'))}; /* @data:end */"
    new, n = re.subn(r"/\* @data:begin \*/.*?/\* @data:end \*/", lambda _: block, html, flags=re.S)
    if n != 1:
        raise SystemExit(f"{path}: expected exactly one @data block, found {n}")
    open(full, "w", encoding="utf-8", newline="\n").write(new)
    print(f"{path}: {len(block) / 1000:.0f} kB of data")


def main():
    out = build()
    json.dump(out, open(os.path.join(ROOT, "prototype", "data", "bundle.json"), "w"), separators=(",", ":"))
    for path, name in PAGES.items():
        inject(path, name, out[name])
    c = out["B"]
    print("as of", c["asof"], "| 10y last", c["us10"]["last"], "peak", c["us10"]["peak"], "prev", c["us10"]["prevAbovePeak"])


if __name__ == "__main__":
    main()
