#!/usr/bin/env python3
"""sitemap.py --out sitemap.xml [--merge FILE_OR_URL] URL[=YYYY-MM-DD|=-]...
        [--robots LOCAL_ROBOTS_TXT --sitemap-url https://site/sitemap.xml]
Write a sitemap. With --merge, keep every entry of an existing sitemap (local file or live URL; a 404 counts as empty) and
update/add the given URLs: use it on shared sites so other pages are never dropped. lastmod defaults to today;
`URL=-` writes no lastmod (a page you did not change) and keeps the lastmod of an entry that already exists.
--robots appends a `Sitemap:` line to a LOCAL copy of robots.txt when missing; no other line is changed. Never uploads anything.
"""
import sys, re, argparse, datetime, urllib.request, urllib.error
from xml.sax.saxutils import escape, unescape

def read(src):
    try:
        if re.match(r"https?://", src):
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (sitemap.py)"})
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        return open(src, encoding="utf-8").read()
    except (urllib.error.HTTPError, FileNotFoundError) as e:
        if isinstance(e, FileNotFoundError) or e.code == 404: return ""
        raise

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*"); ap.add_argument("--out"); ap.add_argument("--merge")
    ap.add_argument("--robots"); ap.add_argument("--sitemap-url")
    a = ap.parse_args()
    today = datetime.date.today().isoformat()
    if a.out:
        entries = {}
        if a.merge:
            old = read(a.merge)
            if old and "<urlset" not in old: sys.exit("error: %s is not a <urlset> sitemap (an index or HTML?); not touching it" % a.merge)
            for block in re.findall(r"<url>(.*?)</url>", old, re.S):
                loc = re.search(r"<loc>\s*(.*?)\s*</loc>", block, re.S); lm = re.search(r"<lastmod>\s*(.*?)\s*</lastmod>", block, re.S)
                if loc: entries[unescape(loc.group(1))] = lm.group(1) if lm else ""
        for u in a.urls:
            url, _, lm = u.partition("=")
            if not re.match(r"https?://\S+$", url): sys.exit("error: not an absolute URL: %s" % url)
            if lm == "-": entries.setdefault(url, ""); continue
            if lm and not re.fullmatch(r"\d{4}-\d\d-\d\d", lm): sys.exit("error: bad lastmod %s" % lm)
            entries[url] = lm or today
        if not entries: sys.exit("error: no URLs")
        body = "".join("  <url><loc>%s</loc>%s</url>\n" % (escape(u), "<lastmod>%s</lastmod>" % lm if lm else "") for u, lm in sorted(entries.items()))
        open(a.out, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % body)
        print("wrote %s (%d urls)" % (a.out, len(entries)))
    if a.robots:
        if not a.sitemap_url: sys.exit("error: --robots needs --sitemap-url")
        txt = read(a.robots)
        if re.search(r"(?im)^\s*sitemap:\s*%s\s*$" % re.escape(a.sitemap_url), txt): print("robots: Sitemap line already present")
        else:
            open(a.robots, "w", encoding="utf-8").write((txt.rstrip("\n") + "\n\n" if txt.strip() else "User-agent: *\nAllow: /\n\n") + "Sitemap: %s\n" % a.sitemap_url)
            print("robots: appended Sitemap line to %s" % a.robots)

if __name__ == "__main__": main()
