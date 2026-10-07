# StephanusArtifex.github.io

Portfolio website for Steve Muganda across **Data Analytics, Data Science, Machine Learning and Data Engineering**.

## Architecture

The portfolio is a lightweight static site with a browser-based content layer:

- Pages CMS edits structured content and media stored in the repository.
- Notes live in `content/notes/`.
- Projects and case studies live in `content/projects/`.
- Homepage, About, Tech Stack and shared site settings live in `content/site/`.
- `tools/build.py` generates the public site into `_site/`.
- GitHub Actions deploys `_site/` to GitHub Pages after every push to `main`.
- Draft Notes remain in the repository but are excluded from production.

The design remains code-controlled. Routine content and image updates require no HTML editing.

## Current homepage constitution

- Full-width discipline rail: Data Analytics, Data Science, Machine Learning, Data Engineering.
- Portrait-led hero with the hook: **Analytics that inform. Models that forecast. Systems built to scale.**
- High-contrast global intelligence field with tethered continent labels.
- Three equal hero actions: **Work with me**, **View work**, **Résumé**.
- The Résumé action links directly to the uploaded PDF and has no dedicated page.
- Contact strip with Email, LinkedIn, GitHub and Nairobi.
- Selected Work with **Read more** and **GitHub** actions.
- **Practice** section with four matched line icons.

## Local development

Install dependencies once:

```bash
python -m pip install -r requirements.txt
```

Preview public content:

```bash
python tools/preview.py
```

Include draft Notes:

```bash
python tools/preview.py --drafts
```

The preview runs at `http://127.0.0.1:8000` by default.

Validate the generated site:

```bash
python tools/qa.py
```

The build rewrites internal asset and route references to page-relative URLs, so generated pages remain valid on GitHub Pages, local preview servers and QA copies. GitHub Actions runs the same QA check before deployment.

## GitHub Pages

Configure **Settings → Pages → Source → GitHub Actions** once. Thereafter, pushes to `main`, including Pages CMS edits, build and deploy automatically.

## Design constitution

- Deep Cathedral Green `#123D32`: identity and primary action.
- Oxford Blue `#142B4A`: technical intelligence and structure.
- Prayerbook Rubric Red `#8B2C2F`: editorial emphasis only.
- Antique Gold `#B3924A`: ceremony, reference and ornament.
- Charcoal `#252622`: principal text.
- Ivory `#F7F3E9`: primary ground.
- Parchment `#EDE4D2`: secondary surfaces.

**Majesty through restraint.** Ornament is punctuation, never wallpaper. About retains the site's only lancet arch.

See `CMS-PUBLISHING.md` and `DESIGN-SPEC.md` for the operational and visual rules.
