#!/usr/bin/env python3
"""Verify every source URL in data.js resolves (HTTP 200 after redirects).
Failures are rewritten in-place to the year's Wikipedia fallback page.
Usage: python3 scripts/verify_urls.py [--fix]"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data.js")

def status(url):
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-I", "-L",
             "-m", "20", "-A", "Mozilla/5.0 (compatible; BoykinsFiesta/1.0)", url],
            capture_output=True, text=True, timeout=25)
        return url, r.stdout.strip()
    except Exception:
        return url, "ERR"

def main():
    fix = "--fix" in sys.argv
    with open(DATA) as f:
        txt = f.read()
    rows = json.loads(txt[txt.index("=") + 1:].rstrip().rstrip(";"))
    urls = sorted({fa["u"] for r in rows for fa in r["facts"]})
    print(f"checking {len(urls)} unique urls...")
    bad = {}
    with ThreadPoolExecutor(max_workers=24) as ex:
        for url, code in ex.map(status, urls):
            if code != "200":
                bad[url] = code
                print(f"  BAD {code} {url}")
    print(f"{len(bad)} bad / {len(urls)} total")
    if bad and fix:
        nfix = 0
        for r in rows:
            fb = f"https://en.wikipedia.org/wiki/{r['year']}_in_the_United_States"
            for fa in r["facts"]:
                if fa["u"] in bad:
                    fa["u"] = fb
                    nfix += 1
        with open(DATA, "w") as f:
            f.write("window.FACTS=")
            json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
            f.write(";\n")
        print(f"rewrote {nfix} fact urls to year-fallback pages")
    sys.exit(1 if (bad and not fix) else 0)

if __name__ == "__main__":
    main()
