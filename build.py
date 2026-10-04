#!/usr/bin/env python3
"""Static blog generator for blog.ramadanadipa.com — stdlib only."""
import os, re, json, shutil, html
from datetime import date
from xml.sax.saxutils import escape as xesc

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, "content")
TPL = os.path.join(BASE, "templates")
STATIC = os.path.join(BASE, "static")
OUT = "/home/hatch/workspace/www/blog.ramadanadipa.com"
SITE = "https://blog.ramadanadipa.com"
AUTHOR = "Rama Danadipa Putra Wijaya"

# ── frontmatter ──────────────────────────────────────
def parse_post(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            fm = raw[3:end].strip()
            body = raw[end + 4:].lstrip("\n")
            key = None
            for line in fm.split("\n"):
                if re.match(r"^\s*-\s+", line) and key:
                    meta.setdefault(key, []).append(line.strip()[2:].strip().strip("'\""))
                elif ":" in line:
                    k, v = line.split(":", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if v == "":
                        key, meta[k] = k, []
                    else:
                        key, meta[k] = None, v
    fname = os.path.basename(path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", fname)
    d, slug = (m.group(1), m.group(2)) if m else (str(date.today()), fname[:-3])
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = tags.strip().strip("[]")
        tags = [t.strip().strip("'\"") for t in tags.split(",") if t.strip()]
    faqs = []
    if isinstance(meta.get("faq", []), list):
        items = meta["faq"]
        for i in range(0, len(items) - 1, 2):
            faqs.append((items[i], items[i + 1]))
    words = len(re.findall(r"\w+", body))
    return {
        "slug": slug, "date": meta.get("date", d),
        "title": meta.get("title", slug.replace("-", " ").title()),
        "description": meta.get("description", ""),
        "tags": [t.lower() for t in tags], "faqs": faqs,
        "draft": str(meta.get("draft", "")).lower() == "true",
        "body": body, "minutes": max(1, round(words / 200)),
        "url": f"{SITE}/posts/{slug}/",
    }

# ── markdown subset → html ───────────────────────────
def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s

def md_to_html(md):
    out, i, lines = [], 0, md.split("\n")
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            code = html.escape("\n".join(buf))
            out.append(f'<pre><code class="lang-{html.escape(lang)}">{code}</code></pre>')
            continue
        if re.match(r"^#{1,3}\s", line):
            lvl = len(line) - len(line.lstrip("#"))
            txt = line.lstrip("#").strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append(f'<h{lvl} id="{anchor}">{inline(txt)}</h{lvl}>')
        elif line.strip() == "---":
            out.append("<hr>")
        elif line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip()); i += 1
            out.append("<blockquote>" + "".join(f"<p>{inline(b)}</p>" for b in buf) + "</blockquote>")
            continue
        elif re.match(r"^(\s*[-*]\s+)", line):
            buf = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                buf.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
            continue
        elif re.match(r"^\s*\d+\.\s+", line):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ol>")
            continue
        elif line.strip() == "":
            pass
        else:
            buf = []
            while i < n and lines[i].strip() not in ("", "---") and not re.match(r"^(#{1,3}\s|```|>|(\s*[-*]\s+)|(\s*\d+\.\s+))", lines[i]):
                buf.append(lines[i].strip()); i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
            continue
        i += 1
    return "\n".join(out)

# ── templates ────────────────────────────────────────
def tpl(name, **kw):
    s = open(os.path.join(TPL, name), encoding="utf-8").read()
    for k, v in kw.items():
        s = s.replace("{{" + k + "}}", v)
    return s

def jsonld_article(p):
    d = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["description"],
        "datePublished": p["date"], "dateModified": p["date"],
        "author": {"@type": "Person", "name": AUTHOR, "url": "https://ramadanadipa.com/"},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "mainEntityOfPage": p["url"], "inLanguage": "id-ID",
    }
    parts = [json.dumps(d, ensure_ascii=False)]
    if p["faqs"]:
        parts.append(json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in p["faqs"]],
        }, ensure_ascii=False))
    return "\n".join(f'<script type="application/ld+json">{x}</script>' for x in parts)

def head_common(title, desc, url, jsonld=""):
    return tpl("head.html", title=html.escape(title), description=html.escape(desc),
               url=url, jsonld=jsonld)

def render_page(filename, head, body_html):
    page = tpl("base.html", head=head, content=body_html, year=str(date.today().year))
    dest = os.path.join(OUT, filename)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(page)

def id_date(iso):
    y, m, d = iso.split("-")
    bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
             "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    return f"{int(d)} {bulan[int(m)]} {y}"

def tag_slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

# ── page generators (continued) ──────────────────────
def card(p):
    tags = "".join(f'<a class="chip link" href="/tags/{tag_slug(t)}/">{html.escape(t)}</a>' for t in p["tags"][:3])
    return f"""<article class="card">
  <div class="card-top"><span class="card-date">{id_date(p['date'])}</span><span class="card-read">{p['minutes']} mnt baca</span></div>
  <h3><a href="/posts/{p['slug']}/">{html.escape(p['title'])}</a></h3>
  <p>{html.escape(p['description'])}</p>
  <div class="chips">{tags}</div>
</article>"""

