# QA Report — v21 design completion

## Purpose

This pass resolves four visual/content gaps identified after the v20 mobile-map restoration: the Contact-page Availability block, missing Tech Stack entries, the incomplete Practice table treatment, and inaccurate Europe / Asia label placement.

## Rectifications

### Availability
- Rebuilt Availability as a first-class framed Contact-page module rather than a loose text note.
- Added the established Antique Gold corner language, Oxford Blue display typography, internal rules and restrained ivory/parchment surface treatment.
- Presented **Employment**, **Freelance** and **Collaboration** as three equal status fields on desktop and a deliberate stacked sequence on mobile.
- Added an editable Availability introduction to `content/site/contact.yml` and the Pages CMS schema.

### Tech Stack
- Restored **Microsoft Excel** with a local SVG icon.
- Added **Polars** alongside **pandas**, with its own local SVG icon and separate CMS entry.
- Rebalanced the 14-item Tech Stack so the final two entries form an intentional two-up final row rather than an incomplete three-column row.

### Practice
- Completed the Practice table with a full perimeter, rounded frame, internal rules, subtle field numbering and cell-level Antique Gold accents.
- Preserved the existing four-column → two-column → one-column responsive behaviour while keeping the table visually closed at every breakpoint.

### Hero map labels
- Re-anchored **Europe** over Europe rather than the North American/Atlantic field.
- Repositioned **Asia** toward the Iran / Pakistan / China belt for a more geographically central placement.
- Preserved the existing North America, South America, Africa and Oceania placements and the Antique Gold tether-marker language.

## Build verification

### Production build
- Build: **passed**
- Project records: **6**
- Generated project detail pages: **5 visible projects**
- Published Notes: **0**
- Draft Notes exposed: **0**

### Automated QA

**11 HTML pages · 108 image references · 0 unresolved local references · 0 duplicate IDs · 0 missing image alt attributes**

Additional validation:
- `.pages.yml` parses successfully.
- v21 desktop/mobile Home, About and Contact renders complete without browser console errors.
- All local SVG technology assets parse and render in the built site.

## Content still pending

These remain deliberate content placeholders rather than technical faults:

- LinkedIn public URL
- Résumé PDF
- project-specific GitHub repository URLs where not yet supplied
