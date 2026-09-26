#!/usr/bin/env python3
"""Keep the derived parts of the site in sync with index.html's visible content.

Single sources of truth:
  * treatment names and prices  -> the tables in index.html
  * opening hours and NAP        -> OPENING_HOURS / BUSINESS below

From those the script owns (rewrites) these regions and files:
  * the JSON-LD BeautySalon block in index.html (offer catalogue, price range, hours)
  * the visible "Opening hours" line in the header and footer (<p class="hours">)
  * the Content-Security-Policy hashes for the inline <style> / JSON-LD in index.html and 404.html
  * llms.txt and llms-full.txt
  * sitemap.xml <lastmod>, stamped only when index.html actually changes

It also fails if the visible contact details in index.html disagree with BUSINESS.

Usage:  python3 tools/sync-metadata.py          # rewrite files
        python3 tools/sync-metadata.py --check  # exit 1 if anything is out of date (CI)
Standard library only.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://beautyonthelane-wirral.co.uk/"

BUSINESS = {
    "name": "Beauty on the Lane Wirral",
    "alternateName": "Beauty on the Lane",
    "telephone": "+441513430877",
    "telephone_display": "0151 343 0877",
    "whatsapp": "+447742014037",
    "whatsapp_display": "+44 7742 014037",
    "email": "beautyonthelanewirral@gmail.com",
    "street": "8 Allport Lane",
    "locality": "Bromborough",
    "region": "Merseyside",
    "postcode": "CH62 7HP",
    "lat": 53.3318795,
    "lng": -2.9781226,
    # Google Business Profile listing (CID from the Maps place id 0x…:0xcf504ec8424d31bd)
    "map": "https://maps.google.com/?cid=" + str(int("cf504ec8424d31bd", 16)),
    "facebook": "https://www.facebook.com/beautyonthelanewirral2025/",
    "instagram": "https://www.instagram.com/beautyonthelanewirral/",
}

WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Must match the Google Business Profile. The visible text is generated from this.
OPENING_HOURS = {
    "Tuesday": ("09:00", "17:00"),
    "Wednesday": ("09:00", "20:00"),
    "Thursday": ("09:00", "17:00"),
    "Friday": ("09:00", "17:00"),
    "Saturday": ("09:00", "16:00"),
}

AREAS_SERVED = ["Bromborough", "Bebington", "Port Sunlight", "Eastham", "Spital", "Wirral"]


# ---------------------------------------------------------------- helpers

def clean(fragment: str) -> str:
    """Strip tags and unescape entities."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def sha256_b64(text: str) -> str:
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode()


