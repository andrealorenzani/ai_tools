---
name: seo-page
description: Make a web page search-engine and share friendly, and check it. MUST be used whenever a page that a browser will display is created, regenerated or published (HTML file, PHP page or template, generated report, landing page, any server-rendered or JS-rendered view), and when asked for SEO, meta tags, Open Graph, structured data, keywords, sitemap or robots.txt. Covers the public/private decision (private pages get noindex), the head and content checklist, JSON-LD, sitemap and robots, plus a linter and a sitemap merger.
---
# seo-page

Apply this before calling a displayed page finished. Then run the linter and fix every FAIL.

## 0. Decide first: public or private
- **Public** (meant to be found: site pages, tools, guides, landing pages) -> everything below.
- **Private** (personal analysis, internal report, admin, drafts, anything about a named person or with personal data, anything the user has not said is public) -> `<meta name="robots" content="noindex,nofollow">`, no sitemap entry, no canonical needed; still do title, lang, viewport. Lint with `--private`.
- Unsure -> treat as private and ask. Never make a private page indexable on your own.

## 1. Head (public page)
- `<html lang="..">`, `<meta charset="utf-8">` first, `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- `<title>`: 30-60 chars, main keyword first, brand last, unique per page.
- `<meta name="description">`: 70-160 chars, says what the visitor gets, contains the main phrase once, unique per page.
- `<link rel="canonical" href="https://absolute/url">` (one URL per content; no tracking params).
- Open Graph: `og:type`, `og:title`, `og:description`, `og:url`, `og:image` (absolute, 1200x630 PNG/JPG, under 1 MB), `og:image:alt`, `og:site_name`, `og:locale`. Twitter: `twitter:card=summary_large_image`, title, description, image.
- `<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">`. `theme-color`. A favicon (an inline SVG data URI is enough).
- `meta keywords` is ignored by Google and Bing: optional, max ~10 real phrases, never a substitute for visible text.
- JSON-LD (`<script type="application/ld+json">`), only types that match what is visibly on the page: `WebSite`/`WebPage` (+ `BreadcrumbList` on deep pages), `Article`, `Event` (name, startDate with timezone, location name + address, url), `ItemList`, `Dataset` (for a published data file), `FAQPage` (only if the questions are visible), `LocalBusiness`, `Product`. Validate that it parses.

## 2. Content
- Exactly one `<h1>` with the main phrase; `h2`/`h3` in order, each naming a real section with the words people search for.
- Keywords: pick 1 main phrase + 5-10 related ones from what people actually type (autocomplete, "people also ask", competitors' titles). Use them in title, h1, first paragraph, headings, link text, image alt. Write for a person: no stuffing, no lists of keywords.
- **The text must be in the HTML the server sends.** A page that builds its content with JavaScript (fetch + render) must ship a static version of the same content in the markup (intro, sections, the list of items with links), which the script then enhances or replaces. 250+ words without JS is the floor. Never hide text for crawlers only (`display:none`, same-colour text): content replaced or collapsed by the UI is fine, content nobody can ever see is not.
- Descriptive link text (not "click here"); external links `rel="noopener"`; every `<img>` has `alt`, `width`, `height`; `loading="lazy"` below the fold.
- Show a visible "updated" date; put it in JSON-LD `dateModified` and in the sitemap `lastmod`.
- An honest FAQ or "about this page" section is a cheap way to cover question-style searches.

## 3. Site level
- `sitemap.xml` at the site root lists every public canonical URL with `lastmod`. `robots.txt` has a `Sitemap: https://site/sitemap.xml` line and does not block the page or its CSS/JS.
- **Shared sites: merge, never replace.** Fetch the live `robots.txt` / `sitemap.xml` first; add your line or URL and keep everything else. Use `scripts/sitemap.py`.
- HTTPS, one host (www or not) with 301 from the other, real 404 status for missing pages, no redirect chains.
- Speed: no render-blocking extras, `preconnect` to the CDNs used, compress images, cache static files. Mobile layout must work (no horizontal scroll, tap targets 44px).
- After publishing: fetch the live URL and lint it; tell the user to submit the sitemap in Google Search Console and Bing Webmaster Tools (needs their account: you cannot do it).

## PHP / templated pages
- Title, description, canonical, og tags and JSON-LD come from per-page variables with site defaults in ONE head partial; escape with `htmlspecialchars`; JSON-LD via `json_encode(..., JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)`.
- Clean lowercase hyphenated URLs, one canonical per content, 301 for moved pages, `http_response_code(404)` on not found, `noindex` on search results, filters, login, admin and thin pages.
- Generate `sitemap.xml` from the route/content table (script or route), not by hand.
- Lint the rendered output, not the source: `seo_check.py http://localhost:8000/page`.

## Tools (stdlib Python, no network writes)
- `python3 ~/.claude/skills/seo-page/scripts/seo_check.py FILE_OR_URL [--url CANONICAL] [--private] [--min-words N]`: prints FAIL / WARN / ok lines, exit 1 on any FAIL. Checks lang, charset, viewport, title and description length, canonical, robots meta, h1 count, Open Graph and Twitter tags, JSON-LD validity and types, image alt, empty links, and how many words the page has without JavaScript.
- `python3 ~/.claude/skills/seo-page/scripts/sitemap.py --out sitemap.xml [--merge FILE_OR_URL] URL[=YYYY-MM-DD|=-]...`: writes a sitemap, keeping the entries of an existing one and updating/adding the given URLs. `--robots FILE --sitemap-url URL` appends the `Sitemap:` line to a local copy of robots.txt if it is missing (never touches other lines).

## Guardrails
- No deception: no hidden or stuffed keywords, no doorway pages, no fake reviews/ratings/dates, structured data only for content that is on the page. These get sites penalised.
- Never promise rankings; say what was done and what only time and links can do.
- Never overwrite a live `robots.txt` or `sitemap.xml` you did not generate from scratch for that site: merge and keep a copy of the previous version.
- Publishing or re-publishing is outward-facing: follow the project's deploy rules (ask unless the user already asked for the upload).
- Private stays private: noindex pages are not added to sitemaps, and are not made indexable without the user saying so.
