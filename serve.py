#!/usr/bin/env python3
"""Blog web server + view counter API (stdlib only).

Serves ~/workspace/www/blog.ramadanadipa.com/ on 127.0.0.1:8081 plus:
  POST /api/hit            {"slug": "..."} -> {"views": N}   (dedupe 1/IP/hari)
  GET  /api/views?slug=a,b -> {"a": N, "b": M}
  POST /api/like           {"slug": "..."} -> {"likes": N, "liked": bool} (toggle 1/IP)
  GET  /api/likes?slug=a,b -> {"a": N, "b": M}
  POST /api/comments       {"slug","name","body"} -> {"ok": true, "comment": {...}}
  GET  /api/comments?slug=x -> {"comments": [...]} (terbaru dulu, maks 50)

Counts = unique visitors per day per article (IP di-hash SHA-256, tidak disimpan mentah).
Caddy di depan otomatis menambah X-Forwarded-For, jadi IP asli tetap kebaca.
DB: ~/workspace/blog/data/views.db (WAL) — ikut persist saat VM reset.
"""
import hashlib
import json
import os
import sqlite3
import time
from datetime import date, datetime, timezone
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
    con.execute("""CREATE TABLE IF NOT EXISTS likes(
        slug TEXT PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS like_hits(
        slug TEXT, ip_hash TEXT,
        PRIMARY KEY (slug, ip_hash))""")
    con.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL,
        name TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS comment_hits(
        ip_hash TEXT PRIMARY KEY, ts INTEGER NOT NULL)""")
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


def clean_slug(slug):
    return "".join(c for c in str(slug) if c.isalnum() or c in "-_")[:120]


def get_likes(slugs):
    clean = [clean_slug(s) for s in slugs]
    clean = [s for s in clean if s][:50]
    if not clean:
        return {}
    con = db()
    try:
        rows = con.execute(
            f"SELECT slug, count FROM likes WHERE slug IN ({','.join('?'*len(clean))})",
            clean).fetchall()
        out = {s: 0 for s in clean}
        out.update({s: c for s, c in rows})
        return out
    finally:
        con.close()


def toggle_like(slug, ip):
    slug = clean_slug(slug)
    if not slug:
        return None
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:32]
    con = db()
    try:
        cur = con.execute(
            "INSERT OR IGNORE INTO like_hits(slug, ip_hash) VALUES (?,?)",
            (slug, ip_hash))
        if cur.rowcount:
            liked = True
            con.execute(
                "INSERT INTO likes(slug, count) VALUES (?,1) "
                "ON CONFLICT(slug) DO UPDATE SET count = count + 1",
                (slug,))
        else:
            liked = False
            con.execute("DELETE FROM like_hits WHERE slug=? AND ip_hash=?",
                        (slug, ip_hash))
            con.execute(
                "UPDATE likes SET count = MAX(count - 1, 0) WHERE slug=?",
                (slug,))
        con.commit()
        row = con.execute("SELECT count FROM likes WHERE slug=?", (slug,)).fetchone()
        return {"likes": row[0] if row else 0, "liked": liked}
    finally:
        con.close()


def list_comments(slug):
    slug = clean_slug(slug)
    if not slug:
        return None
    con = db()
    try:
        rows = con.execute(
            "SELECT id, name, body, created_at FROM comments "
            "WHERE slug=? ORDER BY id DESC LIMIT 50", (slug,)).fetchall()
        return [{"id": i, "name": n, "body": b, "created_at": c}
                for i, n, b, c in rows]
    finally:
        con.close()


COMMENT_RATE_SECONDS = 30


def add_comment(slug, name, body, ip):
    slug = clean_slug(slug)
    if not slug:
        return None, "bad slug"
    name = " ".join(str(name).split())[:40]
    body = str(body).strip()[:500]
    if not name:
        return None, "nama wajib diisi"
    if not body:
        return None, "komentar wajib diisi"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:32]
    now = int(time.time())
    con = db()
    try:
        row = con.execute("SELECT ts FROM comment_hits WHERE ip_hash=?",
                          (ip_hash,)).fetchone()
        if row and now - row[0] < COMMENT_RATE_SECONDS:
            return None, "tunggu sebentar sebelum kirim komentar lagi"
        created_at = datetime.now(timezone.utc).isoformat()
        cur = con.execute(
            "INSERT INTO comments(slug, name, body, created_at) "
            "VALUES (?,?,?,?)", (slug, name, body, created_at))
        con.execute(
            "INSERT INTO comment_hits(ip_hash, ts) VALUES (?,?) "
            "ON CONFLICT(ip_hash) DO UPDATE SET ts = excluded.ts",
            (ip_hash, now))
        con.commit()
        return {"id": cur.lastrowid, "name": name, "body": body,
                "created_at": created_at}, None
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
        path = urlparse(self.path).path
        if path == "/api/hit":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n) or b"{}")
                views = record_hit(str(data.get("slug", "")), client_ip(self))
            except Exception:
                return self._json({"error": "bad request"}, 400)
            if views is None:
                return self._json({"error": "bad slug"}, 400)
            return self._json({"views": views})
        if path == "/api/like":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n) or b"{}")
                res = toggle_like(str(data.get("slug", "")), client_ip(self))
            except Exception:
                return self._json({"error": "bad request"}, 400)
            if res is None:
                return self._json({"error": "bad slug"}, 400)
            return self._json(res)
        if path == "/api/comments":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n) or b"{}")
                comment, err = add_comment(data.get("slug", ""), data.get("name", ""),
                                           data.get("body", ""), client_ip(self))
            except Exception:
                return self._json({"error": "bad request"}, 400)
            if err == "bad slug":
                return self._json({"error": "bad slug"}, 400)
            if err:
                code = 429 if err.startswith("tunggu") else 400
                return self._json({"error": err}, code)
            return self._json({"ok": True, "comment": comment})
        self.send_error(404)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/views":
            slugs = parse_qs(u.query).get("slug", [""])[0].split(",")
            return self._json(get_views(slugs))
        if u.path == "/api/likes":
            slugs = parse_qs(u.query).get("slug", [""])[0].split(",")
            return self._json(get_likes(slugs))
        if u.path == "/api/comments":
            slug = parse_qs(u.query).get("slug", [""])[0]
            comments = list_comments(slug)
            if comments is None:
                return self._json({"error": "bad slug"}, 400)
            return self._json({"comments": comments})
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
