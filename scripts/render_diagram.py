#!/usr/bin/env python3
"""Renders one diagram SVG to PNG and measures it, so a diagram can be checked by eye and by numbers.
  python3 scripts/render_diagram.py public/diagrams/levels-wide.svg out.png [display_width]
display_width is the width the SVG is drawn at on the page: 778 for a wide diagram (the desktop content column),
332 for a narrow one on a 390 px phone (the narrow version is also used up to 860 px, drawn at up to 520 px).
The report prints JSON with:
  min_font_px     smallest rendered text size at that display width (aim for >= 11 everywhere; on a phone the
                  Full screen button shows the wide version at its natural size, where the smallest text is 14 px)
  overlaps        pairs of text elements whose boxes overlap
  outside         text elements that spill outside the SVG viewBox
  text_over_edge  text elements that cross the edge of the rect or path they sit in
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
FONTS = (ROOT / "public/fonts").as_uri()

def main():
    svg_path, out = Path(sys.argv[1]), sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 778
    svg = svg_path.read_text()
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:"Be Vietnam Pro";src:url({FONTS}/be-vietnam-pro-latin-400-normal.woff2);font-weight:400}}
@font-face{{font-family:"Be Vietnam Pro";src:url({FONTS}/be-vietnam-pro-latin-500-normal.woff2);font-weight:500}}
@font-face{{font-family:"Be Vietnam Pro";src:url({FONTS}/be-vietnam-pro-latin-600-normal.woff2);font-weight:600}}
@font-face{{font-family:"Be Vietnam Pro";src:url({FONTS}/be-vietnam-pro-latin-700-normal.woff2);font-weight:700}}
@font-face{{font-family:"JetBrains Mono";src:url({FONTS}/jetbrains-mono-latin-400-normal.woff2);font-weight:400}}
@font-face{{font-family:"JetBrains Mono";src:url({FONTS}/jetbrains-mono-latin-500-normal.woff2);font-weight:500}}
html,body{{margin:0;background:#141f26;font-family:"Be Vietnam Pro"}} .f1{{font:700 1px "Be Vietnam Pro"}} .f2{{font:600 1px "Be Vietnam Pro"}} .f3{{font:500 1px "Be Vietnam Pro"}} .f4{{font:400 1px "JetBrains Mono"}} .f5{{font:500 1px "JetBrains Mono"}} .wrap{{width:{width}px;padding:16px}} svg{{display:block;width:100%;height:auto}}
</style></head><body><div class="wrap">{svg}</div><span class="f1">a</span><span class="f2">a</span><span class="f3">a</span><span class="f4">a</span><span class="f5">a</span></body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width + 32, "height": 800}, device_scale_factor=2)
        # Load from a file URL so the local @font-face files load; set_content runs on about:blank and silently falls back.
        tmp = Path(__import__("tempfile").gettempdir()) / f"render-{svg_path.stem}-{width}.html"; tmp.write_text(page)
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready.then(() => true)"); pg.wait_for_timeout(300)
        loaded = pg.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight)")
        if not any("Be Vietnam Pro" in f for f in loaded):
            raise SystemExit("fonts did not load, measurements would be wrong")
        report = pg.evaluate("""() => {
          const svg = document.querySelector('svg');
          const vb = svg.viewBox.baseVal; const r = svg.getBoundingClientRect();
          const scale = r.width / vb.width;
          const texts = [...svg.querySelectorAll('text')];
          const boxes = texts.map(t => ({t: t.textContent.trim().slice(0, 40), b: t.getBoundingClientRect(),
             fs: parseFloat(getComputedStyle(t).fontSize) * scale}));
          const minfs = Math.min(...boxes.map(x => x.fs));
          const overlaps = [];
          for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
            const a = boxes[i].b, c = boxes[j].b;
            const ox = Math.min(a.right, c.right) - Math.max(a.left, c.left);
            const oy = Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top);
            if (ox > 1 && oy > 2) overlaps.push([boxes[i].t, boxes[j].t]);
          }
          const outside = boxes.filter(x => x.b.left < r.left - 1 || x.b.right > r.right + 1 || x.b.top < r.top - 1 || x.b.bottom > r.bottom + 1).map(x => x.t);
          // text that crosses the border of the smallest rect containing its start point
          const rects = [...svg.querySelectorAll('rect')].map(e => e.getBoundingClientRect()).filter(b => b.width > 30 && b.height > 16);
          const over = [];
          boxes.forEach(x => {
            const cx = x.b.left + 2, cy = x.b.top + x.b.height / 2;
            const host = rects.filter(b => cx >= b.left && cx <= b.right && cy >= b.top && cy <= b.bottom)
                              .sort((p, q) => p.width * p.height - q.width * q.height)[0];
            if (host && (x.b.right > host.right + 1 || x.b.bottom > host.bottom + 1)) over.push(x.t);
          });
          return {display_width: r.width, scale: +scale.toFixed(3), texts: texts.length, min_font_px: +minfs.toFixed(1),
                  overlaps, outside, text_over_edge: over};
        }""")
        pg.locator(".wrap").screenshot(path=out)
        b.close()
    print(json.dumps(report, indent=1))

if __name__ == "__main__":
    main()
