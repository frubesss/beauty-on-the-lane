# SEO Action Plan — Ranking #1 for "Beauty Salons on the Wirral"

The website code is fully optimized (see the on-page work summarised at the
bottom). Search position for a local query like this is now decided by the
steps below — most happen **outside this repository** and need the business
owner to action them.

## 1. Deploy the changes

Merge the `claude/sleepy-babbage-1ezvju` branch into `main`. GitHub Pages
serves the live site from `main`, so nothing takes effect until it's merged.

## 2. Google Business Profile (the #1 lever)

For searches like "beauty salons on the Wirral", Google shows the **local
map pack above all normal results**. Winning that spot matters more than
anything else. At https://business.google.com:

- Claim/verify the profile for **Beauty on the Lane, 8 Allport Lane,
  Bromborough, CH62 7HP**.
- Primary category: **Beauty salon**. Secondary: Facial spa, Nail salon,
  Waxing hair removal service, Massage spa.
- Website: `https://beautyonthelane-wirral.co.uk/`
- Phone: `0151 343 0877` (exactly this format everywhere — see NAP below).
- Opening hours: Mon–Fri 09:00–18:00.
- Add 10+ real photos (salon interior, treatments in progress, results).
- Ready-to-paste business description:

> Beauty on the Lane is a beauty salon on Allport Lane in the heart of
> Bromborough village, Wirral. We offer Dermalogica and Elemis facials,
> dermaplaning, massage, manicures and pedicures, gel and builder gel
> nails, Vita Liberata spray tans, lash and brow treatments and waxing for
> both ladies and gentlemen. Our fully qualified therapists tailor every
> treatment to you. We welcome clients from across the Wirral, including
> Bebington, Eastham, New Ferry, Port Sunlight, Heswall and beyond.

- Post a Google update (offer/news) at least monthly — active profiles
  rank higher.

## 3. Reviews

Review quantity, rating and recency are the strongest local-pack signals
after proximity:

- Ask every happy client for a Google review. Get the short review link
  from the Business Profile dashboard and send it by WhatsApp after
  appointments.
- Aim for a steady trickle (2–4/month) rather than a one-off burst.
- Reply to every review — replies are a ranking and trust signal.

## 4. Citations & directories (also fixes the zero-backlink problem)

The domain currently has **Domain Rating 0** (no backlinks). List the salon
on these, using *identical* name/address/phone (NAP) everywhere:

```
Beauty on the Lane
8 Allport Lane, Bromborough, Wirral, CH62 7HP
0151 343 0877
https://beautyonthelane-wirral.co.uk/
```

Priority list:
- Treatwell — https://www.treatwell.co.uk (ranks #1–3 for the target search itself)
- Fresha — https://www.fresha.com
- Booksy — https://booksy.com
- Yell — https://www.yell.com
- Bing Places — https://www.bingplaces.com
- Apple Maps (Apple Business Connect) — https://businessconnect.apple.com
- Facebook page: ensure address/phone/website exactly match the NAP above
- FreeIndex, Scoot, Thomson Local (quick free citations)

## 5. Google Search Console

- Verify the site at https://search.google.com/search-console (DNS record
  or HTML-file method — the file can be committed to this repo).
- Submit `https://beautyonthelane-wirral.co.uk/sitemap.xml`.
- Request indexing of the homepage after the merge so Google picks up the
  new content quickly.

## 6. Local links (ongoing)

A few genuinely local backlinks will outweigh dozens of generic ones:
- Wirral Globe business features / local press
- Bromborough & Bebington community Facebook groups and village websites
- Supplier locator pages: Dermalogica, Elemis and Vita Liberata all have
  "find a salon/stockist" listings that link to salon websites
- Sponsor or support a local event/school fair and ask for a link

## 7. Monitor

- Track "beauty salon wirral", "beauty salon bromborough", "beauty salons
  on the wirral" in Search Console's Performance report.
- Expect movement 2–6 weeks after merge + Business Profile work; the local
  pack typically responds faster than organic results.

---

### On-page work already completed in this repo

- Title/meta/OG/Twitter retargeted at "Beauty Salon in Bromborough, Wirral"
- Visible keyword-rich H1 and in-page navigation
- BeautySalon schema with geo coordinates, areaServed (Wirral towns),
  structured opening hours and a full service catalogue
- FAQPage schema with matching visible FAQ content
- "Your Local Beauty Salon on the Wirral" section naming surrounding areas
- Geo meta tags, updated sitemap, optimized 156KB share image (was 2.6MB)