def join_names(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " & " + names[-1]


def clock(hhmm: str) -> str:
    """'09:00' -> '9am', '17:30' -> '5.30pm'."""
    h, m = (int(x) for x in hhmm.split(":"))
    suffix = "am" if h < 12 else "pm"
    h12 = h % 12 or 12
    return f"{h12}{suffix}" if m == 0 else f"{h12}.{m:02d}{suffix}"


def hours_text() -> str:
    """'Tuesday, Thursday & Friday 9am–5pm · Wednesday 9am–8pm · Saturday 9am–4pm · Closed Monday & Sunday'."""
    by_times: dict[tuple[str, str], list[str]] = {}
    for day in WEEK:
        if day in OPENING_HOURS:
            by_times.setdefault(OPENING_HOURS[day], []).append(day)
    parts = [f"{join_names(days)} {clock(o)}–{clock(c)}" for (o, c), days in by_times.items()]
    closed = [d for d in WEEK if d not in OPENING_HOURS]
    if closed:
        parts.append("Closed " + join_names(closed))
    return " · ".join(parts)


# ---------------------------------------------------------------- parsing

def parse_treatments(page: str) -> list[tuple[str, object]]:
    """Walk the treatments section in document order.

    Returns blocks: ("group", {id, name, rows}) for an <h3> followed by a price table,
    ("heading", text) for any other <h3>, ("para", text) and ("list", [items]) for prose.
    rows are (treatment, duration or None, price) tuples.
    """
    section = re.search(r'<section id="treatments">(.*?)</section>', page, re.S).group(1)
    blocks: list[tuple[str, object]] = []
    for chunk in re.split(r'(?=<h3 id=")', section)[1:]:
        head = re.match(r'<h3 id="([^"]+)">(.*?)</h3>', chunk, re.S)
        gid, title = head.group(1), clean(head.group(2))
        body = chunk[head.end():]
        table = re.search(r"<table[^>]*>.*?</table>", body, re.S)
        blocks.append(("group", {"id": gid, "name": title, "rows": parse_rows(table.group(0))}) if table else ("heading", title))
        for m in re.finditer(r"<p>(.*?)</p>|<ul>(.*?)</ul>", body, re.S):
            if m.group(1) is not None:
                blocks.append(("para", clean(m.group(1))))
            else:
                blocks.append(("list", [clean(li) for li in re.findall(r"<li>(.*?)</li>", m.group(2), re.S)]))

    # Structural guard: every table and every data row in the section must have been captured.
    groups = [b for kind, b in blocks if kind == "group"]
    n_tables = len(re.findall(r"<table[^>]*>", section))
    n_rows = len(re.findall(r"<tr[^>]*>\s*<td", section))
    parsed_rows = sum(len(g["rows"]) for g in groups)
    if n_tables != len(groups) or n_rows != parsed_rows:
        raise SystemExit(f"Treatments parse mismatch: {n_tables} tables/{n_rows} rows in HTML, "
                         f"{len(groups)} groups/{parsed_rows} rows parsed")
    return blocks


def parse_rows(table: str) -> list[tuple[str, str | None, str]]:
    rows = []
    for cells in re.findall(r"<tr[^>]*>((?:\s*<td[^>]*>.*?</td>)+)\s*</tr>", table, re.S):
        cols = [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", cells, re.S)]
        rows.append((cols[0], cols[1] if len(cols) == 3 else None, cols[-1]))
    return rows


def price_value(text: str) -> int:
    return int(re.search(r"£(\d+)", text).group(1))


# ---------------------------------------------------------------- generation

def build_json_ld(groups: list[dict], description: str) -> dict:
    prices = [price_value(p) for g in groups for _, _, p in g["rows"]]
    catalog = [{
        "@type": "OfferCatalog",
        "name": g["name"],
        "url": SITE + "#" + g["id"],
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": name},
             "price": str(price_value(price)), "priceCurrency": "GBP"}
            for name, _, price in g["rows"]
        ],
    } for g in groups]

    b = BUSINESS
    return {
        "@context": "https://schema.org",
        "@type": "BeautySalon",
        "@id": SITE + "#salon",
        "name": b["name"],
        "alternateName": b["alternateName"],
        "url": SITE,
        "logo": SITE + "images/icon-512.png",
        "image": [SITE + "images/share.png", SITE + "images/logo.svg"],
        "description": description,
        "telephone": b["telephone"],
        "email": b["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": b["street"],
            "addressLocality": b["locality"],
            "addressRegion": b["region"],
            "postalCode": b["postcode"],
            "addressCountry": "GB",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": b["lat"], "longitude": b["lng"]},
        "hasMap": b["map"],
        "areaServed": [{"@type": "Place", "name": a} for a in AREAS_SERVED],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "https://schema.org/" + day,
             "opens": opens, "closes": closes}
            for day in WEEK if day in OPENING_HOURS for opens, closes in [OPENING_HOURS[day]]
        ],
        "priceRange": f"£{min(prices)}-£{max(prices)}",
        "currenciesAccepted": "GBP",
        "sameAs": [b["facebook"], b["instagram"]],
        "contactPoint": [
            {"@type": "ContactPoint", "contactType": "customer service", "telephone": b["telephone"],
             "areaServed": "GB", "availableLanguage": "en"},
            {"@type": "ContactPoint", "contactType": "customer service", "name": "WhatsApp",
             "telephone": b["whatsapp"], "url": "https://wa.me/" + b["whatsapp"].lstrip("+"),
             "areaServed": "GB", "availableLanguage": "en"},
        ],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Treatments & Prices", "itemListElement": catalog},
    }


def set_csp_hash(page: str, directive: str, content: str) -> str:
    """Replace the whole source list of one CSP directive with the hash of `content`."""
    m = re.search(r'http-equiv="Content-Security-Policy" content="([^"]*)"', page)
    if not m:
        raise SystemExit("No Content-Security-Policy meta tag found")
    directives = [d.strip() for d in m.group(1).split(";") if d.strip()]
    names = [d.split()[0] for d in directives]
    if directive not in names:
        raise SystemExit(f"CSP has no {directive} directive")
    directives[names.index(directive)] = f"{directive} 'sha256-{sha256_b64(content)}'"
    return page[:m.start(1)] + "; ".join(directives) + page[m.end(1):]


def hash_style(page: str) -> str:
    return set_csp_hash(page, "style-src", re.search(r"<style>(.*?)</style>", page, re.S).group(1))


def render_index(page: str, json_ld: dict) -> str:
    ld_text = "\n" + json.dumps(json_ld, ensure_ascii=False, separators=(",", ":")) + "\n    "
    page = re.sub(r'(<script type="application/ld\+json">).*?(</script>)',
                  lambda m: m.group(1) + ld_text + m.group(2), page, count=1, flags=re.S)
    page, n = re.subn(r'(<p class="hours">).*?(</p>)',
                      lambda m: m.group(1) + "Opening hours: " + html.escape(hours_text(), quote=False) + m.group(2),
                      page, flags=re.S)
    if n == 0:
        raise SystemExit('No <p class="hours"> element to write the opening hours into')
    page = set_csp_hash(page, "script-src", ld_text)
    return hash_style(page)


