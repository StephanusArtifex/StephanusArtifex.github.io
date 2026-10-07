# v22.1 QA Report

- Availability redundancy removed: one heading plus Employment, Freelance and Collaboration status fields; no repeated eyebrow or explanatory sentence.
This pass applies the requested corrections to the actual source, CMS content and generated `_site` output.

## Corrected areas

- Tech Stack now includes Microsoft Excel and Polars as distinct first-class entries with local SVG icons; pandas remains a separate entry.
- Availability is rendered as a framed, first-class Contact module with three deliberate status fields: Employment, Freelance and Collaboration.
- Practice is completed as a bounded four-column module with a closing edge, internal rules, icon treatments and restrained numbering.
- Mobile map labels are re-anchored against the actual mobile map crop. Europe, South America and Oceania are pulled onto their visible landmasses, while Asia remains centred around the Iran/Pakistan/China field.

## Build validation

QA passed: 11 HTML pages, 108 image references, 0 unresolved local references, 0 duplicate IDs, 0 missing image alt attributes.

Exact validation renders were generated directly from the built `_site` HTML/CSS/assets, without reusing older screenshots.
