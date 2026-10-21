#!/usr/bin/env python3
"""Serves public/ on http://localhost:8000 the way Vercel does (cleanUrls): /sources opens sources.html,
/chapters/why-now opens chapters/why-now.html, and an unknown address shows 404.html.
Run: python3 scripts/serve.py [port]"""
import http.server, sys
from pathlib import Path

PUB = Path(__file__).resolve().parent.parent / "public"

class CleanUrls(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(PUB), **k)

    def send_head(self):
        path = self.path.split("?")[0].split("#")[0]
        if path.endswith(".html"):
            clean = "/" if path == "/index.html" else path[:-5]
            self.send_response(308); self.send_header("Location", clean); self.end_headers(); return None
        if path != "/" and not (PUB / path.lstrip("/")).is_file() and (PUB / (path.lstrip("/") + ".html")).is_file():
            self.path = path + ".html"
        elif path != "/" and not (PUB / path.lstrip("/")).exists():
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write((PUB / "404.html").read_bytes()); return None
        return super().send_head()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"serving {PUB} on http://localhost:{port}")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), CleanUrls).serve_forever()
