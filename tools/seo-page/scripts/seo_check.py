#!/usr/bin/env python3
"""seo_check.py FILE_OR_URL [--url CANONICAL] [--private] [--min-words N]
Lint one rendered HTML page for the basics crawlers and link previews need. Prints FAIL / WARN / ok lines; exit 1 on any FAIL.
Read-only: fetches a URL with GET or reads a local file. For PHP/templates lint the rendered output (a local server URL), not the source.
"""
import sys, re, json, argparse, urllib.request
from html.parser import HTMLParser

class Page(HTMLParser):
    VOID_SKIP = {"script", "style", "template", "svg"}
    def __init__(s):
        super().__init__(convert_charrefs=True)
        s.lang = None; s.title = ""; s.meta = {}; s.links = []; s.h = {}; s.jsonld = []; s.imgs = []; s.anchors = []
        s.text = []; s._in = []; s._buf = None; s._a = None; s.charset = False; s.noscript = 0
    def handle_starttag(s, t, attrs):
        a = dict(attrs)
        if t == "html": s.lang = a.get("lang")
        if t == "meta":
            if a.get("charset"): s.charset = True
            k = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if k: s.meta.setdefault(k, a.get("content") or "")
        if t == "link": s.links.append(a)
        if t == "img": s.imgs.append(a)
        if t == "a": s._a = [a.get("href"), "", a.get("aria-label") or a.get("title") or ""]
        if t == "title" or re.fullmatch(r"h[1-6]", t): s._buf = [t, ""]
        if t == "script" and (a.get("type") or "").lower() == "application/ld+json": s._buf = ["ld", ""]
        if t == "noscript": s.noscript += 1
        if t in s.VOID_SKIP: s._in.append(t)
    def handle_endtag(s, t):
        if s._in and s._in[-1] == t: s._in.pop()
        if t == "noscript" and s.noscript: s.noscript -= 1
        if t == "a" and s._a: s.anchors.append(s._a); s._a = None
        if s._buf and (t == s._buf[0] or (s._buf[0] == "ld" and t == "script")):
            k, v = s._buf; s._buf = None
            if k == "title": s.title = " ".join(v.split())
            elif k == "ld": s.jsonld.append(v)
            else: s.h.setdefault(k, []).append(" ".join(v.split()))
    def handle_data(s, d):
        if s._buf: s._buf[1] += d
        if s._in: return
        if s._a is not None: s._a[1] += d
        s.text.append(d)
    def handle_startendtag(s, t, attrs):
        s.handle_starttag(t, attrs)
        if t == "a" and s._a: s.anchors.append(s._a); s._a = None

def load(src):
    if re.match(r"https?://", src):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (seo_check)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read(5_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    return open(src, encoding="utf-8", errors="replace").read()

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"); ap.add_argument("--url", help="expected canonical URL"); ap.add_argument("--private", action="store_true", help="page must be noindex")
    ap.add_argument("--min-words", type=int, default=250)
    a = ap.parse_args()
    html = load(a.src); p = Page(); p.feed(html)
    out = {"FAIL": [], "WARN": [], "ok": []}
    def chk(cond, level, msg, good=None):
        out["ok" if cond else level].append((good or msg) if cond else msg)
    m = p.meta; robots = m.get("robots", "").lower()
    chk(bool(p.lang), "FAIL", "<html> has no lang attribute", "lang=%s" % p.lang)
    chk(p.charset or "content-type" in m, "FAIL", "no <meta charset>", "charset declared")
    chk("width=device-width" in m.get("viewport", ""), "FAIL", "no responsive viewport meta", "viewport ok")
    chk(bool(p.title), "FAIL", "missing <title>", "title (%d): %s" % (len(p.title), p.title))
    if a.private:
        chk("noindex" in robots, "FAIL", "private page must have <meta name=robots content=\"noindex,nofollow\"> (found: %r)" % robots, "noindex set")
    else:
        if p.title: chk(30 <= len(p.title) <= 60, "WARN", "title is %d chars (aim for 30-60)" % len(p.title), "title length ok")
        d = m.get("description", "")
        chk(bool(d), "FAIL", "missing meta description", "description (%d chars)" % len(d))
        if d: chk(70 <= len(d) <= 160, "WARN", "description is %d chars (aim for 70-160)" % len(d), "description length ok")
        chk("noindex" not in robots, "FAIL", "public page is marked noindex (%r)" % robots, "indexable")
        canon = [l.get("href") for l in p.links if (l.get("rel") or "").lower() == "canonical"]
        chk(len(canon) == 1, "FAIL", "need exactly one <link rel=canonical> (found %d)" % len(canon), "canonical: %s" % (canon[0] if canon else ""))
        if canon:
            chk(str(canon[0]).startswith("https://"), "WARN", "canonical should be an absolute https URL: %s" % canon[0], "canonical is absolute https")
            if a.url: chk(canon[0] == a.url, "FAIL", "canonical %s != expected %s" % (canon[0], a.url), "canonical matches --url")
        for k in ("og:title", "og:description", "og:url", "og:type", "og:image"):
            chk(bool(m.get(k)), "WARN", "missing %s" % k, "%s set" % k)
        if m.get("og:image"): chk(m["og:image"].startswith("https://"), "WARN", "og:image must be an absolute https URL", "og:image absolute")
        chk(bool(m.get("twitter:card")), "WARN", "missing twitter:card", "twitter:card set")
        types = []
        for raw in p.jsonld:
            try:
                def walk(x):
                    if isinstance(x, dict):
                        if "@type" in x: types.append(x["@type"] if isinstance(x["@type"], str) else ",".join(x["@type"]))
                        for v in x.values(): walk(v)
                    elif isinstance(x, list):
                        for v in x: walk(v)
                walk(json.loads(raw))
            except Exception as e: out["FAIL"].append("JSON-LD block does not parse: %s" % e)
        chk(bool(p.jsonld), "WARN", "no JSON-LD structured data", "JSON-LD types: %s" % ", ".join(sorted(set(types)))[:200])
        words = len(re.findall(r"\w{2,}", " ".join(p.text)))
        chk(words >= a.min_words, "WARN" if words >= a.min_words // 2 else "FAIL", "only %d words in the HTML without JavaScript (need %d+): ship static content" % (words, a.min_words), "%d words without JS" % words)
        chk(any("icon" in (l.get("rel") or "").lower() for l in p.links), "WARN", "no favicon link", "favicon set")
    h1 = p.h.get("h1", [])
    chk(len(h1) == 1, "FAIL" if not h1 else "WARN", "need exactly one <h1> (found %d)" % len(h1), "h1: %s" % (h1[0] if h1 else ""))
    noalt = [i.get("src", "")[:60] for i in p.imgs if i.get("alt") is None]
    chk(not noalt, "WARN", "%d <img> without alt: %s" % (len(noalt), noalt[:3]), "all images have alt")
    empty = [x[0] for x in p.anchors if x[0] and not x[1].strip() and not x[2]]
    chk(not empty, "WARN", "%d links with no text: %s" % (len(empty), empty[:3]), "links have text")
    for lvl in ("FAIL", "WARN", "ok"):
        for msg in out[lvl]:
            if msg: print("%-4s %s" % (lvl, msg))
    print("\n%d FAIL, %d WARN" % (len(out["FAIL"]), len([x for x in out["WARN"] if x])))
    sys.exit(1 if out["FAIL"] else 0)

if __name__ == "__main__": main()
