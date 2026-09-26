#!/usr/bin/env python3
"""Keep index.html's derived data in sync with its visible price list.

Reads the treatment tables and opening hours from index.html and then:
  * rebuilds the JSON-LD BeautySalon block (offer catalogue, price range, hours)
  * recomputes the Content-Security-Policy hashes for the inline <style> and JSON-LD
  * regenerates llms.txt and llms-full.txt
  * stamps today's date into sitemap.xml <lastmod>

Run it after every content change:  python3 tools/sync-metadata.py
Standard library only; no dependencies to install.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SITE = "https://beautyonthelane-wirral.co.uk/"

BUSINESS = {
    "name": "Beauty on the Lane Wirral",
    "alternateName": "Beauty on the Lane",
    "telephone": "+441513430877",
    "whatsapp": "+447742014037",
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

# Must match the Google Business Profile and the visible text in index.html.
OPENING_HOURS = [
    ("Tuesday", "09:00", "17:00"),
    ("Wednesday", "09:00", "20:00"),
    ("Thursday", "09:00", "17:00"),
    ("Friday", "09:00", "17:00"),
    ("Saturday", "09:00", "16:00"),
]
HOURS_TEXT = "Tuesday, Thursday & Friday 9am–5pm · Wednesday 9am–8pm · Saturday 9am–4pm · Closed Sunday & Monday"

AREAS_SERVED = ["Bromborough", "Bebington", "Port Sunlight", "Eastham", "Spital", "Wirral"]

# <h3> ids inside the treatments section that intentionally have no price table.
HEADINGS_WITHOUT_TABLE = {"cancellation-policy"}


def clean(fragment: str) -> str:
    """Strip tags and unescape entities from a table cell."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def parse_treatments(page: str) -> list[dict]:
    """Return [{'id', 'name', 'rows': [(treatment, duration|None, price)]}] per <h3> that has a table."""
    section = re.search(r'<section id="treatments">(.*?)</section>', page, re.S).group(1)
    groups = []
    for m in re.finditer(r'<h3 id="([^"]+)">(.*?)</h3>\s*(?:<p>.*?</p>\s*)*(<table>.*?</table>)?', section, re.S):
        gid, title, table = m.group(1), clean(m.group(2)), m.group(3)
        if not table:
            if gid in HEADINGS_WITHOUT_TABLE:
                continue
            raise SystemExit(f"No price table found under <h3 id=\"{gid}\">; add it to HEADINGS_WITHOUT_TABLE if that is intended")
        rows = []
        for cells in re.findall(r"<tr>((?:<td>.*?</td>)+)</tr>", table, re.S):
            cols = [clean(c) for c in re.findall(r"<td>(.*?)</td>", cells, re.S)]
            duration = cols[1] if len(cols) == 3 else None
            rows.append((cols[0], duration, cols[-1]))
        groups.append({"id": gid, "name": title, "rows": rows})
    return groups


def price_value(text: str) -> int:
    return int(re.search(r"£(\d+)", text).group(1))


def build_json_ld(groups: list[dict], description: str) -> dict:
    prices = [price_value(p) for g in groups for _, _, p in g["rows"]]
    catalog = []
    for g in groups:
        offers = []
        for name, duration, price in g["rows"]:
            service = {"@type": "Service", "name": name, "provider": {"@id": SITE + "#salon"}}
            if duration:
                service["description"] = f"{name} ({duration})"
            offers.append({
                "@type": "Offer",
                "itemOffered": service,
                "price": str(price_value(price)),
                "priceCurrency": "GBP",
                "url": SITE + "#" + g["id"],
            })
        catalog.append({"@type": "OfferCatalog", "name": g["name"], "itemListElement": offers})

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
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "https://schema.org/" + day, "opens": opens, "closes": closes}
            for day, opens, closes in OPENING_HOURS
        ],
        "priceRange": f"£{min(prices)}-£{max(prices)}",
        "currenciesAccepted": "GBP",
        "sameAs": [b["facebook"], b["instagram"]],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "telephone": b["telephone"],
                "areaServed": "GB",
                "availableLanguage": "en",
            },
            {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "name": "WhatsApp",
                "telephone": b["whatsapp"],
                "url": "https://wa.me/" + b["whatsapp"].lstrip("+"),
                "areaServed": "GB",
                "availableLanguage": "en",
            },
        ],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Treatments & Prices", "itemListElement": catalog},
    }


def sha256_b64(text: str) -> str:
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode()


