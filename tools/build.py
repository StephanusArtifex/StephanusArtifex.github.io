#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import sys
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse

import mistune
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
SITE_URL = "https://stephanusartifex.github.io"
NOTES_CONTENT = ROOT / "content" / "notes"
PROJECT_CONTENT = ROOT / "content" / "projects"
SITE_CONTENT = ROOT / "content" / "site"
TEMPLATES = ROOT / "templates"

COPY_FILES = ["404.html", ".nojekyll"]
COPY_DIRS = ["assets"]

markdown = mistune.create_markdown(
    escape=False,
    plugins=["strikethrough", "table", "task_lists", "url"],
)

STATUS_LABELS = {
    "in-development": "In development",
    "demonstration": "Demonstration",
    "published": "Published",
    "archived": "Archived",
}
FILTER_LABELS = {
    "analytics": "Analytics",
    "science": "Data Science",
    "engineering": "Data Engineering",
    "ml": "Machine Learning",
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)}: missing YAML front matter")
    try:
        _, front, body = raw.split("---", 2)
    except ValueError as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: malformed front matter") from exc
    data = yaml.safe_load(front) or {}
    return data, body.strip()


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a YAML mapping")
    return data


def slug_from_path(path: Path) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", path.stem.lower()).strip("-")


def parse_date(value: object) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def human_date(value: date | None) -> str:
    if not value:
        return "Draft"
    return f"{value.day} {value.strftime('%B %Y')}"


def reading_time(body: str) -> str:
    words = re.findall(r"\b[\w’'-]+\b", body)
    minutes = max(1, math.ceil(len(words) / 220))
    return f"{minutes} min read"


def normalise_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    return [text] if text else []


def load_site_data() -> dict:
    required = ["settings.yml", "profile.yml", "homepage.yml", "current-direction.yml", "exploring.yml", "tech-stack.yml", "page-copy.yml"]
    missing = [name for name in required if not (SITE_CONTENT / name).exists()]
    if missing:
        raise RuntimeError("Missing site content file(s): " + ", ".join(missing))
    return {
        "settings": load_yaml(SITE_CONTENT / "settings.yml"),
        "profile": load_yaml(SITE_CONTENT / "profile.yml"),
        "home": load_yaml(SITE_CONTENT / "homepage.yml"),
        "direction": load_yaml(SITE_CONTENT / "current-direction.yml"),
        "exploring": load_yaml(SITE_CONTENT / "exploring.yml"),
        "tech": load_yaml(SITE_CONTENT / "tech-stack.yml"),
        "copy": load_yaml(SITE_CONTENT / "page-copy.yml"),
    }


def load_projects() -> list[dict]:
    projects: list[dict] = []
    errors: list[str] = []
    for path in sorted(PROJECT_CONTENT.glob("*.md")):
        try:
            data, body = parse_frontmatter(path)
            title = str(data.get("title", "")).strip()
            summary = str(data.get("summary", "")).strip()
            short_label = str(data.get("short_label", "")).strip()
            if not title or not summary or not short_label:
                raise ValueError("title, short_label and summary are required")
            project = dict(data)
            project.update({
                "slug": slug_from_path(path),
                "title": title,
                "summary": summary,
                "short_label": short_label,
                "visible": bool(data.get("visible", True)),
                "featured": bool(data.get("featured", False)),
                "display_order": int(data.get("display_order", 99) or 99),
                "featured_order": int(data.get("featured_order", 99) or 99),
                "categories": normalise_list(data.get("categories")),
                "filter_keys": normalise_list(data.get("filter_keys")),
                "tech_stack": normalise_list(data.get("tech_stack")),
                "approach_steps": normalise_list(data.get("approach_steps")),
                "model_results": normalise_list(data.get("model_results")),
                "business_implications": normalise_list(data.get("business_implications")),
                "observed_impact": normalise_list(data.get("observed_impact")),
                "case_study": bool(data.get("case_study", False)),
                "status": str(data.get("status", "in-development")),
                "body_md": body,
                "source": path,
            })
            projects.append(project)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if errors:
        raise RuntimeError("\n".join(errors))
    seen = set()
    for project in projects:
        if project["slug"] in seen:
            raise RuntimeError(f"Duplicate project slug: {project['slug']}")
        seen.add(project["slug"])
    return projects


