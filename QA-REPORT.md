# QA Report — v15 homepage implementation

## Scope

This pass implements the approved portrait-led homepage while preserving the CMS-backed publishing architecture and the v14 contact/project-link fixes.

## Implemented

- Hero keeps the narrowed professional scope: Data Analytics · Data Science · Machine Learning · Data Engineering.
- Hook remains: “Analytics that inform. Models that forecast. Systems built to scale.”
- Portrait remains CMS-driven from `content/site/profile.yml`.
- Global intelligence visual remains CMS-replaceable from `content/site/homepage.yml`.
- Map rendering is deliberately higher-saturation and higher-contrast than v14.
- Continent labels are presentation overlays and do not alter the underlying media asset.
- Résumé is no longer a route or navigation item.
- `settings.resume_file` drives a direct homepage résumé/PDF artefact link; when blank, a non-broken placeholder is shown.
- Selected Work cards show image, summary, category tags, `Read more`, and GitHub state.
- All four capability icons are local SVG assets and remain replaceable through the Homepage CMS record.
- Contact remains a real `/contact/` route.

## Automated checks

Validated against both production and draft-inclusive builds:

- CMS YAML parses successfully.
- Python build/preview scripts compile.
- 0 unresolved internal links.
- 0 duplicate HTML ids.
- 0 missing `alt` attributes on images.
- 0 `/resume/` links in generated HTML.
- No generated `/resume/` directory.
- 4 capability icon images render from CMS-backed records.
- 3 Selected Work cards contain project actions.
- CSS braces balance.

## Content still pending

- Public résumé PDF upload.
- Public LinkedIn URL and email, if desired.
- Repository URLs for project records currently showing GitHub as pending.
- Validated evidence for project records still marked demonstration/in-development.
