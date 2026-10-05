# StephanusArtifex.github.io

Portfolio website for Steve Muganda across Data Analytics, Data Science, Machine Learning and Data Engineering.

## Architecture

The portfolio remains a lightweight static site with a browser-based content layer:

- Pages CMS edits structured content and media stored in the repository.
- Notes are stored as Markdown in `content/notes/`.
- Projects and case studies are stored in `content/projects/`.
- Homepage, About, shared labels, Tech Stack, Current Direction and site settings are stored in `content/site/`.
- `tools/build.py` generates the public site from those records.
- GitHub Actions builds and deploys `_site/` to GitHub Pages after every push to `main`.
- Draft Notes stay in the repository but are excluded from production.

The visual design remains independent of the publishing workflow. Routine content and image updates require no HTML editing.

See `CMS-PUBLISHING.md` for the editor workflow.

## Design constitution

- **Deep Cathedral Green** `#123D32`: identity and primary actions.
- **Oxford Blue** `#142B4A`: technical intelligence, diagrams and primary chart series.
- **Prayerbook Rubric Red** `#8B2C2F`: editorial and scholarly emphasis only.
- **Antique Gold** `#B3924A`: ceremony, ornament and chart benchmarks.
- **Charcoal** `#252622`: principal text and structure.
- **Ivory** `#F7F3E9`: primary field.
- **Parchment** `#EDE4D2`: secondary surfaces.

Ornament is punctuation, never wallpaper. About owns the site's only lancet arch.

See `DESIGN-SPEC.md` for the full implementation rules.

## Local development

Install dependencies once:

```bash
python -m pip install -r requirements.txt
```

Build and preview the public site:

```bash
python tools/preview.py
```

Include draft Notes:

```bash
python tools/preview.py --drafts
```

The preview runs at `http://127.0.0.1:8000` by default.

## GitHub Pages

The repository includes `.github/workflows/deploy.yml`. Configure **Settings → Pages → Source → GitHub Actions** once. Thereafter, pushes to `main`, including Pages CMS edits, build and deploy automatically.

## Content integrity

Drafts are never included in the production Notes index. Published notes must provide a title, category, excerpt, publication date and body. Portfolio metrics and project impact remain evidence-led and should not be invented.

## Content management

The site uses Pages CMS as a browser-based editorial layer over GitHub. Notes, Work/Case Studies, About/Profile, Currently Exploring, Tech Stack, Current Direction and shared Contact/Site Settings are editable without routine HTML changes. The visual design remains code-controlled.

See `CMS-PUBLISHING.md` for the publishing workflow.


## v13 CMS media

Homepage visuals, profile images, project covers, Note images, technology icons and the brand mark are now CMS media fields. See `CMS-PUBLISHING.md`.
