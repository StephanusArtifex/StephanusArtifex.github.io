#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "javascript:", "data:")


def local_target(page: Path, value: str) -> Path | None:
    value = value.strip()
    if not value or value.startswith("#") or value.startswith(EXTERNAL_PREFIXES):
        return None
    clean = unquote(value.split("?", 1)[0].split("#", 1)[0])
    target = (page.parent / clean).resolve()
    if clean.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def main() -> int:
    if not SITE.exists():
        print("QA failed: _site does not exist. Run tools/build.py first.", file=sys.stderr)
        return 1

    issues: list[str] = []
    html_files = sorted(SITE.rglob("*.html"))
    image_count = 0

    for page in html_files:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        rel_page = page.relative_to(SITE)

        ids = [str(tag.get("id")) for tag in soup.find_all(id=True)]
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        if duplicates:
            issues.append(f"{rel_page}: duplicate id(s): {', '.join(duplicates)}")

        for img in soup.find_all("img"):
            image_count += 1
            if not img.has_attr("alt"):
                issues.append(f"{rel_page}: image missing alt attribute: {img.get('src', '')}")

        for tag in soup.find_all(True):
            for attr in ("src", "href", "poster", "action"):
                value = tag.get(attr)
                if not isinstance(value, str):
                    continue
                if value.startswith("/") and not value.startswith("//"):
                    issues.append(f"{rel_page}: site-root {attr} remains after build: {value}")
                    continue
                target = local_target(page, value)
                if target is not None and not target.exists():
                    issues.append(f"{rel_page}: unresolved {attr}: {value}")

        data_node = soup.find("script", id="notes-data")
        if data_node and data_node.string:
            try:
                data = json.loads(data_node.string)
                for slug, record in data.items():
                    image = str(record.get("image", "")).strip()
                    if image:
                        target = local_target(page, image)
                        if target is not None and not target.exists():
                            issues.append(f"{rel_page}: unresolved Notes preview image for {slug}: {image}")
            except json.JSONDecodeError as exc:
                issues.append(f"{rel_page}: invalid notes-data JSON: {exc}")

    css_url = re.compile(r"url\((?:['\"])?([^)'\"]+)")
    for css in sorted(SITE.rglob("*.css")):
        text = css.read_text(encoding="utf-8")
        for value in css_url.findall(text):
            value = value.strip()
            if value.startswith(EXTERNAL_PREFIXES) or value.startswith("#"):
                continue
            if value.startswith("/"):
                issues.append(f"{css.relative_to(SITE)}: site-root CSS asset remains after build: {value}")
                continue
            target = (css.parent / value.split("?", 1)[0].split("#", 1)[0]).resolve()
            if not target.exists():
                issues.append(f"{css.relative_to(SITE)}: unresolved CSS asset: {value}")

    if issues:
        print(f"QA failed with {len(issues)} issue(s):", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print(f"QA passed: {len(html_files)} HTML page(s), {image_count} image reference(s), 0 unresolved local references, 0 duplicate IDs, 0 missing image alt attributes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
