#!/usr/bin/env python3
"""Local preview of public/ that follows vercel.json, so the site behaves here as it does on Vercel.

  python3 scripts/serve.py                  http://127.0.0.1:8000
  python3 scripts/serve.py 8080             another port
  python3 scripts/serve.py --host 0.0.0.0   reachable from other devices on the network, e.g. a phone

What it takes from vercel.json:
  cleanUrls       /chapters/what-is-overledger serves chapters/what-is-overledger.html, and an address that ends
                  in .html is redirected to its clean form (/index.html goes to /)
  trailingSlash   false: /sources/ is redirected to /sources, and /evidence serves evidence/index.html
  headers         every rule is applied, so the Content-Security-Policy and cache headers can be tried before a deploy
An address that matches no file answers 404 with public/404.html."""
import argparse, io, json, re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
VERCEL = json.loads((ROOT / "vercel.json").read_text())
CLEAN = VERCEL.get("cleanUrls", False)
NO_SLASH = VERCEL.get("trailingSlash") is False
# vercel.json writes its header sources in the regular expression form, such as /(.*) and /fonts/(.*)
HEADER_RULES = [(re.compile(rule["source"] + r"\Z"), [(h["key"], h["value"]) for h in rule["headers"]])
                for rule in VERCEL.get("headers", [])]


def inside_public(rel):
    """The file for a site path, or None if the path would leave public/."""
    target = (PUB / rel).resolve()
    return target if target == PUB or PUB in target.parents else None


class VercelPreview(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".woff2": "font/woff2", ".svg": "image/svg+xml",
                      ".json": "application/json", ".txt": "text/plain; charset=utf-8", ".md": "text/markdown; charset=utf-8"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUB), **kwargs)

    def end_headers(self):
        asked = getattr(self, "asked", "/")
        for pattern, pairs in HEADER_RULES:
            if pattern.match(asked):
                for key, value in pairs:
                    self.send_header(key, value)
        super().end_headers()

    def redirect(self, where, query):
        self.send_response(HTTPStatus.PERMANENT_REDIRECT)
        self.send_header("Location", quote(where) + (f"?{query}" if query else ""))
        self.send_header("Content-Length", "0")
        self.end_headers()

    def not_found(self):
        body = (PUB / "404.html").read_bytes()
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return io.BytesIO(body)

    def serve(self, rel):
        self.path = quote("/" + rel)
        return super().send_head()

    def send_head(self):
        parts = urlsplit(self.path)
        self.asked = asked = unquote(parts.path) or "/"
        if NO_SLASH and asked != "/" and asked.endswith("/"):
            return self.redirect(asked.rstrip("/") or "/", parts.query)
        if CLEAN and asked.endswith(".html"):
            clean = asked[:-len(".html")]
            if clean == "/index" or clean.endswith("/index"):
                clean = clean[:-len("index")].rstrip("/") or "/"
            return self.redirect(clean, parts.query)
        rel = asked.lstrip("/")
        target = inside_public(rel)
        if target is None:
            return self.not_found()
        if target.is_dir() and (target / "index.html").is_file():
            return self.serve(f"{rel}/index.html" if rel else "index.html")
        if target.is_file():
            return self.serve(rel)
        if CLEAN and (PUB / f"{rel}.html").is_file():
            return self.serve(f"{rel}.html")
        return self.not_found()


def main():
    ap = argparse.ArgumentParser(description="Preview public/ the way Vercel serves it, using the settings in vercel.json.")
    ap.add_argument("port", nargs="?", type=int, help="port to listen on (default 8000)")
    ap.add_argument("--port", dest="port_flag", type=int, help="the same, as an option")
    ap.add_argument("--host", default="127.0.0.1", help="address to listen on (default 127.0.0.1, this computer only)")
    args = ap.parse_args()
    port = args.port_flag or args.port or 8000
    server = ThreadingHTTPServer((args.host, port), VercelPreview)
    print(f"previewing {PUB} at http://{args.host}:{port}  (Ctrl+C stops it)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
