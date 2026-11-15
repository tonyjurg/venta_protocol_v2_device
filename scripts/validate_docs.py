"""Check the combined Jekyll and Sphinx output for broken local links."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse, urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROUTES = (
    "/",
    "/getting-started/",
    "/user-guide/",
    "/architecture/",
    "/examples/",
    "/contributing/",
    "/api/",
)


class PageLinks(HTMLParser):
    """Collect local-reference attributes and the text of links on a page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.anchors = []
        self._anchor = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for name in ("href", "src"):
            value = attributes.get(name)
            if value:
                self.references.append(value.strip())
        if tag == "a":
            self._anchor = {"href": attributes.get("href", ""), "text": []}

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == "a":
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._anchor is not None:
            self._anchor["text"] = " ".join(" ".join(self._anchor["text"]).split())
            self.anchors.append(self._anchor)
            self._anchor = None


class PageAnchors(HTMLParser):
    """Collect fragment targets from a rendered HTML page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for name in ("id", "name"):
            if attributes.get(name):
                self.anchors.add(attributes[name])


def site_settings(config_path):
    """Read the simple Jekyll URL and baseurl scalar settings."""
    settings = {}
    for line in config_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(url|baseurl):\s*(.*?)\s*(?:#.*)?$", line)
        if match:
            settings[match.group(1)] = match.group(2).strip().strip("\"'")
    if "url" not in settings or "baseurl" not in settings:
        raise RuntimeError(f"Could not read url and baseurl from {config_path}")
    return settings["url"].rstrip("/"), settings["baseurl"].rstrip("/")


def link_target(reference, page, site_root, site_host, baseurl):
    """Resolve a local URL to a file under the combined site directory."""
    parsed = urlsplit(reference)
    if parsed.scheme and parsed.scheme.lower() not in ("http", "https", "file"):
        return None, parsed.fragment
    if parsed.netloc and parsed.hostname != site_host:
        return None, parsed.fragment
    if parsed.scheme in ("http", "https") and parsed.hostname != site_host:
        return None, parsed.fragment

    path = unquote(parsed.path)
    root = site_root.resolve()
    if path.startswith("/"):
        if baseurl:
            if path == baseurl:
                path = "/"
            elif path.startswith(baseurl + "/"):
                path = path[len(baseurl):]
            else:
                raise RuntimeError(
                    f"Root-relative link omits Pages base path {baseurl}: {reference} ({page})"
                )
        target = (root / path.lstrip("/"))
    else:
        target = page.parent / path if path else page

    target = target.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"Link escapes the site output: {reference} ({page})") from exc

    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    elif not target.suffix and not target.exists() and (target / "index.html").is_file():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def page_links(path):
    """Parse a page's references and visible link labels."""
    parser = PageLinks()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def anchors_for(path, cache):
    """Return HTML fragment IDs, parsing each linked page only once."""
    if path not in cache:
        parser = PageAnchors()
        parser.feed(path.read_text(encoding="utf-8"))
        cache[path] = parser.anchors
    return cache[path]


def validate_site(site_root):
    """Check expected pages, release output, local URLs, and anchor targets."""
    site_root = site_root.resolve()
    if not site_root.is_dir():
        raise RuntimeError(f"Site output directory does not exist: {site_root}")

    site_url, baseurl = site_settings(ROOT / "docs/_config.yml")
    site_host = urlparse(site_url).hostname

    for route in EXPECTED_ROUTES:
        route_path = route.strip("/")
        target = site_root / route_path / "index.html" if route_path else site_root / "index.html"
        if not target.is_file():
            raise RuntimeError(f"Missing built page for route {route}: {target}")

    homepage = page_links(site_root / "index.html")
    api_link = any(
        link["text"].casefold() == "python api reference"
        and link_target(link["href"], site_root / "index.html", site_root, site_host, baseurl)[0]
        == (site_root / "api/index.html").resolve()
        for link in homepage.anchors
    )
    if not api_link:
        raise RuntimeError("Homepage must show a Python API reference link to /api/")

    manifest_path = site_root / "api/versions.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Missing API release manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest or manifest[0].get("label") != "Current (main)":
        raise RuntimeError("API release manifest must start with Current (main)")
    labels = [entry.get("label") for entry in manifest]
    if len(set(labels)) != len(labels):
        raise RuntimeError("API release manifest contains duplicate version labels")
    for entry in manifest:
        relative_path = Path(entry.get("path", ""))
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise RuntimeError(f"Unsafe API version path in manifest: {entry}")
        api_page = site_root / "api" / relative_path / "index.html"
        if not api_page.is_file():
            raise RuntimeError(f"Missing API page for {entry.get('label')}: {api_page}")

    anchor_cache = {}
    checked_links = 0
    pages = sorted(site_root.rglob("*.html"))
    for page in pages:
        for reference in page_links(page).references:
            target, fragment = link_target(
                reference, page, site_root, site_host, baseurl
            )
            if target is None:
                continue
            if not target.is_file():
                raise RuntimeError(f"Broken local link: {reference} ({page})")
            if fragment and target.suffix.lower() in (".html", ".htm"):
                if fragment not in anchors_for(target, anchor_cache):
                    raise RuntimeError(
                        f"Broken fragment #{fragment}: {reference} ({page})"
                    )
            checked_links += 1

    return len(pages), checked_links, labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site",
        type=Path,
        default=Path(".cache/pages-site"),
        help="Combined Jekyll and Sphinx output directory.",
    )
    args = parser.parse_args()
    page_count, link_count, versions = validate_site(args.site)
    print(
        f"Validated {page_count} HTML pages and {link_count} local links; "
        f"API versions: {', '.join(versions)}."
    )


if __name__ == "__main__":
    main()
