# CMS Publishing Workflow

The portfolio is content-managed through Pages CMS while the visual constitution remains code-controlled.

## Everyday workflow

1. Sign into Pages CMS with GitHub.
2. Open the `StephanusArtifex.github.io` repository.
3. Choose the section you want to edit.
4. Edit text, reorder items, upload/replace media, or publish content.
5. Save.
6. Pages CMS commits the change to GitHub.
7. GitHub Actions runs `python tools/build.py`.
8. GitHub Pages deploys the rebuilt site automatically.

Routine publishing requires no HTML editing.

## CMS areas

### Homepage
Editable from one singleton record:
- hero data-intelligence visual
- hero visual alt text
- Selected Work heading and view-all label
- whether project images appear in Selected Work
- Capabilities heading
- capability titles and descriptions
- capability fallback letters or optional uploaded icons
- Confluence sequence

The hero portrait and professional scope come from **About / Profile**, so Home and About stay consistent.

### Notes
Create, revise, draft and publish technical articles.

Editable media:
- preview image
- images embedded inside the rich-text article body

Publishing automatically generates the Notes index, article page, metadata and RSS feed.

### Work / Case Studies
Each project is one CMS record. The same record powers the Work page, Featured/Selected Work on Home, and any case-study page.

Editable content includes:
- title, summary and taxonomy
- Work visibility and ordering
- Home feature toggle and ordering
- project cover image and alt text
- technology stack
- case-study publication and evidence sections
- repository and live-demo links

`Feature on Home` controls Selected Work. Project images shown there come from the same editable `Project image` field used on Work.

### About / Profile
Editable:
- name
- professional disciplines
- homepage hook
- People / Data / Systems / Impact manifesto
- About copy
- Focus, Approach, Interests and Collaboration
- inscription
- Beyond Work
- portrait

The same uploaded portrait is used on both Home and About.

### Currently Exploring
Editable ordered list for the About timeline.

### Tech Stack
Each technology can be added, hidden, reordered or renamed. Its icon is an **image field**, so icons can be uploaded and replaced directly in the CMS.

### Current Direction
Editable Home-page Current Direction heading, body and collaboration invitation.

### Page Headings & Labels
Editable labels for the Work, Notes and About information sections, including the Notes empty state.

### Contact & Site Settings
One source of truth for:
- site title and description
- brand monogram/logo image
- GitHub, LinkedIn and public email
- location / remote status
- availability line
- Work with me label

## Media libraries

The CMS exposes separate media libraries so replacements remain organised:

- `Notes images` → `assets/media/notes`
- `Project images` → `assets/media/projects`
- `Profile images` → `assets/media/profile`
- `Site visuals` → `assets/media/site`
- `Technology icons` → `assets/media/tech`

When you replace an image in the CMS, the content record receives the new repository path and the next build uses it automatically. No HTML path editing is required.

## What remains protected in code

The CMS does not expose:
- colour tokens
- typography
- grid geometry
- lancet architecture
- ornament rules
- responsive breakpoints
- interaction logic
- accessibility behaviour
- chart colour semantics

This keeps content flexible without turning the portfolio into a page builder.

## Local preview

Install dependencies once:

```bash
pip install -r requirements.txt
```

Preview the production content set:

```bash
python tools/preview.py
```

Preview Notes drafts as well:

```bash
python tools/preview.py --drafts
```

Then open `http://127.0.0.1:8000`.

## Content integrity

- Do not publish fabricated project metrics.
- Use **Observed Impact** only for genuine evidenced outcomes.
- Keep unfinished work marked `In development` or `Demonstration`.
- Enable a full case-study page only when its content is ready for public use.
- Every meaningful uploaded image should have suitable alt text where the CMS exposes that field.
