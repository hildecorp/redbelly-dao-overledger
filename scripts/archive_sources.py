#!/usr/bin/env python3
"""Asks the Internet Archive's Wayback Machine to keep a copy of every source page, and records the address of that copy
in content/sources.json as "archived". The source list on the site, SOURCES.md, the PDF and the Word file then show an
"Archived copy" link next to the original, so every claim can still be checked if a page moves or goes down.

  python3 scripts/archive_sources.py          only the sources that have no archived copy yet
  python3 scripts/archive_sources.py --all    ask again for every source
  python3 scripts/archive_sources.py ID ...   only the sources with these ids

For each page it first asks Save Page Now for a fresh copy. If that is refused (the service limits how often it saves),
it takes the copy the Wayback Machine already holds that is closest to 15 October 2026, the day our snapshots were made.
A page with neither is left without the field. Our own test logs live on this site, so they are skipped.
Then run scripts/build.py and scripts/check.py (check.py --online also tries every archived copy)."""
import argparse, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "content/sources.json"
UA = "Mozilla/5.0 (compatible; source archiving for a Redbelly DAO Task Board report)"
SNAPSHOT_DAY = "20261015"
PAUSE = 8   # seconds between saves; the Wayback Machine refuses fast repeat requests
COPY = re.compile(r"https?://web\.archive\.org/web/(\d{14})[^/]*/(.+)")

def open_url(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout)

def saved_now(url):
    """Save Page Now: on success the request ends at the new copy, /web/<14-digit time>/<url>."""
    try:
        with open_url("https://web.archive.org/save/" + url) as r:
            for candidate in (r.geturl(), urllib.parse.urljoin("https://web.archive.org", r.headers.get("Content-Location") or "")):
                if COPY.match(candidate):
                    return candidate
    except Exception as e:
        print(f"    save refused ({getattr(e, 'code', e)})")
    return None

def closest_copy(url):
    """The copy the Wayback Machine already holds that is closest to the snapshot day, if any."""
    query = urllib.parse.urlencode({"url": url, "timestamp": SNAPSHOT_DAY})
    try:
        with open_url("https://archive.org/wayback/available?" + query, timeout=60) as r:
            closest = json.load(r).get("archived_snapshots", {}).get("closest") or {}
    except Exception as e:
        print(f"    lookup failed ({getattr(e, 'code', e)})")
        return None
    return closest.get("url") if closest.get("available") and str(closest.get("status", "200")).startswith("2") else None

def https(url):
    return "https://" + url.split("://", 1)[1] if url.startswith("http://") else url

def write_sources(sources):
    """The same layout as the file in the repository: one source per line."""
    lines = [" " + json.dumps(s, ensure_ascii=False) for s in sources]
    SOURCES.write_text("[\n" + ",\n".join(lines) + "\n]\n")

def main():
    ap = argparse.ArgumentParser(description="Record an Internet Archive copy of every source page.")
    ap.add_argument("ids", nargs="*", help="only these source ids")
    ap.add_argument("--all", action="store_true", help="ask again even where an archived copy is recorded")
    args = ap.parse_args()
    sources = json.loads(SOURCES.read_text())
    unknown = set(args.ids) - {s["id"] for s in sources}
    if unknown:
        raise SystemExit(f"unknown source id: {', '.join(sorted(unknown))}")
    todo = [s for s in sources if not s.get("local") and (not args.ids or s["id"] in args.ids) and (args.all or args.ids or not s.get("archived"))]
    done = 0
    for i, s in enumerate(todo):
        if i:
            time.sleep(PAUSE)
        print(f"{s['id']}: {s['url']}")
        copy = saved_now(s["url"]) or closest_copy(s["url"])
        if copy:
            s["archived"] = https(copy); done += 1
            print(f"    {s['archived']}")
            write_sources(sources)   # after each page, so an interrupted run keeps what it has
        else:
            print("    no archived copy, left as it was")
    print(f"\n{done} of {len(todo)} sources now have an archived copy; run scripts/build.py, then scripts/check.py")
    sys.exit(0 if done == len(todo) else 1)

if __name__ == "__main__":
    main()
