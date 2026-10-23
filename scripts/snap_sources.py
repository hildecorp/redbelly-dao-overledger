#!/usr/bin/env python3
"""Takes a fresh text copy of every source page and compares it with the saved copy the report quotes.

  python3 scripts/snap_sources.py           capture into build/snapshots/ and report what changed; evidence/ is left alone
  python3 scripts/snap_sources.py --write   then also replace the changed copies in evidence/snapshots/ and update
                                            evidence/manifest.json

The copies in evidence/snapshots/ are the evidence: every quote in the report is checked against them, and the manifest
records when each was captured (15 October 2026). That is why a plain run never touches them. It prints, for each source,
whether the page still reads the same and which quoted facts are no longer on it, and exits with 1 if any quote is gone.
With --write only the copies whose text changed are replaced, and every unchanged copy keeps its original capture time.

How a page is read: most are rendered with Playwright (Chromium). Four need another route:
  the Celer blog shows a bot check in a browser, so it is fetched with a plain HTTP request;
  the X post is read from X's public embed service; the TASK-16 PDF is converted with pdftotext;
  a Markdown file on GitHub is read raw.
Personal credit is removed from every copy before it is compared or saved: names listed in the local, git-ignored
.credit-names file become [name removed], and links to sites listed in .credit-links become [link removed]. A NOTE line
under the title says what was replaced, and the manifest keeps that note. --write refuses to run without both lists.
After --write, run scripts/check.py."""
import argparse, difflib, hashlib, html, json, re, shutil, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
SAVED = EVIDENCE / "snapshots"
FRESH = ROOT / "build/snapshots"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(request, timeout=60).read()

def raw_github(url):
    return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

# ---------- one reader per kind of page; each returns the text of the copy, headed by URL and TITLE lines ----------
def celer_blog(s):
    page = fetch(s["url"]).decode("utf-8", "ignore")
    article = re.search(r"<article.*?</article>", page, re.S)
    text = article.group(0) if article else page
    text = re.sub(r"<(script|style).*?</\1>", "", text, flags=re.S)
    text = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", text)
    lines = (line.strip() for line in html.unescape(re.sub(r"<[^>]+>", "", text)).splitlines())
    body = "\n".join(line for line in lines if line)
    return f"URL: {s['url']}\nTITLE: {s['title']}\n(fetched with curl; the browser view shows a bot check)\n\n{body}"

def x_post(s):
    post_id = s["url"].rstrip("/").split("/")[-1]
    post = json.loads(fetch(f"https://cdn.syndication.twimg.com/tweet-result?id={post_id}&token=4"))
    return (f"URL: {s['url']}\nTITLE: Redbelly Network post on X, {post['created_at']} (text read from the public embed service, cdn.syndication.twimg.com)\n\n"
            f"Author: {post['user']['name']} (@{post['user']['screen_name']})\n\n{post['text']}\n")

def github_pdf(s):
    pdf = ROOT / "build/source.pdf"
    pdf.parent.mkdir(exist_ok=True)
    pdf.write_bytes(fetch(raw_github(s["url"])))
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    return f"URL: {s['url']}\nTITLE: {s['title']} (PDF text)\n\n{text}"

def github_markdown(s):
    return f"URL: {s['url']}\nTITLE: {s['title']} (raw Markdown)\n\n" + fetch(raw_github(s["url"])).decode("utf-8")

READERS = [(lambda u: "blog.celer.network" in u, celer_blog), (lambda u: "x.com/" in u, x_post),
           (lambda u: u.endswith(".pdf"), github_pdf), (lambda u: u.endswith(".md"), github_markdown)]

def reader_for(s):
    return next((read for matches, read in READERS if matches(s["url"])), None)

def browser_page(context, s):
    page = context.new_page()
    try:
        page.goto(s["url"], wait_until="networkidle", timeout=60000)
    except Exception:
        pass   # a page that never goes quiet is still read after the pause below
    page.wait_for_timeout(2500)
    text = f"URL: {s['url']}\nTITLE: {page.title()}\n\n{page.inner_text('body')}"
    page.close()
    return text

# ---------- personal credit ----------
def private_list(name):
    p = ROOT / name
    return [line.strip() for line in p.read_text().splitlines() if line.strip()] if p.exists() else []

def credit_note(names, links):
    """The NOTE line for a copy with personal credit removed, worded as in the saved evidence."""
    if names and links:
        what = "contributor names and links in this copy were replaced with [name removed] and [link removed]"
    elif names:
        what = "a contributor name in this copy was replaced" if names == 1 else "contributor names in this copy were replaced"
        what += " with [name removed]"
    else:
        what = ("a contributor link in this copy was replaced" if links == 1 else "contributor links in this copy were replaced") + " with [link removed]"
    return f"NOTE: {what}, because the Task Board does not allow personal credit inside a deliverable. Nothing else was changed."

