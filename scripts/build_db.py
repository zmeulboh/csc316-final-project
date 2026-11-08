"""Build prototype/data/project.db (SQLite) from the team's raw data exports.

Usage (from the repo root):
    python scripts/build_db.py <folder with the .xlsx exports>

The raw Bloomberg .xlsx exports are NOT kept in the repo (the team keeps them
in the shared cloud folder). Download them into any folder and pass that
folder. The script also downloads two small public series that the exports
don't cover:
  - Bank of Canada 5- and 10-year Government of Canada bond yields (Valet API)
  - US recession months (FRED USREC, NBER dates)

Requires: Python 3.10+, openpyxl (pip install openpyxl).

Tables
  series(series_id, name, country, category, unit, frequency, parent_id, depth, source, source_file)
  observations(series_id, date 'YYYY-MM-DD', value)
  meta(key, value)
Views
  monthly(series_id, month 'YYYY-MM', value = average of the month, n)
"""
import csv
import datetime as dt
import glob
import io
import os
import sqlite3
import subprocess
import sys
import urllib.request

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "prototype", "data", "project.db")

SCHEMA = """
CREATE TABLE series(
  series_id   TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  country     TEXT,
  category    TEXT,
  unit        TEXT,
  frequency   TEXT,
  parent_id   TEXT,
  depth       INTEGER,
  source      TEXT,
  source_file TEXT
);
CREATE TABLE observations(
  series_id TEXT NOT NULL REFERENCES series(series_id),
  date      TEXT NOT NULL,
  value     REAL NOT NULL,
  PRIMARY KEY(series_id, date)
) WITHOUT ROWID;
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
CREATE VIEW monthly AS
  SELECT series_id, substr(date, 1, 7) AS month, round(avg(value), 4) AS value, count(*) AS n
  FROM observations GROUP BY series_id, month;
"""

# Readable names / units for the single-series market exports (keyed by Bloomberg ticker)
MARKET = {
    "USGG10YR": ("US 10-year Treasury yield", "United States", "Rates", "%"),
    "USGG2YR": ("US 2-year Treasury yield", "United States", "Rates", "%"),
    "NMCMFR30": ("US 30-year fixed mortgage rate", "United States", "Mortgage", "%"),
    "NMCMFR15": ("US 15-year fixed mortgage rate", "United States", "Mortgage", "%"),
    "USURTOT": ("US unemployment rate", "United States", "Labour", "%"),
    "EHUPCA": ("Canada unemployment rate", "Canada", "Labour", "%"),
    "SPX": ("S&P 500 index", "United States", "Stocks", "index points"),
}
FREQ = {"D": "daily", "W": "weekly", "M": "monthly", "Q": "quarterly"}


def iso(d):
    return d.date().isoformat() if isinstance(d, dt.datetime) else d.isoformat()


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    return None  # '#N/A N/A', '--', None


def rows_of(path):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    return [tuple(r) + (None,) * 4 for r in ws.iter_rows(values_only=True)]