def build_index(posts):
    latest = posts[0] if posts else None
    hero_post = ""
    if latest:
        hero_post = f"""<section class="hero-post">
  <p class="kicker">最新 — ARTIKEL TERBARU</p>
  <h2><a href="/posts/{latest['slug']}/">{html.escape(latest['title'])}</a></h2>
  <p class="lede">{html.escape(latest['description'])}</p>
  <a class="btn" href="/posts/{latest['slug']}/">Baca Artikel <span>→</span></a>
</section>"""
    grid = "\n".join(card(p) for p in posts[1:13])
    all_tags = sorted({t for p in posts for t in p["tags"]})
    tagcloud = "".join(f'<a class="chip link" href="/tags/{tag_slug(t)}/">{html.escape(t)}</a>' for t in all_tags[:24])
    body = tpl("index_body.html", hero_post=hero_post, grid=grid, tagcloud=tagcloud,
               count=str(len(posts)))
    head = head_common(
        "Blog — Rama Danadipa | Tutorial Laravel, React, AI & VPS",
        "Blog programming Indonesia: tutorial Laravel, React/Next.js, PostgreSQL, integrasi AI, dan deploy VPS. Artikel baru setiap hari.",
        SITE + "/",
        '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "Blog",
            "name": "Blog Rama Danadipa", "url": SITE + "/",
            "description": "Tutorial programming Indonesia: Laravel, React, PostgreSQL, AI, VPS.",
            "inLanguage": "id-ID",
            "author": {"@type": "Person", "name": AUTHOR, "url": "https://ramadanadipa.com/"},
        }, ensure_ascii=False) + "</script>")
    render_page("index.html", head, body)

def build_post(p, posts):
    body_html = md_to_html(p["body"])
    faq_html = ""
    if p["faqs"]:
        items = "".join(
            f"<details><summary>{html.escape(q)}</summary><p>{inline(a)}</p></details>"
            for q, a in p["faqs"])
        faq_html = f'<section class="faq"><h2>Pertanyaan Umum</h2>{items}</section>'
    related = [x for x in posts if x["slug"] != p["slug"]
               and set(x["tags"]) & set(p["tags"])][:3]
    rel_html = ""
    if related:
        rel_html = '<section class="related"><h2>Artikel Terkait</h2><div class="grid">' + \
                   "".join(card(r) for r in related) + "</div></section>"
    tags = "".join(f'<a class="chip link" href="/tags/{tag_slug(t)}/">{html.escape(t)}</a>' for t in p["tags"])
    toc = ""
    for m in re.finditer(r"<h2 id=\"([^\"]+)\">(.+?)</h2>", body_html):
        toc += f'<li><a href="#{m.group(1)}">{m.group(2)}</a></li>'
    toc_html = f'<nav class="toc"><p>DAFTAR ISI</p><ul>{toc}</ul></nav>' if toc else ""
    body = tpl("post_body.html", title=html.escape(p["title"]),
               date=id_date(p["date"]), minutes=str(p["minutes"]),
               tags=tags, toc=toc_html, article=body_html,
               faq=faq_html, related=rel_html)
    head = head_common(p["title"] + " — Blog Rama Danadipa", p["description"],
                       p["url"], jsonld_article(p))
    render_page(f"posts/{p['slug']}/index.html", head, body)

def build_tags(posts):
    by_tag = {}
    for p in posts:
        for t in p["tags"]:
            by_tag.setdefault(t, []).append(p)
    for t, ps in by_tag.items():
        grid = "\n".join(card(p) for p in ps)
        body = tpl("tag_body.html", tag=html.escape(t), count=str(len(ps)), grid=grid)
        head = head_common(f"Topik: {t} — Blog Rama Danadipa",
                           f"Kumpulan artikel tentang {t}: tutorial dan tips programming Indonesia.",
                           f"{SITE}/tags/{t}/")
        render_page(f"tags/{tag_slug(t)}/index.html", head, body)

def build_sitemap(posts):
    urls = [(SITE + "/", date.today().isoformat())]
    for p in posts:
        urls.append((p["url"], p["date"]))
    for t in {x for p in posts for x in p["tags"]}:
        urls.append((f"{SITE}/tags/{tag_slug(t)}/", date.today().isoformat()))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in urls:
        xml.append(f"  <url><loc>{xesc(u)}</loc><lastmod>{lm}</lastmod></url>")
    xml.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(xml))

def build_rss(posts):
    items = []
    for p in posts[:20]:
        items.append(f"""<item>
<title>{xesc(p['title'])}</title>
<link>{xesc(p['url'])}</link>
<guid>{xesc(p['url'])}</guid>
<pubDate>{p['date']}T07:00:00+07:00</pubDate>
<description>{xesc(p['description'])}</description>
</item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Blog Rama Danadipa</title>
<link>{SITE}/</link>
<description>Tutorial programming Indonesia: Laravel, React, PostgreSQL, AI, VPS.</description>
<language>id-ID</language>
{''.join(items)}
</channel></rss>"""
    open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8").write(rss)

def build_robots():
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

def main():
    posts = []
    for f in sorted(os.listdir(CONTENT)):
        if not f.endswith(".md"):
            continue
        p = parse_post(os.path.join(CONTENT, f))
        if not p["draft"]:
            posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    shutil.copytree(STATIC, os.path.join(OUT, "assets"))
    build_index(posts)
    for p in posts:
        build_post(p, posts)
    build_tags(posts)
    build_sitemap(posts)
    build_rss(posts)
    build_robots()
    print(f"built {len(posts)} posts -> {OUT}")

if __name__ == "__main__":
    main()
