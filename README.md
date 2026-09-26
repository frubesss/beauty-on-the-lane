# Beauty on the Lane – Static Site

A minimal, fast, and dependency‑free static website for Beauty on the Lane (Bromborough, Wirral). The site is hosted on GitHub Pages with a custom domain and consists of a single HTML entry point plus SVG assets.

Live site: https://beautyonthelane-wirral.co.uk/

## Overview
- Stack: Pure static HTML/CSS. No frameworks, no bundlers, no package manager.
- Entry point: `index.html`
- Assets: SVG logo and favicon plus PNG share image and app icons in `images/`.
- Hosting: GitHub Pages with custom domain via `CNAME`.
- SEO: Canonical URL, Open Graph/Twitter tags, and a JSON‑LD `BeautySalon` schema block are embedded in `index.html`. The schema, CSP hashes, `llms*.txt` and sitemap date are regenerated from the price tables by `tools/sync-metadata.py`.

This repository intentionally avoids any runtime dependencies or build steps to keep the site simple, lean, and easy to maintain.

## Requirements
- Any modern web browser to view the site.
- GitHub account with access to the repository to deploy changes via Pages.

No Node, bundler, or package manager is required.

## Environment Variables
None. The site is fully static and does not rely on any environment variables.

## Project Structure
```
/ (repo root)
├─ CNAME                 # Custom domain for GitHub Pages (beautyonthelane-wirral.co.uk)
├─ index.html            # Single-page site (HTML, embedded CSS, metadata, JSON-LD)
├─ 404.html              # Custom error page (served automatically by GitHub Pages)
├─ site.webmanifest      # Web app manifest (PWA metadata, icon)
├─ robots.txt            # Crawler rules + Content-Signal line
├─ sitemap.xml           # XML sitemap
├─ llms.txt              # Curated index for AI agents/LLMs
├─ llms-full.txt         # Full page content in markdown, for AI agents/LLMs
├─ .well-known/
│  └─ security.txt       # Vulnerability disclosure contact (RFC 9116)
├─ tools/
│  └─ sync-metadata.py   # Regenerates JSON-LD, CSP hashes, llms*.txt and sitemap lastmod from index.html
├─ images/
│  ├─ favicon.svg        # Favicon referenced by index.html, site.webmanifest, and 404.html
│  ├─ logo.svg           # Logo shown in the page header
│  ├─ share.png          # 1200x630 Open Graph / Twitter share image
│  ├─ apple-touch-icon.png # 180x180 iOS home-screen icon
│  └─ icon-512.png       # 512x512 manifest icon and schema logo
└─ logo.png              # Optional raster logo for docs/README (not used by the site)
```

### Content Security Policy
`index.html` and `404.html` each ship a `Content-Security-Policy` meta tag that allowlists the page's inline `<style>` (and, on `index.html`, the inline JSON-LD `<script>`) by SHA-256 hash rather than `'unsafe-inline'`. **If you edit the contents of a `<style>` or `<script type="application/ld+json">` block, you must recompute its hash and update the matching `sha256-...` value in that page's CSP meta tag**, or the browser will silently refuse to apply the styles/data.

For `index.html` this is automated. After any content change run:
```
python3 tools/sync-metadata.py
```
It rebuilds the JSON-LD offer catalogue and price range from the treatment tables, recomputes both CSP hashes, regenerates `llms.txt` and `llms-full.txt`, and stamps today's date into `sitemap.xml`. Opening hours and business details live at the top of that script; keep them identical to the visible header/footer text and the Google Business Profile.

For `404.html` compute the style hash by hand:
```
python3 -c "
import hashlib, base64, re
html = open('404.html').read()
style = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
print(base64.b64encode(hashlib.sha256(style.encode()).digest()).decode())
"
```
Some security headers (HSTS, X-Content-Type-Options, X-Frame-Options/frame-ancestors, Permissions-Policy, COOP/COEP) cannot be set via `<meta>` and require an HTTP response header — not possible on plain GitHub Pages without a proxy such as Cloudflare in front of the domain.


## Deployment (GitHub Pages)
1. Branch and directory
   - Pages should serve from the default branch (commonly `main`) and the root directory.
2. Custom domain
   - The `CNAME` file contains `beautyonthelane-wirral.co.uk` (do not remove or alter unless the domain changes).
   - Ensure the repository’s Pages settings list the same custom domain.
   - Configure DNS to point the domain to GitHub Pages per the official documentation.
3. After pushing changes to the configured branch, GitHub Pages will rebuild and publish automatically.


## Metadata & SEO Discipline
The project follows a strict metadata discipline to keep visible content and structured data in sync. When you update business details, update BOTH the visible content and JSON‑LD in `index.html`.

Key items to keep consistent:
- Canonical URL
  - `<link rel="canonical" href="https://beautyonthelane-wirral.co.uk/">` must match the live domain.
- Open Graph & Twitter cards
  - Reference `images/share.png` (1200x630 PNG). Social platforms do not render SVG share images, so keep this a PNG or JPEG and update `og:image:width`/`height` if its size changes.
- JSON‑LD (`application/ld+json`)
  - Type: `BeautySalon` with address, telephone, opening hours, social profiles (`sameAs`), and contact points.
  - If you change phone numbers, opening hours, or social profiles, update all places:
    - Visible header and footer content (address, hours line, `tel:` link, WhatsApp link).
    - The `BUSINESS`, `OPENING_HOURS` and `HOURS_TEXT` values in `tools/sync-metadata.py`, then re-run it.
    - The Google Business Profile, which is the reference for hours and NAP consistency.
- Accessibility
  - Maintain descriptive `alt` text for meaningful images. The logo alt text is present; refine if needed.
- Performance
  - Prefer SVG for icons/logos. If adding raster images, optimize (TinyPNG/Squoosh) and specify width/height to reduce layout shifts.

## Acknowledgements
- Hosted by GitHub Pages.
- Built as a deliberately lightweight static site to minimize maintenance overhead.
