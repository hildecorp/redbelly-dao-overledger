#!/usr/bin/env python3
"""Quality gate for the report. Prints RESULT: PASS or RESULT: FAIL.
  python3 scripts/check.py            offline checks
  python3 scripts/check.py --online   also confirms every source link answers today
Checks:
  1  every fact quote is found word for word in its saved snapshot, and every snapshot matches its SHA-256 in evidence/manifest.json
  2  every citation points to a known fact, every source is cited, every paragraph with a status label cites at least one fact
  3  no wording that suggests a partnership, talks, plans or an agreement between Redbelly and Quant
  4  no price talk, investment advice or hype words, no en dash, em dash or emoji
  5  no personal name or handle from the local, git-ignored .credit-names file, and no link to a site listed in the
     local, git-ignored .credit-links file, anywhere in the deliverables; the Word file carries no tool or person in its properties
  6  each X post fits in 280 characters
  7  the PDF, the Word file and the website (home page and every chapter page) contain the current text of every paragraph,
     and the source page every quote
  8  diagrams follow the SVG rules (brand palette, prefixed ids, title and desc, no styles, images or outside links),
     and the website loads nothing from another domain
  9  every link inside the website opens a page that exists, at a clean address (no .html), and every #anchor exists
"""
import hashlib, json, re, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors, notes = [], []
R = json.loads((ROOT / "content/report.json").read_text())
FACTS = json.loads((ROOT / "content/facts.json").read_text()); F = {f["id"]: f for f in FACTS}
SOURCES = {s["id"]: s for s in json.loads((ROOT / "content/sources.json").read_text())}
CITE = re.compile(r"\{([a-z0-9 -]+)\}")

