"""Build versioned Sphinx API docs from this checkout and published releases."""

import argparse
import hashlib
import html.parser
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "tonyjurg/venta_protocol_v2_device"


class VersionOptions(html.parser.HTMLParser):
    """Collect options from the rendered Sphinx version selector."""

    def __init__(self):
        super().__init__()
        self.options = []

    def handle_starttag(self, tag, attrs):
        if tag == "option":
            self.options.append(dict(attrs))


def git(*args):
    """Run Git against the checkout containing this script."""
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def release_tags():
    """Return published GitHub release tags, newest first."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "venta-protocol-v2-api-docs",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    releases = []
    page = 1
    while True:
        request = Request(
            f"https://api.github.com/repos/{REPOSITORY}/releases"
            f"?per_page=100&page={page}",
            headers=headers,
        )
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        releases.extend(
            release
            for release in batch
            if not release.get("draft") and release.get("published_at")
        )
        if len(batch) < 100:
            break
        page += 1

    releases.sort(key=lambda release: release["published_at"], reverse=True)
    return list(dict.fromkeys(release["tag_name"] for release in releases))


def tag_directory(tag):
    """Keep normal version tags readable and map unusual names safely."""
    if re.fullmatch(r"v?\d+(?:\.\d+)+(?:[-.][A-Za-z0-9.-]+)?", tag):
        return tag
    return "tag-" + hashlib.sha256(tag.encode("utf-8")).hexdigest()[:16]


def verify_selector(page, entries, selected_output):
    """Fail if a rendered selector is missing, incorrect, or links nowhere."""
    parser = VersionOptions()
    parser.feed(page.read_text(encoding="utf-8"))

    expected = [(entry["output"] / "index.html").resolve() for entry in entries]
    actual = [
        (page.parent / option["value"]).resolve()
        for option in parser.options
        if option.get("value")
    ]
    if actual != expected or any(not target.is_file() for target in actual):
        raise RuntimeError(f"Broken API version selector in {page}")

    selected_links = [
        target
        for target, option in zip(actual, parser.options)
        if "selected" in option
    ]
    if selected_links != [(selected_output / "index.html").resolve()]:
        raise RuntimeError(f"Incorrect selected API version in {page}")


def build(source, docs, output, python, label, entries):
    """Build one source revision with links to every version's landing page."""
    choices = [
        {
            "label": entry["label"],
            "relative_url": Path(
                os.path.relpath(entry["output"] / "index.html", output / "_static")
            ).as_posix(),
        }
        for entry in entries
    ]
    environment = {
        **os.environ,
        "VENTA_DOCS_SOURCE": str(source),
        "VENTA_DOCS_VERSION": label,
        "VENTA_DOCS_VERSIONS": json.dumps(choices),
    }
    subprocess.run(
        [
            str(python),
            "-m",
            "sphinx",
            "-E",
            "-W",
            "--keep-going",
            "-b",
            "html",
            str(docs),
            str(output),
        ],
        env=environment,
        check=True,
    )


def extract_tag(tag, destination):
    """Extract a release revision without creating another Git checkout."""
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", tag], cwd=ROOT
    )
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as source_archive:
        source_archive.extractall(destination, filter="data")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".cache/pages-site/api"),
        help="Sphinx output directory (default: .cache/pages-site/api)",
    )
    parser.add_argument(
        "--current-only",
        action="store_true",
        help="Build the current checkout without querying GitHub releases.",
    )
    parser.add_argument(
        "--release-tag",
        action="append",
        default=[],
        help="Build a specific local tag instead of looking up GitHub releases; repeat as needed.",
    )
    args = parser.parse_args()

    if args.current_only and args.release_tag:
        parser.error("--current-only cannot be combined with --release-tag")

    output = args.output.resolve()
    if output == ROOT or output in ROOT.parents:
        parser.error("--output must not be the repository root or one of its parents")

    tags = [] if args.current_only else (args.release_tag or release_tags())
    known_tags = set(git("tag", "--list").splitlines())
    missing_tags = [tag for tag in tags if tag not in known_tags]
    if missing_tags:
        raise RuntimeError(
            "Release tag(s) missing from this checkout: " + ", ".join(missing_tags)
        )

    entries = [
        {
            "label": "Current (main)",
            "output": output,
            "revision": git("rev-parse", "HEAD"),
            "tag": None,
        }
    ]
    entries.extend(
        {
            "label": tag,
            "output": output / "versions" / tag_directory(tag),
            "revision": git("rev-parse", f"refs/tags/{tag}^{{commit}}"),
            "tag": tag,
        }
        for tag in tags
    )

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    build(ROOT, ROOT / "docs/api", output, Path(sys.executable), entries[0]["label"], entries)

    for entry in entries[1:]:
        temporary_root = os.environ.get("VENTA_DOCS_TMPDIR")
        with tempfile.TemporaryDirectory(
            prefix="venta-api-", dir=temporary_root
        ) as temporary:
            workspace = Path(temporary)
            source = workspace / "source"
            extract_tag(entry["tag"], source)

            # These tags predate the Sphinx setup; reuse the current Sphinx
            # source while pointing autodoc at the historical package source.
            docs = workspace / "docs"
            shutil.copytree(ROOT / "docs/api", docs)
            build(source, docs, entry["output"], Path(sys.executable), entry["label"], entries)

    for entry in entries:
        if not (entry["output"] / "index.html").is_file():
            raise RuntimeError(f"Missing API documentation for {entry['label']}")
        for page in entry["output"].rglob("*.html"):
            if entry is entries[0] and (output / "versions") in page.parents:
                continue
            verify_selector(page, entries, entry["output"])

    manifest = [
        {
            "label": entry["label"],
            "path": entry["output"].relative_to(output).as_posix(),
            "revision": entry["revision"],
        }
        for entry in entries
    ]
    (output / "versions.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