def update_index(page: str, json_ld: dict) -> str:
    ld_text = "\n" + json.dumps(json_ld, indent=4, ensure_ascii=False) + "\n    "
    page = re.sub(
        r'(<script type="application/ld\+json">).*?(</script>)',
        lambda m: m.group(1) + ld_text + m.group(2),
        page, count=1, flags=re.S,
    )
    style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    for directive, content in (("script-src", ld_text), ("style-src", style)):
        page, n = re.subn(rf"{directive} 'sha256-[^']*'", f"{directive} 'sha256-{sha256_b64(content)}'", page, count=1)
        if n != 1:
            raise SystemExit(f"Could not update the {directive} hash: CSP meta tag no longer matches the expected shape")
    return page


def paragraphs(page: str, section_id: str) -> list[str]:
    section = re.search(rf'<section id="{section_id}">(.*?)</section>', page, re.S).group(1)
    return [clean(p) for p in re.findall(r"<p>(.*?)</p>", section, re.S)]


def write_llms(page: str, groups: list[dict]) -> None:
    b = BUSINESS
    about = paragraphs(page, "about")
    contact_line = (
        f"Phone: 0151 343 0877 · WhatsApp: +44 7742 014037 · Email: {b['email']}\n"
        f"Opening hours: {HOURS_TEXT}\n"
        f"Facebook: {b['facebook']}\nInstagram: {b['instagram']}"
    )
    summary = (
        f"Independent beauty salon at {b['street']}, {b['locality']}, Wirral, {b['postcode']}, UK. "
        "Offers Dermalogica and Elemis facials, dermaplaning, massage, manicures, pedicures, "
        "Gel Bottle and builder gel nails, Vita Liberata spray tanning, eyebrow and eyelash treatments, and waxing."
    )

    full = [f"# {b['alternateName']}", "", f"> {summary}", "", contact_line, "", "## About Us", ""]
    full += [p + "\n" for p in about]
    full += ["## Treatments & Prices", ""]
    for g in groups:
        full.append(f"### {g['name']}")
        full.append("")
        has_duration = any(d for _, d, _ in g["rows"])
        full.append("| Treatment | Duration | Price |" if has_duration else "| Treatment | Price |")
        full.append("|---|---|---|" if has_duration else "|---|---|")
        for name, duration, price in g["rows"]:
            full.append(f"| {name} | {duration} | {price} |" if has_duration else f"| {name} | {price} |")
        full.append("")
    upgrades = re.search(r"<p><em>(.*?)</em></p>\s*<ul>(.*?)</ul>", page, re.S)
    if upgrades:
        full.append(clean(upgrades.group(1)))
        full += ["- " + clean(li) for li in re.findall(r"<li>(.*?)</li>", upgrades.group(2), re.S)]
        full.append("")
    cancellation = re.search(r'<h3 id="cancellation-policy">(.*?)</h3>\s*<p>(.*?)</p>', page, re.S)
    if cancellation:
        full += [f"### {clean(cancellation.group(1))}", "", clean(cancellation.group(2)), ""]
    full += [
        "## Contact Us", "",
        f"Use the contact form at {SITE}#contact, or get in touch directly by email, phone, or WhatsApp (details above).", "",
        "## Privacy", "",
        "This site does not use cookies, analytics, or third-party tracking. The contact form sends an email directly via your own email client — it is not submitted to or stored on any server.", "",
    ]
    (ROOT / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")

    categories = ", ".join(g["name"].lower() for g in groups)
    short = f"""# {b['alternateName']}

> {summary}

{b['alternateName']} is a single-page brochure website. Opening hours: {HOURS_TEXT}. Phone: 0151 343 0877. WhatsApp: +44 7742 014037. Email: {b['email']}.

## Pages

- [Home]({SITE}): About the salon, full treatment & price list ({categories}), and a contact form.

## Notes

- This site does not use cookies, analytics, or third-party tracking.
- Full page content is also available at [/llms-full.txt]({SITE}llms-full.txt).
- Structured data (schema.org BeautySalon) is embedded as JSON-LD on the homepage.
"""
    (ROOT / "llms.txt").write_text(short, encoding="utf-8")


def stamp_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    today = dt.date.today().isoformat()
    path.write_text(re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{today}</lastmod>", path.read_text()), encoding="utf-8")


def main() -> None:
    page = INDEX.read_text(encoding="utf-8")
    groups = parse_treatments(page)
    description = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', page).group(1))
    page = update_index(page, build_json_ld(groups, description))
    INDEX.write_text(page, encoding="utf-8")
    write_llms(page, groups)
    stamp_sitemap()
    total = sum(len(g["rows"]) for g in groups)
    print(f"synced {len(groups)} treatment groups / {total} offers; CSP hashes, llms files and sitemap updated")


if __name__ == "__main__":
    main()
