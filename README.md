# Beauty on the Lane – Static Site

A minimal, fast, and dependency‑free static website for Beauty on the Lane (Bromborough, Wirral). The site is hosted on GitHub Pages with a custom domain and consists of a single HTML entry point plus SVG assets.

Live site: https://beautyonthelane-wirral.co.uk/

## Overview
- Stack: Pure static HTML/CSS. No frameworks, no bundlers, no package manager.
- Entry point: `index.html`
- Assets: SVG logo and favicon in `images/`. Optional PNGs in repo root for docs/marketing.
- Hosting: GitHub Pages with custom domain via `CNAME`.
- SEO: Canonical URL, Open Graph/Twitter tags, and a JSON‑LD `BeautySalon` schema block are embedded in `index.html`.

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
├─ images/
│  ├─ favicon.svg        # Favicon referenced by index.html
│  └─ logo.svg           # Logo referenced by index.html and social tags
├─ cover.png             # Optional cover image for docs/README (not used by the site)
└─ logo.png              # Optional raster logo for docs/README (not used by the site)
```


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
  - Currently reference `images/logo.svg`.
  - SVG is acceptable for branding; if some platforms misbehave, add a PNG fallback and update tags accordingly.
- JSON‑LD (`application/ld+json`)
  - Type: `BeautySalon` with address, telephone, opening hours, social profiles (`sameAs`), and contact points.
  - If you change phone numbers, opening hours, or social profiles, update all places:
    - Visible header content (address, `tel:` link, WhatsApp link).
    - JSON‑LD fields: `telephone`, `openingHours`, `contactPoint`, `sameAs`.
    - Meta tags (if applicable) and any deep links.
- Accessibility
  - Maintain descriptive `alt` text for meaningful images. The logo alt text is present; refine if needed.
- Performance
  - Prefer SVG for icons/logos. If adding raster images, optimize (TinyPNG/Squoosh) and specify width/height to reduce layout shifts.

## Acknowledgements
- Hosted by GitHub Pages.
- Built as a deliberately lightweight static site to minimize maintenance overhead.
