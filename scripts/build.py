#!/usr/bin/env python3
"""Builds every output of the report from content/report.json, content/facts.json, content/sources.json and the diagrams.

  public/index.html          home page: the short answer, key findings, how to read the labels and the list of chapters
  public/chapters/*.html     one page per chapter, served at /chapters/<name> (Vercel cleanUrls)
  public/sources.html        the source list, served at /sources: every source, the exact words relied on, and where each is cited
  public/evidence/           the saved copy of every source, manifest.json and our test logs, with an index page
  public/404.html            the page shown for an unknown address
  public/site.css, site.js   shared style and behaviour (copied from scripts/)
  public/brand/og.png        the link preview image
  public/downloads/          the report as PDF (Playwright print of build/print.html) and Word (python-docx),
                             plus SOURCES.md and COMMUNITY-SUMMARY.md
  SOURCES.md, COMMUNITY-SUMMARY.md at the repository root

The work is split by output: scripts/report_model.py reads the content and numbers sources and figures,
scripts/pages.py writes the HTML, scripts/word_file.py the Word file, and this file puts everything in place.
Diagrams are hand-written SVG in public/diagrams/ID-wide.svg and ID-narrow.svg, specified in content/diagrams.json."""
import shutil
from report_model import *
from pages import chapter_bodies, chapter_page, home_page, not_found_page, print_page, sources_page, write_evidence_index, CH_IDS, CH_SLUG
from word_file import build_docx, render_pngs

# ---------- Markdown ----------
def sources_md():
    L = ["# Source list", "", "Every factual claim in the report cites one of these sources as S1, S2 and so on. Under each source are the exact words the report relies on. "
         "Text snapshots of every page, with capture time and SHA-256, are in `evidence/` (see `evidence/manifest.json`).", ""]
    for sid in ORDER:
        s = SOURCES[sid]
        L.append(f"**S{NUM[sid]}. {s['publisher']}**: {s['title']}  ")
        line = src_url(s) + (f" (also `{s['url']}` in the repository)" if s.get("local") else "")
        L += [line + "  ", f"Archived copy: {s['archived']}"] if s.get("archived") else [line]
        L.append("")
        for f in FACTS.values():
            if f["source"] == sid and f["id"] in USED:
                L.append(f"- \"{f['quote']}\"")
        L.append("")
    return "\n".join(L)

def summary_md():
    cs = R["community_summary"]
    L = ["# Community summary", "", "Plain language summary of the report, ready to share.", ""] + [p.replace("{site}", SITE) + "\n" for p in cs["paragraphs"]]
    L += ["## As an X thread", ""] + [t.replace("{site}", SITE) + "\n" for t in cs["thread"]]
    return "\n".join(L)

def prepare_assets():
    shutil.copy(ROOT / "scripts/site.css", PUB / "site.css")
    shutil.copy(ROOT / "scripts/site.js", PUB / "site.js")
    (PUB / "evidence/tests").mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "evidence/tests").glob("*.txt"):
        shutil.copy(f, PUB / "evidence/tests" / f.name)
    # the saved copy of every source and the manifest of hashes are published with the site, so a reader can check any quote
    shutil.rmtree(PUB / "evidence/snapshots", ignore_errors=True)
    shutil.copytree(ROOT / "evidence/snapshots", PUB / "evidence/snapshots")
    shutil.copy(ROOT / "evidence/manifest.json", PUB / "evidence/manifest.json")
    write_evidence_index()
    from PIL import Image
    icon = PUB / "brand/icon.png"
    for size, name in ((32, "icon-32.png"), (180, "icon-180.png")):
        Image.open(icon).convert("RGBA").resize((size, size), Image.LANCZOS).save(PUB / "brand" / name, optimize=True)
    logo = PUB / "brand/dao-logo.png"
    im = Image.open(logo)
    if im.height > 200:
        im = im.convert("RGBA"); w = round(im.width * 176 / im.height)
        im.resize((w, 176), Image.LANCZOS).save(logo, optimize=True)

