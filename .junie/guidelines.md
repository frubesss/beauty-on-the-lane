Project guidelines for Beauty on the Lane

Audience: advanced developers maintaining a simple, static website served via GitHub Pages with a custom domain.

1. Build and configuration
- Stack: Pure static site (index.html + images). No bundler, no framework, no runtime dependencies.
- Hosting: GitHub Pages with a custom domain (CNAME present). The canonical domain is https://beautyonthelane-wirral.co.uk/.
- Canonical/SEO configuration:
  - <link rel="canonical" href="https://beautyonthelane-wirral.co.uk/"> must match the live domain.
  - Open Graph and Twitter cards point to images/logo.svg. Ensure the image exists and remains a reasonable social share dimension (SVG is fine for branding; consider adding a PNG fallback if platforms misbehave).
  - JSON-LD schema.org block describes a BeautySalon. If you change contact details, opening hours, or social profiles, update BOTH the visible content and the JSON-LD to keep them consistent.
- Domain/Pages configuration:
  - CNAME file contains beautyonthelane-wirral.co.uk. Do not remove or alter unless the domain changes.
  - Ensure the repository’s Pages settings are configured for the correct branch (commonly main) and root directory.
- Local development:
  - You can open index.html directly in the browser. For parity and to avoid CORS or relative path quirks, prefer a static HTTP server:
    - Python 3: python3 -m http.server 8080 (serve from the repo root) then open http://localhost:8080/
- Assets:
  - images/ contains SVG assets for logo and favicon. Keep file names and relative paths stable; index.html references them as images/logo.svg and images/favicon.svg.
  - When adding raster images, optimize them (TinyPNG, Squoosh) and prefer modern formats (WebP/AVIF) with fallbacks if needed.

2. Additional development information
- SEO/metadata discipline:
  - Maintain consistency between visible content and metadata (title, meta description, Open Graph, Twitter, JSON-LD fields such as telephone, openingHours, sameAs).
  - If you change the business phone number, update it in: visible header, tel: link, WhatsApp link, and JSON-LD contactPoint.
  - Keep the priceRange and openingHours current; search engines may reflect these in rich results.
- Accessibility:
  - All meaningful images must have alt text. The logo already includes alt; preserve or refine.
  - External links using target="_blank" should include rel="noopener noreferrer" (already present).
  - Use clear link text; avoid "click here".
- Performance:
  - Prefer SVG for icons and logos. Compress raster images and specify width/height when embedding to reduce layout shifts.
  - Avoid adding blocking third-party scripts; the page is intentionally lean.
- Styling:
  - Styles are embedded in a <style> block within index.html. If extracting to a CSS file, update references and consider cache-busting.
  - Keep the established grayscale palette unless brand guidelines change.
- Content structure:
  - Sections include About, Treatments & Prices (with tables), and Contact. When adding new treatments, follow the existing table semantics.

3. House rules
- Keep the repo free of compiled assets and node_modules. The site is static by design.