def load_notes(include_drafts: bool) -> list[dict]:
    notes: list[dict] = []
    errors: list[str] = []
    for path in sorted(NOTES_CONTENT.glob("*.md")):
        try:
            data, body = parse_frontmatter(path)
            published = bool(data.get("published", False))
            if not published and not include_drafts:
                continue
            title = str(data.get("title", "")).strip()
            category = str(data.get("category", "")).strip()
            excerpt = str(data.get("excerpt", "")).strip()
            pub_date = parse_date(data.get("publish_date"))
            image = str(data.get("preview_image", "")).strip()
            missing = [name for name, value in (("title", title), ("category", category), ("excerpt", excerpt), ("body", body)) if not value]
            if published and not pub_date:
                missing.append("publish_date")
            if missing:
                raise ValueError(f"missing required field(s): {', '.join(missing)}")
            slug = slug_from_path(path)
            notes.append({
                "slug": slug,
                "title": title or path.stem.replace("-", " ").title(),
                "category": category or "Draft",
                "excerpt": excerpt or "Draft in development.",
                "date": pub_date,
                "date_human": human_date(pub_date),
                "image": image,
                "featured": bool(data.get("featured", False)),
                "published": published,
                "body_md": body,
                "body_html": markdown(body),
                "reading_time": reading_time(body),
                "source": path,
            })
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if errors:
        raise RuntimeError("\n".join(errors))
    seen = set()
    for note in notes:
        if note["slug"] in seen:
            raise RuntimeError(f"Duplicate note slug: {note['slug']}")
        seen.add(note["slug"])
    notes.sort(key=lambda n: (n["date"] or date.min, n["title"].lower()), reverse=True)
    return notes