def make_og_image():
    """The 1200 x 630 link preview image (brand kit: the Open Graph size for any linked page)."""
    from playwright.sync_api import sync_playwright
    fonts = (PUB / "fonts").as_uri(); logo = (PUB / "brand/dao-logo.png").as_uri()
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'@font-face{{font-family:"BV";src:url({fonts}/be-vietnam-pro-latin-700-normal.woff2);font-weight:700}}'
            f'@font-face{{font-family:"BV";src:url({fonts}/be-vietnam-pro-latin-400-normal.woff2);font-weight:400}}'
            f'@font-face{{font-family:"JM";src:url({fonts}/jetbrains-mono-latin-500-normal.woff2);font-weight:500}}'
            'html,body{margin:0}body{width:1200px;height:630px;background:#0c1317;color:#f1f5f8;font-family:BV,sans-serif;position:relative;overflow:hidden}'
            '.band{position:absolute;inset:40px;background:#1d3140;border-radius:8px;padding:56px 64px}'
            '.k{display:flex;align-items:center;gap:14px;font:500 22px JM,monospace;letter-spacing:.08em;text-transform:uppercase;color:#8fa1ad}'
            '.k i{display:block;width:40px;height:6px;border-radius:3px;background:#EF5350}'
            'h1{font-size:68px;line-height:1.06;letter-spacing:-.02em;margin:26px 0 22px;max-width:860px}'
            'p{font-size:28px;line-height:1.4;color:#c2ced6;margin:0;max-width:820px}'
            '.v{position:absolute;left:64px;bottom:52px;font:500 22px JM,monospace;color:#ffb3ae}'
            'img{position:absolute;right:64px;bottom:44px;height:84px}</style></head><body><div class="band">'
            '<div class="k"><i></i>Redbelly DAO community research</div>'
            f'<h1>{esc(R["title"])}</h1><p>Feasibility research from public sources. No partnership or talks between Redbelly and Quant have been announced.</p>'
            f'<div class="v">Sources last verified {VERIFIED}</div><img src="{logo}" alt=""></div></body></html>')
    tmp = ROOT / "build/og.html"; tmp.write_text(page)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready.then(() => true)"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(PUB / "brand/og.png")); b.close()

# ---------- PDF ----------
PDF_FOOTER = ("<div style='font-family:sans-serif;font-size:9px;width:100%;padding:0 14mm;display:flex;justify-content:space-between;color:#5b6b76'>"
              "<span>Could Redbelly connect to Quant Overledger? Feasibility research only.</span><span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>")

def print_pdf(html_file, pdf_file):
    """A4, with a bookmark outline and tags for screen readers, and the page number in the footer."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(); pg = browser.new_page()
        pg.goto(html_file.as_uri()); pg.wait_for_timeout(600)
        pg.pdf(path=str(pdf_file), format="A4", print_background=True, outline=True, tagged=True,
               margin={"top": "14mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
               display_header_footer=True, header_template="<span></span>", footer_template=PDF_FOOTER)
        browser.close()

# ---------- putting it together ----------
def write_site():
    """The home page, one page per chapter (the folder is emptied first, so a renamed chapter leaves no old page), sources, 404."""
    bodies = chapter_bodies()
    (PUB / "index.html").write_text(home_page(bodies))
    chapters = PUB / "chapters"
    shutil.rmtree(chapters, ignore_errors=True); chapters.mkdir()
    for cid in CH_IDS:
        (chapters / f"{CH_SLUG[cid]}.html").write_text(chapter_page(cid, bodies[cid]))
    (PUB / "sources.html").write_text(sources_page())
    (PUB / "404.html").write_text(not_found_page())

def write_markdown():
    """SOURCES.md and COMMUNITY-SUMMARY.md at the repository root, with a copy of each in public/downloads/."""
    for name, text in (("SOURCES.md", sources_md()), ("COMMUNITY-SUMMARY.md", summary_md())):
        (ROOT / name).write_text(text)
        shutil.copy(ROOT / name, PUB / "downloads" / name)

def main():
    (PUB / "downloads").mkdir(parents=True, exist_ok=True); (ROOT / "build").mkdir(exist_ok=True)
    prepare_assets()
    make_og_image()
    write_site()
    print_html = ROOT / "build/print.html"
    print_html.write_text(print_page())
    print_pdf(print_html, PUB / "downloads" / PDF_NAME)
    build_docx(PUB / "downloads" / DOCX_NAME, render_pngs())
    write_markdown()
    print(f"built: {len(ORDER)} sources cited, {len(USED)} facts used, {len(FIGNUM)} figures")

if __name__ == "__main__":
    main()