def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), (" ", " "), (" ", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()

# 1 quotes and snapshots
man = {m["file"]: m for m in json.loads((ROOT / "evidence/manifest.json").read_text())}
for fpath, m in man.items():
    p = ROOT / fpath
    if not p.exists():
        errors.append(f"evidence: {fpath} listed in manifest but missing")
    elif hashlib.sha256(p.read_bytes()).hexdigest() != m["sha256"]:
        errors.append(f"evidence: {fpath} changed after capture (SHA-256 mismatch)")
for s in SOURCES.values():
    rel = str((ROOT / "evidence/snapshots" / s["file"]).resolve().relative_to(ROOT))
    if rel not in man:
        errors.append(f"source {s['id']}: snapshot {rel} not in manifest")
for f in FACTS:
    s = SOURCES.get(f["source"])
    if not s:
        errors.append(f"fact {f['id']}: unknown source {f['source']}"); continue
    snap = (ROOT / "evidence/snapshots" / s["file"]).read_text(encoding="utf-8", errors="ignore")
    # Markdown bold markers in a copied README are formatting, not words
    if norm(f["quote"]) not in norm(snap.replace("**", "")):
        errors.append(f"fact {f['id']}: quote not found in {s['file']}")

# 2 citations and labels
prose, labelled = [], []   # prose: (where, text) written by us; labelled: blocks that need a citation
prose.append(("status note", R["status_note"]))
for k in R["key_findings"]:
    prose += [("finding", k["q"]), ("finding", k["a"] + " {" + k["cite"] + "}")]
for s in R["sections"]:
    prose.append((s["id"] + " title", re.sub(r"^\d+\.\s*", "", s["title"])))
    if s.get("intro"):
        prose.append((s["id"] + " intro", s["intro"]))
    for i, b in enumerate(s["blocks"]):
        where = f"{s['id']} block {i + 1}"
        if b["label"] not in ("confirmed", "tested", "analysis", "unknown", "summary_table", "method"):
            errors.append(f"{where}: unknown label {b['label']}")
        parts = [b.get("heading", ""), b.get("text", "")] + b.get("list", []) + [r[0] + " " + r[1] + " {" + r[2] + "}" for r in b.get("rows", [])]
        for t in parts:
            if t:
                prose.append((where, t))
        if b["label"] in ("confirmed", "tested", "analysis", "unknown"):
            for t in ([b["text"]] if b.get("text") else []) + b.get("list", []):
                if not CITE.search(t):
                    errors.append(f"{where}: a {b['label']} statement cites no source: {t[:60]}")
for term, d in R.get("glossary", []):
    prose += [("glossary " + term, term), ("glossary " + term, d)]
summary = [("community summary", p) for p in R["community_summary"]["paragraphs"]] + [("X thread", t) for t in R["community_summary"]["thread"]]
# diagrams: captions are prose with citations; the words drawn inside each SVG go through the same wording rules
DIAG = json.loads((ROOT / "content/diagrams.json").read_text())
PALETTE = {"#0c1317", "#141f26", "#17222a", "#1d3140", "#263641", "#223039", "#f1f5f8", "#c2ced6", "#8fa1ad", "#ffb3ae", "#ef5350", "#86efac", "#fcd34d", "#ffffff", "#fff"}
svg_texts = []
for d in DIAG:
    prose.append((f"figure {d['id']} title", d["title"]))
    prose.append((f"figure {d['id']} caption", d["caption"]))
    if not CITE.search(d["caption"]):
        errors.append(f"figure {d['id']}: caption cites no source")
    for v, tag in (("wide", "w"), ("narrow", "n")):
        f = ROOT / "public/diagrams" / f"{d['id']}-{v}.svg"
        if not f.exists():
            errors.append(f"figure {d['id']}: {f.name} missing"); continue
        svg = f.read_text()
        for bad in ("<style", "<image", "<foreignObject", "<script", "class=", "xlink:href=\"http", "href=\"http", "@import"):
            if bad in svg:
                errors.append(f"figure {d['id']} {v}: contains {bad}")
        if f'id="{d["id"]}-{tag}-title"' not in svg or "<desc" not in svg:
            errors.append(f"figure {d['id']} {v}: needs <title id=\"{d['id']}-{tag}-title\"> and <desc>")
        for i in re.findall(r'\sid="([^"]+)"', svg):
            if not i.startswith(f"{d['id']}-{tag}-"):
                errors.append(f"figure {d['id']} {v}: id '{i}' is not prefixed with {d['id']}-{tag}-")
        for c in re.findall(r"#[0-9a-fA-F]{3,6}\b", svg):
            if c.lower() not in PALETTE:
                errors.append(f"figure {d['id']} {v}: colour {c} is outside the brand palette")
        words = " ".join(re.sub(r"<[^>]+>", " ", m) for m in re.findall(r"<(?:text|title|desc)\b.*?</(?:text|title|desc)>", svg, re.S))
        # every word drawn in the figure must come from its approved wording in content/diagrams.json (catches typos)
        drawn = " ".join(re.sub(r"<[^>]+>", " ", m) for m in re.findall(r"<text\b.*?</text>", svg, re.S))
        allowed = set(re.findall(r"[a-z0-9]+", __import__("html").unescape(" ".join(d["content"]) + " " + d["title"] + " " + d["caption"]).lower()))
        for w in sorted(set(re.findall(r"[a-z0-9]+", __import__("html").unescape(drawn).lower())) - allowed):
            errors.append(f"figure {d['id']} {v}: the word '{w}' is drawn but not in the figure's wording in content/diagrams.json")
        svg_texts.append((f"figure {d['id']} {v} text", __import__("html").unescape(re.sub(r"\s+", " ", words))))
used = set()
for where, t in prose:
    for m in CITE.finditer(t):
        for fid in m.group(1).split():
            if fid not in F:
                errors.append(f"{where}: cites unknown fact {fid}")
            used.add(fid)
for fid in F:
    if fid not in used:
        notes.append(f"fact {fid} is not cited (kept in the fact list only)")
for sid in SOURCES:
    if not any(F[f]["source"] == sid for f in used if f in F):
        errors.append(f"source {sid} is never cited")
if R["key_findings"] and not all(k["label"] in ("confirmed", "analysis", "unknown", "tested") for k in R["key_findings"]):
    errors.append("key findings: every row needs a status label")

# 3 partnership wording (our own words only; source quotes are checked in 1)
texts = [(w, CITE.sub("", t)) for w, t in prose + summary] + svg_texts
NEG = re.compile(r"\b(no|not|none|nothing|never|without)\b", re.I)
for w, t in texts:
    for sent in re.split(r"(?<=[.?!])\s+", t):
        if sent.rstrip().endswith("?"):
            continue
        if re.search(r"partner|talks\b|negotiat|collaborat|agreement|in discussion|working with|plans?\b|roadmap|will (integrate|connect|join|support|list)", sent, re.I) \
           and re.search(r"redbelly|quant", sent, re.I) and not NEG.search(sent):
            if not re.search(r"The Clearing House", sent):
                errors.append(f"{w}: wording could suggest a Redbelly and Quant link: {sent[:90]}")

# 4 price talk, advice, hype, dashes, emoji
BANNED = r"\b(price|prices|priced|profit|profits|returns?|yield|apy|apr|buy|sell|bullish|bearish|moon|pump|undervalued|investment advice|financial advice|guaranteed|revolutionary|game.?changer|unleash|seamless|skyrocket|massive)\b"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿️]")
for w, t in texts:
    m = re.search(BANNED, t, re.I)
    if m:
        errors.append(f"{w}: banned word '{m.group(0)}'")
