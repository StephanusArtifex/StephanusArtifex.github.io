# CMS Publishing Workflow

Pages CMS is the editorial layer; the visual constitution remains protected in code.

## Everyday workflow

1. Sign into Pages CMS with GitHub.
2. Open `StephanusArtifex.github.io`.
3. Edit text, reorder items, replace media or publish content.
4. Save.
5. Pages CMS commits the change to GitHub.
6. GitHub Actions runs `python tools/build.py`.
7. GitHub Pages deploys the rebuilt site automatically.

Routine publishing requires no HTML editing.

## Homepage

Editable fields include:
- global data-intelligence visual and alt text
- Selected Work heading and view-all label
- whether project images appear
- **Practice** heading and introduction
- Practice titles, descriptions and replaceable icons

The professional discipline rail, portrait and homepage hook derive from **About / Profile**, keeping identity consistent across Home and About.

The Résumé button is driven by **Contact & Site Settings → Résumé PDF**. Upload or replace the PDF there. The button links directly to the file; there is no résumé page.

## Work / Case Studies

Each project is one record. That record can drive the Work page, Selected Work on Home and its full project article.

Editable fields include title, summary, categories, cover image, display order, Home feature toggle, case-study evidence, repository URL and live-demo URL.

Every showcased work receives:
- **Read more** → its generated project article
- **GitHub** → its repository URL once supplied

## Notes

Create, revise, draft and publish technical articles. Preview images and images inside the rich-text body can be uploaded directly. Publishing regenerates the Notes index, article route, metadata and RSS feed.

## About / Profile

Editable fields include name, disciplines, homepage hook, portrait, About copy, Focus, Approach, Interests, Collaboration, inscription and Beyond Work. The same portrait is used on Home and About.

## Currently Exploring / Tech Stack

Currently Exploring is an editable ordered list. Tech Stack entries can be added, hidden, reordered, renamed and given replacement icon files.

## Collaboration Invitation

The About-page collaboration invitation is editable from the CMS without changing the page layout.

## Contact & Site Settings

One source of truth for:
- site title and description
- brand monogram/logo
- GitHub URL
- LinkedIn URL
- public email
- location
- availability line
- Résumé PDF
- Work with me label

Public location is currently **Nairobi**.

## Media libraries

- Notes images → `assets/media/notes`
- Project images → `assets/media/projects`
- Profile images → `assets/media/profile`
- Site visuals and Practice icons → `assets/media/site`
- Technology icons → `assets/media/tech`
- Documents → `assets/media/documents`

## Protected in code

The CMS does not expose colour tokens, typography, responsive breakpoints, lancet geometry, ornament rules, interaction logic, accessibility behaviour or chart-colour semantics.

## Local preview

```bash
python -m pip install -r requirements.txt
python tools/preview.py --drafts
```

Then open `http://127.0.0.1:8000`.

## Content integrity

Do not invent metrics, client names, impact or deployments. Use **Observed Impact** only for genuine evidenced outcomes. Keep unfinished work marked appropriately.