def replace_tokens(template: str, values: dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def set_inner_html(tag, html_text: str) -> None:
    tag.clear()
    frag = BeautifulSoup(html_text, "html.parser")
    for child in list(frag.contents):
        tag.append(child)


def apply_global_settings(soup: BeautifulSoup, settings: dict) -> None:
    site_title = str(settings.get("site_title", "Steve Muganda"))
    brand = soup.select_one(".brand span")
    if brand:
        brand.string = site_title
    brand_img = soup.select_one(".brand img")
    if brand_img:
        brand_img["src"] = str(settings.get("brand_logo", "/assets/media/site/monogram.svg"))
        brand_img["alt"] = str(settings.get("brand_logo_alt", ""))
    availability = str(settings.get("availability", "Employment · Freelance · Collaboration"))
    for node in soup.select(".contact-modes"):
        node.string = availability
    for button in soup.select("a.button-primary"):
        if "work with me" in button.get_text(" ", strip=True).lower():
            button.string = str(settings.get("work_with_me_label", "Work with me"))

    github = str(settings.get("github_url", "")).strip()
    linkedin = str(settings.get("linkedin_url", "")).strip()
    email = str(settings.get("email", "")).strip()
    for links in soup.select(".contact-links"):
        parts = []
        if github:
            parts.append(f'<a href="{esc(github)}" rel="noreferrer" target="_blank">GitHub ↗</a>')
        else:
            parts.append('<span class="contact-pending">GitHub</span>')
        if linkedin:
            parts.append(f'<a href="{esc(linkedin)}" rel="noreferrer" target="_blank">LinkedIn ↗</a>')
        else:
            parts.append('<span class="contact-pending" title="Add public LinkedIn URL before launch">LinkedIn</span>')
        if email:
            parts.append(f'<a href="mailto:{esc(email)}">Email</a>')
        else:
            parts.append('<span class="contact-pending" title="Add public email address before launch">Email</span>')
        set_inner_html(links, "".join(parts))


def build_home(projects: list[dict], site: dict) -> None:
    soup = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
    profile = site["profile"]
    home = site["home"]
    direction = site["direction"]
    settings = site["settings"]

    name = str(profile.get("name", "Steve Muganda"))
    h1 = soup.select_one("#hero-title")
    if h1:
        h1.string = name

    domains = soup.select_one(".hero-domains")
    if domains:
        domains.string = str(profile.get("domains", ""))

    hook = soup.select_one(".hero-copy")
    if hook:
        hook.string = str(profile.get("hero_hook", ""))

    portrait = soup.select_one(".hero-portrait-primary img")
    if portrait:
        portrait["src"] = str(profile.get("portrait", "/assets/media/profile/steve-muganda-portrait.png"))
        portrait["alt"] = f"Portrait of {name}"

    visual = soup.select_one(".hero-global-field")
    if visual:
        visual["src"] = str(home.get("hero_visual", "/assets/media/site/home-global-intelligence.webp"))
        visual["alt"] = str(home.get("hero_visual_alt", "Global data-intelligence visual"))

    selected_heading = soup.select_one("#selected-title")
    if selected_heading:
        selected_heading.string = str(home.get("selected_work_heading", "Selected Work"))
    view_all = soup.select_one(".selected-view-all")
    if view_all:
        view_all.string = str(home.get("selected_work_view_all_label", "View all work")) + " →"

    featured = sorted([p for p in projects if p["visible"] and p["featured"]], key=lambda p: (p["featured_order"], p["title"].lower()))[:3]
    cards = []
    show_images = bool(home.get("show_selected_work_images", True))
    for p in featured:
        if p["case_study"]:
            action = f'<a class="text-link" href="./work/{esc(p["slug"])}/">View Case Study →</a>'
        else:
            action = f'<span class="text-link text-link-muted" title="Case study in development">{esc(STATUS_LABELS.get(p["status"], p["status"]))}</span>'
        image = str(p.get("cover_image", "")).strip()
        image_html = ""
        if show_images and image:
            image_html = f'<img class="teaser-image" src="{esc(image)}" alt="{esc(p.get("cover_alt") or p["title"])}" />'
        cards.append(f'<article class="teaser">{image_html}<div class="teaser-body"><h3>{esc(p["title"])}</h3><p class="small">{esc(p["short_label"])}</p>{action}</div></article>')
    grid = soup.select_one(".teaser-grid")
    if grid:
        set_inner_html(grid, "".join(cards))

    capabilities_heading = soup.select_one("#capabilities-title")
    if capabilities_heading:
        capabilities_heading.string = str(home.get("capabilities_heading", "Capabilities"))
    capability_grid = soup.select_one(".capability-grid")
    if capability_grid:
        items = home.get("capabilities", []) or []
        rendered = []
        for item in items:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            body = str(item.get("body", "")).strip()
            icon = str(item.get("icon", "")).strip()
            icon_label = str(item.get("icon_label", "")).strip()
            if icon:
                icon_html = f'<span class="capability-icon capability-icon-image"><img src="{esc(icon)}" alt="" /></span>'
            else:
                icon_html = f'<span aria-hidden="true" class="capability-icon">{esc(icon_label)}</span>'
            rendered.append(f'<article class="capability">{icon_html}<div><h3>{esc(title)}</h3><p>{esc(body)}</p></div></article>')
        set_inner_html(capability_grid, "".join(rendered))

    confluence = soup.select_one(".confluence")
    if confluence:
        parts = normalise_list(home.get("confluence"))
        sequence = []
        for idx, part in enumerate(parts):
            if idx:
                sequence.append('<span class="arrow">→</span>')
            sequence.append(f'<span>{esc(part)}</span>')
        set_inner_html(confluence, "".join(sequence))

    direction_section = soup.select_one(".direction")
    if direction_section:
        h2 = direction_section.select_one("h2")
        p = direction_section.select_one("div > p")
        strong = direction_section.select_one(".direction-cta strong")
        if h2:
            h2.string = str(direction.get("heading", "Current Direction"))
        if p:
            p.string = str(direction.get("body", ""))
        if strong:
            strong.string = str(direction.get("cta", ""))

    apply_global_settings(soup, settings)
    (OUT / "index.html").write_text(str(soup), encoding="utf-8")


def build_work(projects: list[dict], site: dict) -> None:
    soup = BeautifulSoup((ROOT / "work" / "index.html").read_text(encoding="utf-8"), "html.parser")
    page_copy = site.get("copy", {})
    heading = soup.select_one(".page-heading h1")
    if heading:
        heading.string = str(page_copy.get("work_heading", "Selected Work"))
    collab_prompt = soup.select_one(".collab-strip > span")
    if collab_prompt:
        collab_prompt.string = str(page_copy.get("work_collaboration_prompt", "Interested in collaborating on a project?"))
    visible = sorted([p for p in projects if p["visible"]], key=lambda p: (p["display_order"], p["title"].lower()))
    used_keys = []
    for key in ["analytics", "science", "ml", "engineering"]:
        if any(key in p["filter_keys"] for p in visible):
            used_keys.append(key)
    buttons = ['<button aria-pressed="true" class="filter-pill" data-filter="all">All</button>']
    buttons += [f'<button aria-pressed="false" class="filter-pill" data-filter="{esc(k)}">{esc(FILTER_LABELS[k])}</button>' for k in used_keys]
    filter_row = soup.select_one(".filter-row")
    if filter_row:
        set_inner_html(filter_row, "".join(buttons))

    cards = []
    for p in visible:
        image = str(p.get("cover_image", "")).strip()
        img_html = f'<img alt="{esc(p.get("cover_alt", p["title"]))}" src="{esc(image)}"/>' if image else ""
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in p["categories"])
        if p["status"] == "demonstration":
            tags += '<span class="status-label">Demonstration</span>'
        if p["case_study"]:
            action = f'<a class="text-link" href="./{esc(p["slug"])}/">View Case Study →</a>'
        else:
            action = f'<span class="text-link text-link-muted" title="Case study in development">{esc(STATUS_LABELS.get(p["status"], p["status"]))}</span>'
        cards.append(f'''<article class="project-card" data-category="{esc(' '.join(p['filter_keys']))}" data-project-card="">{img_html}<div class="project-card-body"><h2>{esc(p['title'])}</h2><p>{esc(p['summary'])}</p><div class="tags">{tags}</div>{action}</div></article>''')
    grid = soup.select_one(".project-grid")
    if grid:
        set_inner_html(grid, "".join(cards))
    apply_global_settings(soup, site["settings"])
    target = OUT / "work" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(str(soup), encoding="utf-8")