def redact(text):
    names = links = 0
    for name in sorted(private_list(".credit-names"), key=len, reverse=True):
        text, k = re.subn(r"[\w.-]*" + re.escape(name) + r"[\w.-]*", "[name removed]", text, flags=re.I)
        names += k
    for host in private_list(".credit-links"):
        text, k = re.subn(r"(?:https?://)?[\w.-]*" + re.escape(host) + r"[^\s)\]]*", "[link removed]", text)
        links += k
    if names or links:
        lines = text.split("\n")
        lines.insert(2, credit_note(names, links))
        text = "\n".join(lines)
    return text

# ---------- capture, compare, write ----------
def capture(sources):
    """{source id: redacted text} for every source, read the way its page needs."""
    out = {}
    needs_browser = [s for s in sources if reader_for(s) is None]
    for s in sources:
        if reader_for(s):
            out[s["id"]] = redact(reader_for(s)(s)); print("captured", s["id"])
    if needs_browser:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(); context = browser.new_context(user_agent=UA)
            for s in needs_browser:
                out[s["id"]] = redact(browser_page(context, s)); print("captured", s["id"])
            browser.close()
    return out

def norm(s):
    """As in scripts/check.py: curly quotes and odd spaces made plain, white space made one space."""
    for fancy, simple in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("\u00a0", " "), ("\u202f", " ")):
        s = s.replace(fancy, simple)
    return re.sub(r"\s+", " ", s).strip()

def compare(sources, fresh, facts):
    """Prints one line per source and returns (ids whose text changed, facts whose quote is no longer on the page)."""
    changed, lost = [], []
    for s in sources:
        saved = SAVED / s["file"]
        old = saved.read_text(encoding="utf-8", errors="ignore") if saved.exists() else ""
        new = fresh[s["id"]]
        gone = [f["id"] for f in facts if f["source"] == s["id"] and norm(f["quote"]) not in norm(new.replace("**", ""))]
        lost += gone
        if new == old:
            status = "same"
        else:
            changed.append(s["id"])
            moved = sum(1 for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
                        if line[:1] in "+-" and not line.startswith(("+++", "---")))
            status = f"changed, {moved} lines differ" if old else "new"
        print(f"  {s['id']:<24} {status}" + (f"; quote no longer on the page: {', '.join(gone)}" if gone else ""))
    return changed, lost

def rebuild_manifest():
    """Every .txt under evidence/ with its address, capture time and SHA-256. A file whose SHA-256 is unchanged keeps the
    capture time already recorded; a new or replaced file takes the time it was written."""
    before = {m["file"]: m for m in json.loads((EVIDENCE / "manifest.json").read_text())} if (EVIDENCE / "manifest.json").exists() else {}
    manifest = []
    for p in sorted(EVIDENCE.rglob("*.txt")):
        rel, data = str(p.relative_to(ROOT)), p.read_bytes()
        text = data.decode("utf-8", "ignore")
        first = text.splitlines()[:1]
        sha = hashlib.sha256(data).hexdigest()
        old = before.get(rel)
        when = old["captured_utc"] if old and old["sha256"] == sha else \
            datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {"file": rel, "url": first[0][5:] if first and first[0].startswith("URL: ") else None, "captured_utc": when, "sha256": sha}
        note = next((line[6:] for line in text.splitlines()[:4] if line.startswith("NOTE: ")), None)
        if note:
            entry["note"] = note
        manifest.append(entry)
    (EVIDENCE / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")

def main():
    ap = argparse.ArgumentParser(description="Recapture every source and compare it with the saved evidence.")
    ap.add_argument("--write", action="store_true", help="replace changed copies in evidence/snapshots/ and update the manifest")
    args = ap.parse_args()
    have_lists = bool(private_list(".credit-names") and private_list(".credit-links"))
    if args.write and not have_lists:
        raise SystemExit("refusing to write: .credit-names and .credit-links are needed to remove personal credit from the copies")
    if not have_lists:
        print("note: without .credit-names and .credit-links the fresh copies keep personal credit, "
              "so the copies that were redacted will show as changed")
    sources = [s for s in json.loads((ROOT / "content/sources.json").read_text()) if not s.get("local")]
    facts = json.loads((ROOT / "content/facts.json").read_text())
    fresh = capture(sources)
    shutil.rmtree(FRESH, ignore_errors=True); FRESH.mkdir(parents=True)
    for s in sources:
        (FRESH / s["file"]).write_text(fresh[s["id"]])
    print(f"\nfresh copies in {FRESH.relative_to(ROOT)}/, compared with {SAVED.relative_to(ROOT)}/:")
    changed, lost = compare(sources, fresh, facts)
    print(f"\n{len(sources) - len(changed)} of {len(sources)} sources read the same; {len(lost)} quoted facts are no longer on their page")
    if args.write and changed:
        for s in (s for s in sources if s["id"] in changed):
            (SAVED / s["file"]).write_text(fresh[s["id"]])
        rebuild_manifest()
        print(f"replaced {len(changed)} copies in {SAVED.relative_to(ROOT)}/ and updated evidence/manifest.json; now run scripts/check.py")
    elif changed:
        print("evidence/ was not changed; run with --write to replace the changed copies")
    sys.exit(1 if lost else 0)

if __name__ == "__main__":
    main()
