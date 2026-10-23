#!/usr/bin/env python3
"""The report as data, shared by every output: paths, the content files, labels and source groups, and the reading-order
walk that numbers the sources (S1, S2 ...) and the figures and records where each fact is used.
Imported by scripts/pages.py, scripts/word_file.py and scripts/build.py; it writes nothing."""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://overledger.vercel.app"
PDF_NAME = "redbelly-overledger-feasibility-report.pdf"
DOCX_NAME = "redbelly-overledger-feasibility-report.docx"
VERIFIED = "15 Oct 2026"

def load(name):
    return json.loads((ROOT / "content" / name).read_text())

def by_id(items):
    return {x["id"]: x for x in items}

R = load("report.json")
FACTS, SOURCES, DIAGRAMS = by_id(load("facts.json")), by_id(load("sources.json")), by_id(load("diagrams.json"))
CITE = re.compile(r"\{([a-z0-9 -]+)\}")   # {fact-id other-fact-id} inside the report text
LABELS = {"confirmed": "Confirmed", "tested": "Tested", "analysis": "Analysis", "unknown": "Unknown"}
# Where each diagram sits: (section id, index of the block it follows; -1 = straight after the section intro)
FIG_AT = {"stack": ("overledger", 0), "routes": ("how-connect", 0), "access": ("redbelly", 2), "levels": ("now", -1),
          "work": ("work", -1), "receptor": ("compliance", 0), "breaks": ("compliance", 1)}
GROUPS = [("g-brief", "The task brief", ["brief"]),
          ("g-tch", "The Clearing House and Quant", ["tch", "quant-pr"]),
          ("g-ol", "Overledger documentation", ["ol-"]),
          ("g-rb", "Redbelly technical documentation", ["rb-"]),
          ("g-vine", "Vine, Redbelly developer portal", ["vine-"]),
          ("g-bridges", "Bridge announcements", ["celer", "x-wrbnt"]),
          ("g-tk", "Tokeniser", ["tk-"]),
          ("g-task", "Earlier Task Board research", ["task"]),
          ("g-test", "Our own tests", ["test-"])]

def group_of(sid):
    """The source list group of a source id. A key ending in '-' takes every id with that prefix; 'task' takes every task id."""
    for gid, _, keys in GROUPS:
        for k in keys:
            if sid == k or ((k.endswith("-") or k == "task") and sid.startswith(k)):
                return gid
    raise SystemExit(f"source {sid} has no group")

def esc(s):
    return html.escape(s, quote=True)

def strip_num(title):
    return re.sub(r"^\d+\.\s*", "", title)

def nn(i):
    return f"{i:02d}"

# ---------- reading order: number the sources and figures, and record where each fact is used ----------
SEC = {s["id"]: s for s in R["sections"]}
SEC_NUM = {s["id"]: i for i, s in enumerate(R["sections"], 1)}
FIGS_AT = {}   # (section id, block index) -> diagram ids placed there, in FIG_AT order
for _did, _spot in FIG_AT.items():
    if _did in DIAGRAMS:
        FIGS_AT.setdefault(_spot, []).append(_did)

def figs_for(sec_id, after):
    return FIGS_AT.get((sec_id, after), [])

def cited_ids(text):
    """The fact ids a piece of text cites, in the order they appear."""
    return [fid for m in CITE.finditer(text) for fid in m.group(1).split()]

def reading_order(fignum):
    """Yields every cited piece of the report as (text, where), in the order a reader meets it,
    and gives each figure its number in fignum as it is reached."""
    yield R["status_note"], "top"
    for k in R["key_findings"]:
        yield "{" + k["cite"] + "}", "findings"
    for s in R["sections"]:
        sid = s["id"]
        yield s.get("intro", ""), sid
        for after in range(-1, len(s["blocks"])):
            if after >= 0:
                b = s["blocks"][after]
                yield b.get("text", ""), sid
                for li in b.get("list", []):
                    yield li, sid
                for row in b.get("rows", []):
                    yield "{" + row[2] + "}", sid
            for did in figs_for(sid, after):
                fignum[did] = len(fignum) + 1
                yield DIAGRAMS[did]["caption"], sid

ORDER, USED_IN, FIGNUM = [], {}, {}   # sources in first-cited order; fact id -> places used; figure id -> number
for _text, _where in reading_order(FIGNUM):
    for _fid in cited_ids(_text):
        if _fid not in FACTS:
            raise SystemExit(f"unknown fact {_fid} in {_where}")
        if FACTS[_fid]["source"] not in ORDER:
            ORDER.append(FACTS[_fid]["source"])
        _places = USED_IN.setdefault(_fid, [])
        if _where not in _places:
            _places.append(_where)
NUM = {sid: n for n, sid in enumerate(ORDER, 1)}
USED = set(USED_IN)

def source_num(fid):
    return NUM[FACTS[fid]["source"]]

FIXED_PLACES = {"top": "Opening note", "findings": "Key findings"}

def where_label(w):
    """(label, id) for a place a fact is used: the opening note, the key findings, or a numbered chapter."""
    return (FIXED_PLACES[w], w) if w in FIXED_PLACES else (f"{SEC_NUM[w]}. {SEC[w]['short']}", w)

def plain(t):
    """Text for the Word file: each {fact ids} becomes [S3, S7], the numbers of their sources."""
    def numbers(m):
        return " [" + ", ".join(f"S{n}" for n in sorted({source_num(f) for f in m.group(1).split()})) + "]"
    return re.sub(r"\s*\{([a-z0-9 -]+)\}", numbers, t)

def src_url(s):
    """Our own test logs live on this site; every other source is its original page."""
    return f"{SITE}/{s['url']}" if s.get("local") else s["url"]
