#!/usr/bin/env python3
"""Rewrite known-bad Wikipedia titles to correct ones across facts_raw/*.json."""
import glob, os
MAP = {
 "https://en.wikipedia.org/wiki/Empress_of_China_(1783_ship)": "https://en.wikipedia.org/wiki/Empress_of_China_(1783)",
 "https://en.wikipedia.org/wiki/Lever_Food_and_Fuel_Control_Act": "https://en.wikipedia.org/wiki/Food_and_Fuel_Control_Act",
 "https://en.wikipedia.org/wiki/Transcontinental_telephone_line": "https://en.wikipedia.org/wiki/First_transcontinental_telephone_call",
 "https://en.wikipedia.org/wiki/English_High_School_(Boston)": "https://en.wikipedia.org/wiki/English_High_School_of_Boston",
 "https://en.wikipedia.org/wiki/Ohio_Enabling_Act_of_1802": "https://en.wikipedia.org/wiki/Enabling_Act_of_1802",
 "https://en.wikipedia.org/wiki/Workingmen%27s_Party_(United_States)": "https://en.wikipedia.org/wiki/Workingmen%27s_Party_of_the_United_States",
 "https://en.wikipedia.org/wiki/1895_Chicago_Times-Herald_race": "https://en.wikipedia.org/wiki/Chicago_Times-Herald_race",
}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in glob.glob(os.path.join(ROOT, "facts_raw", "*.json")):
    with open(p) as f: t = f.read()
    n = 0
    for a, b in MAP.items():
        if a in t: t = t.replace(a, b); n += 1
    if n:
        with open(p, "w") as f: f.write(t)
        print(os.path.basename(p), n, "replaced")