def check_contact_details(page: str) -> None:
    """The visible contact details are hand-written; make sure they match BUSINESS."""
    b = BUSINESS
    expected = {
        "tel: link": f'href="tel:0{b["telephone"][3:]}"',
        "mailto: link": f'href="mailto:{b["email"]}"',
        "WhatsApp link": "wa.me/" + b["whatsapp"].lstrip("+"),
        "postcode": b["postcode"],
        "street": b["street"],
        "og phone": f'content="{b["telephone"]}"',
    }
    missing = [what for what, needle in expected.items() if needle not in page]
    for key in ("telephone", "whatsapp"):
        national = lambda s: re.sub(r"\D", "", s).removeprefix("44").lstrip("0")
        if national(b[key + "_display"]) != national(b[key]):
            missing.append(f"{key}_display digits")
    if missing:
        raise SystemExit("index.html disagrees with BUSINESS: " + ", ".join(missing))


def render_llms(page: str, blocks: list, description: str) -> tuple[str, str]:
    b = BUSINESS
    about = [clean(p) for p in re.findall(r"<p>(.*?)</p>", re.search(r'<section id="about">(.*?)</section>', page, re.S).group(1), re.S)]
    contact = f"Phone: {b['telephone_display']} · WhatsApp: {b['whatsapp_display']} · Email: {b['email']}"
    address = f"{b['street']}, {b['locality']}, Wirral, {b['postcode']}, UK"

    full = [f"# {b['alternateName']}", "", f"> {description}", "", f"Address: {address}", contact,
            f"Opening hours: {hours_text()}", f"Facebook: {b['facebook']}", f"Instagram: {b['instagram']}", "",
            "## About Us", ""]
    full += [p + "\n" for p in about]
    full += ["## Treatments & Prices", ""]
    for kind, block in blocks:
        if kind == "group":
            with_duration = any(d for _, d, _ in block["rows"])
            full += [f"### {block['name']}", "",
                     "| Treatment | Duration | Price |" if with_duration else "| Treatment | Price |",
                     "|---|---|---|" if with_duration else "|---|---|"]
            full += [f"| {n} | {d} | {p} |" if with_duration else f"| {n} | {p} |" for n, d, p in block["rows"]]
            full.append("")
        elif kind == "heading":
            full += [f"### {block}", ""]
        elif kind == "para":
            full += [block, ""]
        else:
            full += ["- " + item for item in block] + [""]
    full += ["## Contact Us", "",
             f"Use the contact form at {SITE}#contact, or get in touch directly by email, phone, or WhatsApp (details above).", "",
             "## Privacy", "",
             "This site does not use cookies, analytics, or third-party tracking. The contact form sends an email "
             "directly via your own email client — it is not submitted to or stored on any server.", ""]

    categories = ", ".join(block["name"].lower() for kind, block in blocks if kind == "group")
    short = f"""# {b['alternateName']}

> {description}

{b['alternateName']} is a single-page brochure website for the salon at {address}. Opening hours: {hours_text()}. {contact}.

## Pages

- [Home]({SITE}): About the salon, full treatment & price list ({categories}), and a contact form.

## Notes

- This site does not use cookies, analytics, or third-party tracking.
- Full page content is also available at [/llms-full.txt]({SITE}llms-full.txt).
- Structured data (schema.org BeautySalon) is embedded as JSON-LD on the homepage.
"""
    return "\n".join(full), short


# ---------------------------------------------------------------- main

def main(check: bool) -> int:
    index_path, notfound_path = ROOT / "index.html", ROOT / "404.html"
    page = index_path.read_text(encoding="utf-8")
    check_contact_details(page)
    blocks = parse_treatments(page)
    groups = [b for kind, b in blocks if kind == "group"]
    description = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', page).group(1))

    new_index = render_index(page, build_json_ld(groups, description))
    full, short = render_llms(new_index, blocks, description)
    outputs = {
        index_path: new_index,
        notfound_path: hash_style(notfound_path.read_text(encoding="utf-8")),
        ROOT / "llms-full.txt": full,
        ROOT / "llms.txt": short,
    }
    stale = [p for p, text in outputs.items() if p.read_text(encoding="utf-8") != text]

    if check:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        print("all generated content is up to date" if not stale else "run: python3 tools/sync-metadata.py")
        return 1 if stale else 0

    for p in stale:
        p.write_text(outputs[p], encoding="utf-8")
    if index_path in stale:
        sitemap = ROOT / "sitemap.xml"
        sitemap.write_text(re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{dt.date.today().isoformat()}</lastmod>",
                                  sitemap.read_text(encoding="utf-8")), encoding="utf-8")
    offers = sum(len(g["rows"]) for g in groups)
    print(f"{len(groups)} treatment groups / {offers} offers; "
          + (f"updated {', '.join(p.name for p in stale)}" if stale else "nothing to update"))
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