class Loader:
    def __init__(self, con):
        self.con = con
        self.conflicts = []

    def add_series(self, **s):
        self.con.execute(
            "INSERT OR IGNORE INTO series VALUES(:series_id,:name,:country,:category,:unit,:frequency,:parent_id,:depth,:source,:source_file)",
            {"parent_id": None, "depth": 0, **s},
        )

    def add_obs(self, sid, date, value):
        old = self.con.execute("SELECT value FROM observations WHERE series_id=? AND date=?", (sid, date)).fetchone()
        if old is None:
            self.con.execute("INSERT INTO observations VALUES(?,?,?)", (sid, date, value))
        elif abs(old[0] - value) > 1e-9:
            # Overlapping months between export files: keep the first value, report the difference
            self.conflicts.append((sid, date, old[0], value))

    # Single-series market exports: Security / Start / End / Period / ... / Date, PX_LAST rows
    def market(self, path):
        rows = rows_of(path)
        head = {r[0]: r[1] for r in rows[:8] if r[0]}
        ticker = head["Security"].replace(" Index", "")
        name, country, cat, unit = MARKET.get(ticker, (rows[0][3] or ticker, None, None, None))
        start = next(i for i, r in enumerate(rows) if r[0] == "Date") + 1
        data = [(iso(r[0]), num(r[1])) for r in rows[start:] if isinstance(r[0], (dt.datetime, dt.date))]
        data = [(d, v) for d, v in data if v is not None]
        freq = FREQ.get(head.get("Period"), head.get("Period"))
        # Some exports are labelled monthly but are really quarterly: trust the spacing
        if len(data) > 2:
            gaps = sorted((dt.date.fromisoformat(a[0]) - dt.date.fromisoformat(b[0])).days for a, b in zip(data, data[1:]))
            gap = gaps[len(gaps) // 2]
            freq = "daily" if gap <= 4 else "weekly" if gap <= 8 else "monthly" if gap <= 31 else "quarterly"
        self.add_series(series_id=ticker, name=name, country=country, category=cat, unit=unit,
                        frequency=freq, source="Bloomberg", source_file=os.path.basename(path))
        for d, v in data:
            self.add_obs(ticker, d, v)
        return ticker, len(data)

    # Employment-by-industry tables: one row per series, one column per month (newest first)
    def employment(self, path):
        rows = rows_of(path)
        head = {r[0]: r[1] for r in rows[:8] if r[0]}
        country = head["Country"]
        survey = head.get("Data Set") or head.get("Category")
        hdr_i = next(i for i, r in enumerate(rows) if r[1] == "Ticker")
        months = [(j, dt.datetime.strptime(c, "%b %Y").date().isoformat()) for j, c in enumerate(rows[hdr_i]) if j >= 3 and c]
        stack = []  # (indent, series_id) for parent lookup
        category = None
        n = 0
        for r in rows[hdr_i + 1:]:
            label = r[0]
            if not label:
                continue
            indent = (len(label) - len(label.lstrip(" "))) // 4
            name = label.strip()
            if not r[1]:
                if indent == 0:
                    category = name
                continue
            sid = r[1].strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            unit = "thousands of jobs"
            self.add_series(series_id=sid, name=name.replace(" (Thousands)", ""), country=country,
                            category=category or survey, unit=unit, frequency="monthly",
                            parent_id=stack[-1][1] if stack else None, depth=indent,
                            source="Bloomberg (" + survey + ")", source_file=os.path.basename(path))
            stack.append((indent, sid))
            for j, d in months:
                v = num(r[j])
                if v is not None:
                    self.add_obs(sid, d, v)
                    n += 1
        return f"{country} employment {months[-1][1][:7]}..{months[0][1][:7]}", n


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "csc316-final-project data script"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8-sig")
    except OSError:  # URLError, SSL errors and timeouts are all OSErrors
        # Some Windows Pythons lack the CA certificates; curl uses the OS certificate store instead
        out = subprocess.run(["curl", "-sSfL", "-m", "60", url], capture_output=True, check=True)
        return out.stdout.decode("utf-8-sig")


def public_series(L):
    # Bank of Canada Valet: daily Government of Canada benchmark bond yields
    text = fetch("https://www.bankofcanada.ca/valet/observations/BD.CDN.5YR.DQ.YLD,BD.CDN.10YR.DQ.YLD/csv?start_date=1990-01-01")
    lines = text.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith('"date"'))
    rdr = list(csv.DictReader(io.StringIO("\n".join(lines[i:]))))
    for sid, col, name in [("CA5Y", "BD.CDN.5YR.DQ.YLD", "Canada 5-year government bond yield"),
                           ("CA10Y", "BD.CDN.10YR.DQ.YLD", "Canada 10-year government bond yield")]:
        L.add_series(series_id=sid, name=name, country="Canada", category="Rates", unit="%", frequency="daily",
                     source="Bank of Canada Valet API (" + col + ")", source_file=None)
        for r in rdr:
            if r.get(col):
                L.add_obs(sid, r["date"], float(r[col]))
    # FRED (St. Louis Fed). USREC: 1 = month inside an NBER-dated US recession.
    # GS10 and MORTGAGE30US give the long history before the Bloomberg exports start (1990).
    for sid, name, cat, unit, freq in [
            ("USREC", "US recession indicator (1 = recession month)", "Business cycle", "0/1", "monthly"),
            ("GS10", "US 10-year Treasury yield, monthly average (FRED)", "Rates", "%", "monthly"),
            ("MORTGAGE30US", "US 30-year fixed mortgage rate (Freddie Mac, FRED)", "Mortgage", "%", "weekly")]:
        L.add_series(series_id=sid, name=name, country="United States", category=cat, unit=unit, frequency=freq,
                     source="FRED " + sid, source_file=None)
        for r in csv.DictReader(io.StringIO(fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + sid))):
            if r[sid] not in ("", ".") and r["observation_date"] >= "1960":
                L.add_obs(sid, r["observation_date"], float(r[sid]))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = sys.argv[1]
    files = sorted(glob.glob(os.path.join(folder, "*.xlsx")))
    if not files:
        sys.exit("No .xlsx files in " + folder)
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    L = Loader(con)
    for f in files:
        kind = "employment" if "employment by industry" in os.path.basename(f).lower() else "market"
        print(f"{os.path.basename(f):58s}", *getattr(L, kind)(f))
    public_series(L)
    con.executemany("INSERT INTO meta VALUES(?,?)", [
        ("built_at", dt.datetime.now().isoformat(timespec="seconds")),
        ("raw_files", "; ".join(os.path.basename(f) for f in files)),
    ])
    con.commit()
    if L.conflicts:
        print(f"\n{len(L.conflicts)} overlapping values differed between files (kept the first file's value), e.g.:")
        for c in L.conflicts[:10]:
            print("  ", c)
    for sid, n, a, b in con.execute(
            "SELECT s.series_id, count(*), min(date), max(date) FROM series s JOIN observations o USING(series_id) "
            "WHERE s.depth=0 OR s.series_id IN ('CANLEMPL','NFP T') GROUP BY 1 ORDER BY 1"):
        print(f"  {sid:10s} {n:6d} rows  {a} .. {b}")
    con.execute("VACUUM")
    con.close()
    print("\nWrote", DB, f"({os.path.getsize(DB) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
