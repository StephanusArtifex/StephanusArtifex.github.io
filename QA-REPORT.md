# QA Report — v20 mobile map-label restoration

## Purpose

This follow-up addresses the mobile map losing geographic meaning. The desktop composition remains unchanged. The mobile hero keeps the v19 structure while restoring explicit continent labels over the analytical world field.

## Rectifications

- Restored all six geographic overlay labels on mobile: **North America, South America, Europe, Africa, Asia and Oceania**.
- Repositioned the labels for the mobile crop rather than inheriting the desktop coordinates.
- Widened the mobile map framing so Asia and Oceania remain visibly represented instead of being pushed off-frame by the former zoom.
- Increased label weight and added a restrained ivory backing/text halo so the labels remain readable over mixed map tones.
- Retained the antique-gold tether line and point-marker language used on desktop.
- Kept the portrait, map crop, hero hook, three peer actions, discipline rail, Selected Work, Practice, contact order and desktop rules unchanged.
- All v20 changes are scoped to `max-width: 760px` and below.

## Build verification

### Production build
- Build: **passed**
- Project records: **6**
- Generated project detail pages: **5 visible projects**
- Published Notes: **0**
- Draft Notes exposed: **0**

### Automated QA

Production result:

**11 HTML pages · 106 image references · 0 unresolved local references · 0 duplicate IDs · 0 missing image alt attributes**

## Content still pending

These remain deliberate content placeholders rather than technical faults:

- LinkedIn public URL
- Résumé PDF
- project-specific GitHub repository URLs where not yet supplied
