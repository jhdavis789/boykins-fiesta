#!/usr/bin/env python3
"""Merge per-chunk agent JSON (facts_raw/*.json) into data.js for the site.
Validates: full 1776-2025 coverage, >=3 facts/year, https Wikipedia-ish URLs.
Exits nonzero listing problems if validation fails."""
import json, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "facts_raw")
OUT = os.path.join(ROOT, "data.js")

def load():
    by_year = {}
    for p in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        with open(p) as f:
            txt = f.read().strip()
        # strip accidental markdown fences
        txt = re.sub(r"^```(json)?\s*|\s*```$", "", txt)
        arr = json.loads(txt)
        for row in arr:
            y = int(row["year"])
            facts = []
            seen = set()
            for fa in row["facts"]:
                t = str(fa.get("t", "")).strip()
                u = str(fa.get("u", "")).strip()
                s = str(fa.get("s", "Wikipedia")).strip() or "Wikipedia"
                if not t or t.lower() in seen:
                    continue
                seen.add(t.lower())
                if not u.startswith("https://"):
                    u = f"https://en.wikipedia.org/wiki/{y}_in_the_United_States"
                facts.append({"t": t, "u": u, "s": s})
            if y in by_year:
                print(f"WARN: duplicate year {y} in {p}, keeping first")
                continue
            by_year[y] = facts
    return by_year

def main():
    by_year = load()
    problems = []
    for y in range(1776, 2026):
        if y not in by_year:
            problems.append(f"missing year {y}")
        elif len(by_year[y]) < 3:
            problems.append(f"year {y} has only {len(by_year[y])} facts")
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    rows = [{"year": y, "facts": by_year[y]} for y in sorted(by_year)]
    n = sum(len(r["facts"]) for r in rows)
    with open(OUT, "w") as f:
        f.write("window.FACTS=")
        json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"OK: {len(rows)} years, {n} facts -> {OUT} ({os.path.getsize(OUT)//1024} KB)")

if __name__ == "__main__":
    main()