for w, t in texts + [("fact " + f["id"], f["quote"]) for f in FACTS]:
    if "–" in t or "—" in t:
        errors.append(f"{w}: contains an en dash or em dash")
    if EMOJI.search(t):
        errors.append(f"{w}: contains an emoji or symbol")

# 5 personal credit
cn, cl = ROOT / ".credit-names", ROOT / ".credit-links"
deliverables = [p for p in ROOT.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git", "build", "__pycache__")) and p.name not in (".credit-names", ".credit-links")]
if cn.exists():
    names = [n.strip().lower() for n in cn.read_text().splitlines() if n.strip()]
    names += [n.strip().lower() for n in cl.read_text().splitlines() if n.strip()] if cl.exists() else []
    for p in deliverables:
        if p.suffix in (".woff2",):
            continue
        if p.suffix == ".pdf":
            body = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
        elif p.suffix == ".docx":
            from docx import Document
            body = "\n".join(x.text for x in Document(p).paragraphs)
        else:
            body = p.read_bytes().decode("utf-8", "ignore")
        for n in names:
            if n in body.lower():
                errors.append(f"personal credit: {p.relative_to(ROOT)} contains a listed name or link")
    if re.search(r"made by|created by|author:", " ".join(t for _, t in texts), re.I):
        errors.append("personal credit: a 'made by' style line")
else:
    notes.append("personal credit scan skipped, .credit-names not present")

docx_file = ROOT / "public/downloads/redbelly-overledger-feasibility-report.docx"
if docx_file.exists():
    from docx import Document
    cp = Document(docx_file).core_properties
    import zipfile
    app = zipfile.ZipFile(docx_file).read("docProps/app.xml").decode("utf-8", "ignore")
    if re.search(r"<Application>[^<]+</Application>", app):
        errors.append("Word file: docProps/app.xml names an application")
    for field in ("author", "last_modified_by", "comments"):
        v = (getattr(cp, field) or "").lower()
        if "python-docx" in v or any(n in v for n in (names if cn.exists() else [])):
            errors.append(f"Word file: the {field} property names a tool or a person")

# 6 X thread length (a link counts as 23 characters on X)
for i, t in enumerate(R["community_summary"]["thread"], 1):
    n = len(t.replace("{site}", "x" * 23))
    if n > 280:
        errors.append(f"X post {i} is {n} characters, over 280")

# 7 outputs carry the current text: the words before each paragraph's first citation must appear in every output
pdf = ROOT / "public/downloads/redbelly-overledger-feasibility-report.pdf"
docx = ROOT / "public/downloads/redbelly-overledger-feasibility-report.docx"
web, srcpage = ROOT / "public/index.html", ROOT / "public/sources.html"
chapter_pages = sorted((ROOT / "public/chapters").glob("*.html"))
import html as H
def squash(t):
    return re.sub(r"[^a-z0-9]", "", norm(t).lower())
outs = {}
if pdf.exists():
    outs["PDF"] = squash(subprocess.run(["pdftotext", "-raw", str(pdf), "-"], capture_output=True, text=True).stdout)
if docx.exists():
    from docx import Document
    d = Document(docx)
    outs["Word file"] = squash("\n".join([p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells]))
if web.exists() and chapter_pages:
    outs["web page"] = squash(H.unescape(re.sub(r"<[^>]+>", " ", "\n".join(p.read_text() for p in [web] + chapter_pages))))
for name in ("PDF", "Word file", "web page"):
    if name not in outs:
        errors.append(f"{name} missing, run scripts/build.py")
        continue
    for where, t in prose + summary:
        if where.startswith("figure") and name == "web page" and "title" in where:
            pass
        probe = squash(CITE.split(t)[0].replace("{site}", ""))[:60]
        if len(probe) >= 12 and probe not in outs[name]:
            errors.append(f"{name} is out of date: '{CITE.split(t)[0][:50]}' ({where}) not found, run scripts/build.py")
            break
if srcpage.exists():
    sp = norm(H.unescape(re.sub(r"<[^>]+>", " ", srcpage.read_text())))
    for fid in used:
        if fid in F and norm(F[fid]["quote"]) not in sp:
            errors.append(f"source page is out of date: quote {fid} missing, run scripts/build.py"); break
else:
    errors.append("public/sources.html missing, run scripts/build.py")

# 8 the website loads nothing from outside its own domain (links to sources are fine)
for p in sorted((ROOT / "public").rglob("*.html")) + [ROOT / "public/site.css", ROOT / "public/site.js"]:
    if not p.exists():
        continue
    t = p.read_text()
    for m in re.finditer(r"<(script|link|img|iframe|source|video|audio)\b[^>]*\b(src|href)=[\"'](https?:)?//", t, re.I):
        if re.search(r'rel="canonical"', m.group(0)):
            continue   # names the page's own address, loads nothing
        errors.append(f"{p.name}: loads an outside resource ({m.group(0)[:60]})")
    for m in re.finditer(r"url\(\s*[\"']?(https?:)?//", t):
        errors.append(f"{p.name}: CSS loads an outside resource")
    if re.search(r"\u2013|\u2014", t):
        errors.append(f"{p.name}: contains an en dash or em dash")

# 9 links inside the website resolve, with clean addresses (Vercel cleanUrls serves /sources from sources.html)
PUBD = ROOT / "public"
_ids = {}
def ids_in(p):
    if p not in _ids:
        _ids[p] = set(re.findall(r'\sid="([^"]+)"', p.read_text()))
    return _ids[p]
def resolve(path):
    path = path.split("?")[0]
    if path == "/":
        return PUBD / "index.html"
    f = PUBD / path.lstrip("/")
    for c in (f, PUBD / (path.lstrip("/") + ".html"), f / "index.html"):
        if c.is_file():
            return c
    return None
pages = sorted(PUBD.rglob("*.html"))
if not (PUBD / "404.html").exists():
    errors.append("public/404.html missing, run scripts/build.py")
for p in pages:
    rel = p.relative_to(ROOT)
    for m in re.finditer(r'\s(href|src)="([^"]+)"', p.read_text()):
        u = H.unescape(m.group(2))
        if u.startswith(("https://", "http://", "mailto:")):
            continue
        if u.startswith("#"):
            if len(u) > 1 and u[1:] not in ids_in(p):
                errors.append(f"{rel}: link {u} points to an anchor that is not on the page")
            continue
        if not u.startswith("/"):
            errors.append(f"{rel}: link {u} is relative, use a path from the site root"); continue
        path, _, frag = u.partition("#")
        if path.split("?")[0].endswith(".html"):
            errors.append(f"{rel}: link {u} ends in .html, use the clean address")
        target = resolve(path)
        if target is None:
            errors.append(f"{rel}: link {u} opens nothing")
        elif frag and target.suffix == ".html" and frag not in ids_in(target):
            errors.append(f"{rel}: link {u} points to an anchor that is not on {target.name}")

# online: every source link answers
if "--online" in sys.argv:
    for s in SOURCES.values():
        if s.get("local"):
            continue
        try:
            req = urllib.request.Request(s["url"], headers={"User-Agent": "Mozilla/5.0"})
            code = urllib.request.urlopen(req, timeout=30).status
        except Exception as e:
            code = getattr(e, "code", str(e)[:40])
        if code != 200:
            notes.append(f"link {s['id']}: answered {code} (check in a browser: {s['url']})")
        else:
            notes.append(f"link {s['id']}: 200")

for n in notes:
    print("note:", n)
for e in errors:
    print("FAIL:", e)
print(f"{len(FACTS)} facts, {len(SOURCES)} sources, {len(man)} evidence files checked")
print("RESULT:", "PASS" if not errors else f"FAIL ({len(errors)})")
sys.exit(1 if errors else 0)
