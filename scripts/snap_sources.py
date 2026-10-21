#!/usr/bin/env python3
"""Recaptures every source in content/sources.json as a text snapshot in evidence/snapshots/,
then rewrites evidence/manifest.json (URL, capture time in UTC, SHA-256).
Most pages are rendered with Playwright (Chromium). Three need another route:
  the Celer blog shows a bot check in a browser, so it is fetched with a plain HTTP request;
  the X post is read from X's public embed service; the TASK-16 PDF is converted with pdftotext.
Personal credit is removed from every copy before it is saved: names listed in the local, git-ignored .credit-names file
become [name removed], and links to sites listed in the local, git-ignored .credit-links file become [link removed].
A NOTE line under the title says what was replaced, and the manifest keeps that note.
After a recapture, run scripts/check.py: it fails if any quote is no longer on its page."""
import hashlib, html, json, re, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence/snapshots"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()

def celer(s):
    t = get(s["url"]).decode("utf-8", "ignore")
    m = re.search(r"<article.*?</article>", t, re.S); a = m.group(0) if m else t
    a = re.sub(r"<(script|style).*?</\1>", "", a, flags=re.S); a = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", a)
    a = html.unescape(re.sub(r"<[^>]+>", "", a))
    a = "\n".join(l.strip() for l in a.splitlines() if l.strip())
    return f"URL: {s['url']}\nTITLE: {s['title']}\n(fetched with curl; the browser view shows a bot check)\n\n{a}"

def xpost(s):
    pid = s["url"].rstrip("/").split("/")[-1]
    d = json.loads(get(f"https://cdn.syndication.twimg.com/tweet-result?id={pid}&token=4"))
    return (f"URL: {s['url']}\nTITLE: Redbelly Network post on X, {d['created_at']} (text read from the public embed service, cdn.syndication.twimg.com)\n\n"
            f"Author: {d['user']['name']} (@{d['user']['screen_name']})\n\n{d['text']}\n")

def pdf(s):
    raw = s["url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    tmp = ROOT / "build/source.pdf"; tmp.parent.mkdir(exist_ok=True); tmp.write_bytes(get(raw))
    txt = subprocess.run(["pdftotext", "-layout", str(tmp), "-"], capture_output=True, text=True).stdout
    return f"URL: {s['url']}\nTITLE: {s['title']} (PDF text)\n\n{txt}"

def rawmd(s):
    raw = s["url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return f"URL: {s['url']}\nTITLE: {s['title']} (raw Markdown)\n\n" + get(raw).decode("utf-8")

def local_list(name):
    p = ROOT / name
    return [l.strip() for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def redact(text):
    """Removes personal credit from a copy and says so under its title."""
    names = links = 0
    for n in sorted(local_list(".credit-names"), key=len, reverse=True):
        text, k = re.subn(r"[\w.-]*" + re.escape(n) + r"[\w.-]*", "[name removed]", text, flags=re.I); names += k
    for host in local_list(".credit-links"):
        text, k = re.subn(r"(?:https?://)?[\w.-]*" + re.escape(host) + r"[^\s)\]]*", "[link removed]", text); links += k
    if names or links:
        parts = ([f"{names} personal name{'s' if names != 1 else ''} with [name removed]"] if names else []) + \
                ([f"{links} link{'s' if links != 1 else ''} to a contributor website with [link removed]"] if links else [])
        note = "NOTE: " + " and ".join(parts) + ", because the Task Board does not allow personal credit inside a deliverable. Nothing else was changed."
        lines = text.split("\n"); lines.insert(2, note); text = "\n".join(lines)
    return text

def main():
    if not (local_list(".credit-names") and local_list(".credit-links")):
        raise SystemExit("refusing to capture: .credit-names and .credit-links are needed to remove personal credit from the copies")
    from playwright.sync_api import sync_playwright
    sources = [s for s in json.loads((ROOT / "content/sources.json").read_text()) if not s.get("local")]
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(user_agent=UA)
        for s in sources:
            f = OUT / s["file"]
            if "blog.celer.network" in s["url"]:
                text = celer(s)
            elif "x.com/" in s["url"]:
                text = xpost(s)
            elif s["url"].endswith(".pdf"):
                text = pdf(s)
            elif s["url"].endswith(".md"):
                text = rawmd(s)
            else:
                pg = ctx.new_page()
                try:
                    pg.goto(s["url"], wait_until="networkidle", timeout=60000)
                except Exception:
                    pass
                pg.wait_for_timeout(2500)
                text = f"URL: {s['url']}\nTITLE: {pg.title()}\n\n{pg.inner_text('body')}"; pg.close()
            f.write_text(redact(text)); print("captured", s["id"])
        b.close()
    man = []
    for p in sorted((ROOT / "evidence").rglob("*.txt")):
        head = p.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        man.append({"file": str(p.relative_to(ROOT)), "url": head[0][5:] if head and head[0].startswith("URL: ") else None,
                    "captured_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        note = next((l[6:] for l in p.read_text(encoding="utf-8", errors="ignore").splitlines()[:4] if l.startswith("NOTE: ")), None)
        if note:
            man[-1]["note"] = note
    (ROOT / "evidence/manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
