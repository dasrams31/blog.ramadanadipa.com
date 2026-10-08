#!/usr/bin/env python3
"""Blog web server + view counter API (stdlib only).

Serves ~/workspace/www/blog.ramadanadipa.com/ on 127.0.0.1:8081 plus:
  POST /api/hit            {"slug": "..."} -> {"views": N}   (dedupe 1/IP/hari)
  GET  /api/views?slug=a,b -> {"a": N, "b": M}

Counts = unique visitors per day per article (IP di-hash SHA-256, tidak disimpan mentah).
Caddy di depan otomatis menambah X-Forwarded-For, jadi IP asli tetap kebaca.
DB: ~/workspace/blog/data/views.db (WAL) — ikut persist saat VM reset.
"""
import hashlib
import json
import os
import sqlite3
from datetime import date
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOME = "/home/hatch"  # jangan pakai ~ : service jalan sebagai root
WEBROOT = os.path.join(HOME, "workspace/www/blog.ramadanadipa.com")
DBDIR = os.path.join(HOME, "workspace/blog/data")
DB = os.path.join(DBDIR, "views.db")


def db():
    os.makedirs(DBDIR, exist_ok=True)
    con = sqlite3.connect(DB, timeout=10)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""CREATE TABLE IF NOT EXISTS views(
        slug TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS hits(
        slug TEXT, ip_hash TEXT, day TEXT,
        PRIMARY KEY (slug, ip_hash, day))""")
    return con


def client_ip(handler):
    xff = handler.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return handler.client_address[0]


def record_hit(slug, ip):
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")[:120]
    if not slug:
        return None
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:32]
    today = date.today().isoformat()
    con = db()
    try:
        cur = con.execute(
            "INSERT OR IGNORE INTO hits(slug, ip_hash, day) VALUES (?,?,?)",
            (slug, ip_hash, today))
        if cur.rowcount:
            con.execute(
                "INSERT INTO views(slug, count) VALUES (?,1) "
                "ON CONFLICT(slug) DO UPDATE SET count = count + 1",
                (slug,))
            con.commit()
        row = con.execute("SELECT count FROM views WHERE slug=?", (slug,)).fetchone()
        return row[0] if row else 0
    finally:
        con.close()


def get_views(slugs):
    clean = ["".join(c for c in s if c.isalnum() or c in "-_")[:120] for s in slugs]
    clean = [s for s in clean if s][:50]
    if not clean:
        return {}
    con = db()
    try:
        rows = con.execute(
            f"SELECT slug, count FROM views WHERE slug IN ({','.join('?'*len(clean))})",
            clean).fetchall()
        out = {s: 0 for s in clean}
        out.update({s: c for s, c in rows})
        return out
    finally:
        con.close()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEBROOT, **kw)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path == "/api/hit":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n) or b"{}")
                views = record_hit(str(data.get("slug", "")), client_ip(self))
            except Exception:
                return self._json({"error": "bad request"}, 400)
            if views is None:
                return self._json({"error": "bad slug"}, 400)
            return self._json({"views": views})
        self.send_error(404)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/views":
            slugs = parse_qs(u.query).get("slug", [""])[0].split(",")
            return self._json(get_views(slugs))
        return super().do_GET()

    def log_message(self, *a):
        pass  # diam, hemat disk

    def end_headers(self):
        # RSS feed boleh diakses dari portfolio (JS fetch lintas subdomain)
        if urlparse(self.path).path == "/feed.xml":
            self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    db()  # pastikan tabel ada
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.serve_forever()