def case_section(section_id: str, title: str, body_html: str) -> str:
    return f'<section class="case-section" id="{esc(section_id)}"><h2>{esc(title)}</h2>{body_html}</section>'


def list_html(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def build_case_study(project: dict, site: dict) -> None:
    sections: list[tuple[str, str, str]] = []
    overview = f'<p>{esc(project["summary"])}</p>'
    sections.append(("overview", "Executive Summary", overview))
    if project.get("business_need"):
        sections.append(("business", "Business Need", f'<p>{esc(project["business_need"])}</p>'))
    if project["approach_steps"]:
        workflow = '<div class="workflow">' + '<span class="workflow-arrow">→</span>'.join(
            f'<div class="workflow-step"><span class="workflow-symbol">{i+1:02d}</span>{esc(step)}</div>' for i, step in enumerate(project["approach_steps"])
        ) + '</div>'
        sections.append(("approach", "Approach", workflow))
    if project.get("data_features"):
        sections.append(("data", "Data & Features", f'<p>{esc(project["data_features"])}</p>'))
    if project.get("modelling"):
        sections.append(("modelling", "Modelling", f'<p>{esc(project["modelling"])}</p>'))
    if project.get("evaluation"):
        sections.append(("evaluation", "Evaluation", f'<div class="evidence-pending" role="note"><p>{esc(project["evaluation"])}</p></div>'))
    if project["model_results"] or project["business_implications"]:
        boxes = []
        if project["model_results"]:
            boxes.append(f'<div class="result-box"><h3>Model Results</h3>{list_html(project["model_results"])}</div>')
        if project["business_implications"]:
            boxes.append(f'<div class="result-box"><h3>Business Implications</h3>{list_html(project["business_implications"])}</div>')
        sections.append(("results", "Results", '<div class="result-grid">' + ''.join(boxes) + '</div>'))
    if project["observed_impact"]:
        sections.append(("impact", "Observed Impact", list_html(project["observed_impact"])))
    if project.get("limitations"):
        sections.append(("limitations", "Limitations", f'<p>{esc(project["limitations"])}</p>'))
    if project["tech_stack"]:
        tech = '<div class="tech-list">' + ''.join(f'<span class="tech">{esc(t)}</span>' for t in project["tech_stack"]) + '</div>'
        sections.append(("stack", "Tech Stack", tech))
    if project.get("conclusion"):
        sections.append(("conclusion", "Conclusion", f'<p>{esc(project["conclusion"])}</p>'))
    links = []
    if str(project.get("repository_url", "")).strip():
        links.append(f'<a class="text-link" href="{esc(project["repository_url"])}" target="_blank" rel="noreferrer">Repository ↗</a>')
    if str(project.get("live_demo_url", "")).strip():
        links.append(f'<a class="text-link" href="{esc(project["live_demo_url"])}" target="_blank" rel="noreferrer">Live demo ↗</a>')
    if links:
        sections.append(("links", "Links", '<div class="tech-list">' + ''.join(links) + '</div>'))

    nav = ''.join(f'<a href="#{sid}"{(" class=\"is-active\"" if i == 0 else "")}>{esc(title)}</a>' for i, (sid, title, _) in enumerate(sections))
    body = ''.join(case_section(sid, title, content) for sid, title, content in sections)
    tags = ''.join(f'<span class="tag">{esc(t)}</span>' for t in project["tech_stack"])
    settings = site["settings"]
    contact = global_footer_html(settings, depth=2)
    html_doc = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/><meta name="description" content="{esc(project['summary'])}"/><meta name="theme-color" content="#123D32"/><title>{esc(project['title'])} | Steve Muganda</title><link rel="preconnect" href="https://fonts.googleapis.com"/><link crossorigin href="https://fonts.gstatic.com" rel="preconnect"/><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Playfair+Display:ital,wght@0,500;1,500&amp;display=swap" rel="stylesheet"/><link href="../../assets/css/styles.css" rel="stylesheet"/></head><body><a class="skip-link" href="#main">Skip to content</a>
{header_html(depth=2, current='work', settings=settings)}
<main class="container page" id="main"><div class="case-layout"><aside aria-label="Case study sections" class="case-nav"><h2>Case Study</h2>{nav}</aside><article class="case-content"><header class="case-title"><h1>{esc(project['title'])}</h1><div class="tags">{tags}</div></header>{body}</article></div></main>
{contact}<script defer src="../../assets/js/site.js"></script><script defer src="../../assets/js/case.js"></script></body></html>'''
    target = OUT / "work" / project["slug"] / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_doc, encoding="utf-8")


def header_html(depth: int, current: str, settings: dict) -> str:
    prefix = "../" * depth
    def nav(link: str, label: str, key: str) -> str:
        current_attr = ' aria-current="page"' if current == key else ''
        return f'<a{current_attr} href="{prefix}{link}">{label}</a>'
    return f'''<header class="site-header"><div class="container header-inner"><a class="brand" href="{prefix}"><img alt="{esc(settings.get('brand_logo_alt',''))}" src="{esc(settings.get('brand_logo', '/assets/media/site/monogram.svg'))}"/><span>{esc(settings.get('site_title','Steve Muganda'))}</span></a><button aria-expanded="false" aria-label="Open navigation" class="nav-toggle" data-nav-toggle=""><span></span></button><nav class="site-nav" data-nav="">{nav('', 'Home', 'home')}{nav('work/', 'Work', 'work')}{nav('about/', 'About', 'about')}{nav('notes/', 'Notes', 'notes')}<a class="button button-primary" href="#contact">{esc(settings.get('work_with_me_label','Work with me'))}</a></nav></div></header>'''


def global_footer_html(settings: dict, depth: int = 0) -> str:
    github = str(settings.get("github_url", "")).strip()
    linkedin = str(settings.get("linkedin_url", "")).strip()
    email = str(settings.get("email", "")).strip()
    links = []
    if github: links.append(f'<a href="{esc(github)}" rel="noreferrer" target="_blank">GitHub ↗</a>')
    else: links.append('<span class="contact-pending">GitHub</span>')
    if linkedin: links.append(f'<a href="{esc(linkedin)}" rel="noreferrer" target="_blank">LinkedIn ↗</a>')
    else: links.append('<span class="contact-pending" title="Add public LinkedIn URL before launch">LinkedIn</span>')
    if email: links.append(f'<a href="mailto:{esc(email)}">Email</a>')
    else: links.append('<span class="contact-pending" title="Add public email address before launch">Email</span>')
    return f'<footer class="contact-footer" id="contact"><div class="container contact-inner"><div class="contact-links">{"".join(links)}</div><div class="contact-modes">{esc(settings.get("availability", "Employment · Freelance · Collaboration"))}</div></div></footer>'


def build_about(site: dict) -> None:
    soup = BeautifulSoup((ROOT / "about" / "index.html").read_text(encoding="utf-8"), "html.parser")
    profile = site["profile"]
    settings = site["settings"]
    page_copy = site.get("copy", {})
    about_eyebrow = soup.select_one(".about6-kicker")
    if about_eyebrow:
        about_eyebrow.string = str(page_copy.get("about_eyebrow", "About"))
    exploring_heading = soup.select_one("#exploring .about6-side-title h2")
    if exploring_heading:
        exploring_heading.string = str(page_copy.get("exploring_heading", "Currently Exploring"))
    tech_heading = soup.select_one("#tech-stack .about6-side-title h2")
    if tech_heading:
        tech_heading.string = str(page_copy.get("tech_stack_heading", "Tech Stack"))
    beyond_heading = soup.select_one("#beyond .about6-side-title h2")
    if beyond_heading:
        beyond_heading.string = str(page_copy.get("beyond_work_heading", "Beyond Work"))
    name = str(profile.get("name", "Steve Muganda"))
    name_node = soup.select_one("#about6-name")
    if name_node: name_node.string = name
    manifesto = soup.select_one(".about6-manifesto")
    if manifesto:
        set_inner_html(manifesto, ''.join(f'<span>{esc(x)}</span>' for x in normalise_list(profile.get("manifesto"))))
    left_copy = soup.select_one(".about6-left-copy")
    if left_copy: left_copy.string = str(profile.get("opening", ""))
    inscription = soup.select_one(".about6-inscription")
    if inscription:
        set_inner_html(inscription, ''.join(f'<span>{esc(x)}</span>' for x in normalise_list(profile.get("inscription"))))
    portrait = soup.select_one(".about6-portrait")
    if portrait:
        portrait["src"] = str(profile.get("portrait", "/assets/img/about-portrait.png"))
        portrait["alt"] = f"Portrait of {name}"
    domains = soup.select_one(".about6-domains")
    if domains:
        d = [x.strip() for x in str(profile.get("domains", "")).split("·") if x.strip()]
        first = ' <b>•</b> '.join(map(esc, d[:3]))
        second = ' <b>•</b> '.join(map(esc, d[3:]))
        set_inner_html(domains, first + ('<br/>' + second if second else ''))
    opening = soup.select_one(".about6-opening")
    if opening: opening.string = str(profile.get("opening", ""))
    copy_paras = soup.select(".about6-copy p")
    if len(copy_paras) >= 3:
        copy_paras[1].string = str(profile.get("intro", ""))
        copy_paras[2].string = str(profile.get("chain", ""))
    field_map = {
        "focus": ("focus_title", "focus_body"),
        "approach": ("approach_title", "approach_body"),
        "interests": ("interests_title", "interests_body"),
        "collaboration": ("collaboration_title", "collaboration_body"),
    }
    for sid, (title_key, body_key) in field_map.items():
        cell = soup.select_one(f"#{sid}")
        if not cell: continue
        p = cell.select_one("p")
        if p:
            set_inner_html(p, f'<strong>{esc(profile.get(title_key, ""))}</strong> {esc(profile.get(body_key, ""))}')
    beyond = soup.select_one(".about6-beyond-copy")
    if beyond: beyond.string = str(profile.get("beyond_work", ""))

    timeline = soup.select_one(".about6-timeline")
    if timeline:
        items = normalise_list(site["exploring"].get("items"))
        set_inner_html(timeline, ''.join(f'<li class="{"red" if i == 0 else ""}">{esc(item)}</li>' for i, item in enumerate(items)))
    tech_grid = soup.select_one(".about6-tech-grid")
    if tech_grid:
        items = site["tech"].get("items", []) or []
        tech_html = []
        for item in items:
            if not isinstance(item, dict) or not item.get("visible", True): continue
            tech_html.append(f'<div><img alt="" src="{esc(item.get("icon", ""))}"/><span>{esc(item.get("name", ""))}</span></div>')
        set_inner_html(tech_grid, ''.join(tech_html))

    cta_text = soup.select_one(".about6-cta p")
    if cta_text: cta_text.string = str(site["direction"].get("cta", ""))
    cta_link = soup.select_one(".about6-cta a")
    if cta_link:
        set_inner_html(cta_link, esc(settings.get("work_with_me_label", "Work with me")) + ' <span>→</span>')
    contact = soup.select_one(".about6-contact")
    if contact:
        email = str(settings.get("email", "")).strip()
        linkedin = str(settings.get("linkedin_url", "")).strip()
        location = str(settings.get("location", "Remote · Open to relocation"))
        email_html = f'<a href="mailto:{esc(email)}"><span class="about6-contact-symbol">✉</span>Email</a>' if email else '<span class="about6-contact-pending" title="Add public email address"><span class="about6-contact-symbol">✉</span>Email</span>'
        linkedin_html = f'<a href="{esc(linkedin)}" target="_blank" rel="noreferrer"><span class="about6-linkedin">in</span>LinkedIn</a>' if linkedin else '<span class="about6-contact-pending" title="Add public LinkedIn URL"><span class="about6-linkedin">in</span>LinkedIn</span>'
        location_html = f'<span><span class="about6-contact-symbol">⌖</span><span class="about6-location-long">{esc(location)}</span><span class="about6-location-short">Remote</span></span>'
        set_inner_html(contact, email_html + linkedin_html + location_html)
    apply_global_settings(soup, settings)
    target = OUT / "about" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(str(soup), encoding="utf-8")


def build_notes_index(notes: list[dict], site: dict) -> None:
    template = (TEMPLATES / "notes-index.html").read_text(encoding="utf-8")
    page_copy = site.get("copy", {})
    template = replace_tokens(template, {
        "NOTES_EYEBROW": esc(page_copy.get("notes_eyebrow", "Technical journal")),
        "NOTES_HEADING": esc(page_copy.get("notes_heading", "Notes")),
        "NOTES_INTRO": esc(page_copy.get("notes_intro", "Thoughts, explanations and technical write-ups.")),
    })
    target = OUT / "notes" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not notes:
        content = f'<section class="notes-empty" aria-labelledby="notes-empty-title"><p class="eyebrow">{esc(page_copy.get("notes_empty_eyebrow", "In preparation"))}</p><h2 id="notes-empty-title">{esc(page_copy.get("notes_empty_heading", "The technical journal is being prepared."))}</h2><p>{esc(page_copy.get("notes_empty_body", "Finished notes will appear here as they are published."))}</p></section>'
        data_script = '<script type="application/json" id="notes-data">{}</script>'
    else:
        item_parts = []
        data: dict[str, dict] = {}
        for note in notes:
            draft_label = '<span class="note-draft-badge">Draft preview</span>' if not note["published"] else ""
            featured_class = " is-featured" if note["featured"] else ""
            item_parts.append(f'<button class="note-item{featured_class}" data-note="{esc(note["slug"])}"><span><h2>{esc(note["title"])}</h2><span class="note-category">{esc(note["category"])}</span>{draft_label}</span><small>{esc(note["date_human"])}</small></button>')
            data[note["slug"]] = {"title": note["title"], "category": note["category"], "excerpt": note["excerpt"], "image": note["image"], "href": f"./{note['slug']}/", "date": note["date_human"], "draft": not note["published"]}
        preview_note = next((n for n in notes if n["featured"]), notes[0])
        preview_img = f'<img data-preview-image src="{esc(preview_note["image"])}" alt="{esc(preview_note["title"])} visual preview" />' if preview_note["image"] else '<img data-preview-image hidden alt="" />'
        content = f'<div class="notes-layout"><div aria-label="Technical notes" class="notes-list">{"".join(item_parts)}</div><aside aria-live="polite" class="note-preview" data-note-preview tabindex="-1"><p class="category" data-preview-category></p><h2 data-preview-title></h2><p class="note-preview-date" data-preview-date></p><p data-preview-abstract></p>{preview_img}<a class="text-link editorial-link" data-preview-link href="./{esc(preview_note["slug"])}/">Read article →</a></aside></div>'
        data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        data_script = f'<script type="application/json" id="notes-data">{data_json}</script>'
    target.write_text(replace_tokens(template, {"NOTES_CONTENT": content, "NOTES_DATA": data_script}), encoding="utf-8")


def build_article(note: dict) -> None:
    template = (TEMPLATES / "note.html").read_text(encoding="utf-8")
    target_dir = OUT / "notes" / note["slug"]
    target_dir.mkdir(parents=True, exist_ok=True)
    image = note["image"]
    hero = ""
    og = ""
    if image:
        hero = f'<figure class="note-hero"><img src="{esc(image)}" alt="Visual for {esc(note["title"])}" /></figure>'
        og_url = image if image.startswith(("http://", "https://")) else SITE_URL + "/" + image.lstrip("/")
        og = f'<meta property="og:image" content="{esc(og_url)}" />'
    canonical = f"{SITE_URL}/notes/{note['slug']}/"
    title_suffix = " (Draft Preview)" if not note["published"] else ""
    target = replace_tokens(template, {"TITLE": esc(note["title"] + title_suffix), "DESCRIPTION": esc(note["excerpt"]), "CATEGORY": esc(note["category"]), "DATE_ISO": esc(note["date"].isoformat() if note["date"] else ""), "DATE_HUMAN": esc(note["date_human"]), "READING_TIME": esc(note["reading_time"]), "HERO_IMAGE": hero, "OG_IMAGE": og, "CANONICAL_URL": esc(canonical), "BODY": note["body_html"]})
    (target_dir / "index.html").write_text(target, encoding="utf-8")


def build_feed(notes: list[dict]) -> None:
    published = [n for n in notes if n["published"]]
    items = []
    for note in published:
        pub_dt = datetime.combine(note["date"], time.min, tzinfo=timezone.utc)
        url = f"{SITE_URL}/notes/{note['slug']}/"
        items.append("<item>" f"<title>{esc(note['title'])}</title>" f"<link>{esc(url)}</link>" f"<guid>{esc(url)}</guid>" f"<pubDate>{format_datetime(pub_dt)}</pubDate>" f"<description>{esc(note['excerpt'])}</description>" f"<category>{esc(note['category'])}</category>" "</item>")
    feed = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Steve Muganda Notes</title>' f'<link>{SITE_URL}/notes/</link><description>Technical notes on data analytics, data science, machine learning and data engineering.</description><language>en</language>' + "".join(items) + '</channel></rss>\n'
    target = OUT / "notes" / "feed.xml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(feed, encoding="utf-8")


def copy_static() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for filename in COPY_FILES:
        source = ROOT / filename
        if source.exists(): shutil.copy2(source, OUT / filename)
    for dirname in COPY_DIRS:
        source = ROOT / dirname
        if source.exists(): shutil.copytree(source, OUT / dirname)


def apply_global_settings_to_generated_html(settings: dict) -> None:
    for path in OUT.rglob("*.html"):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        apply_global_settings(soup, settings)
        path.write_text(str(soup), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the StephanusArtifex CMS-backed static portfolio.")
    parser.add_argument("--include-drafts", action="store_true", help="Include draft Notes for local preview only.")
    args = parser.parse_args()
    try:
        site = load_site_data()
        projects = load_projects()
        notes = load_notes(args.include_drafts)
        copy_static()
        build_home(projects, site)
        build_work(projects, site)
        build_about(site)
        for project in projects:
            if project["visible"] and project["case_study"]:
                build_case_study(project, site)
        build_notes_index(notes, site)
        build_feed(notes)
        for note in notes:
            build_article(note)
        apply_global_settings_to_generated_html(site["settings"])
    except Exception as exc:
        print(f"Build failed:\n{exc}", file=sys.stderr)
        return 1
    published_notes = sum(1 for n in notes if n["published"])
    draft_notes = sum(1 for n in notes if not n["published"])
    case_studies = sum(1 for p in projects if p["visible"] and p["case_study"])
    print(f"Built {OUT}: {len(projects)} project record(s), {case_studies} case study page(s), {published_notes} published note(s), {draft_notes} draft preview(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
