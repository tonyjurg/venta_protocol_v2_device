"""Tests for the combined static documentation site validator."""

import json

import pytest

from scripts.validate_docs import EXPECTED_ROUTES, ROOT, validate_site


def build_site_fixture(site):
    """Create a small combined site using the repository's configured routes."""
    for route in EXPECTED_ROUTES:
        relative = route.strip("/")
        page = site / relative / "index.html" if relative else site / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        if route == "/":
            page.write_text(
                "<html><head><link href='/venta_protocol_v2_device/assets/css/style.css'></head>"
                "<body><a href='/venta_protocol_v2_device/api/'>"
                "Python API reference</a></body></html>",
                encoding="utf-8",
            )
        else:
            page.write_text("<html><body></body></html>", encoding="utf-8")

    stylesheet = site / "assets/css/style.css"
    stylesheet.parent.mkdir(parents=True, exist_ok=True)
    stylesheet.write_text("body { color: #172033; }", encoding="utf-8")

    versions = site / "api/versions/v0.1.2/index.html"
    versions.parent.mkdir(parents=True, exist_ok=True)
    versions.write_text("<html><body></body></html>", encoding="utf-8")
    (site / "api/versions.json").write_text(
        json.dumps(
            [
                {"label": "Current (main)", "path": ".", "revision": "abc123"},
                {
                    "label": "v0.1.2",
                    "path": "versions/v0.1.2",
                    "revision": "def456",
                },
            ]
        ),
        encoding="utf-8",
    )


def test_validate_combined_site_checks_routes_links_and_release_pages(tmp_path):
    """A valid Pages layout has the visible API link and all version targets."""
    build_site_fixture(tmp_path)

    page_count, link_count, versions = validate_site(tmp_path)

    assert page_count == len(EXPECTED_ROUTES) + 1
    assert link_count == 2
    assert versions == ["Current (main)", "v0.1.2"]


def test_validate_combined_site_rejects_broken_local_links(tmp_path):
    """Broken local assets and routes fail the validation step."""
    build_site_fixture(tmp_path)
    homepage = tmp_path / "index.html"
    homepage.write_text(
        "<html><body><a href='/venta_protocol_v2_device/api/'>Python API reference</a>"
        "<a href='/venta_protocol_v2_device/missing/'>Missing page</a></body></html>",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="Broken local link"):
        validate_site(tmp_path)


def test_validate_combined_site_rejects_internal_links_without_pages_baseurl(tmp_path):
    """A root-relative API link must retain the configured Pages base path."""
    build_site_fixture(tmp_path)
    homepage = tmp_path / "index.html"
    homepage.write_text(
        "<html><body><a href='/api/'>Python API reference</a></body></html>",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="omits Pages base path"):
        validate_site(tmp_path)


def test_site_navigation_wraps_and_keeps_touch_targets_on_mobile():
    """The added API nav item remains usable in the responsive site header."""
    css = (ROOT / "docs/assets/css/style.css").read_text(encoding="utf-8")

    assert ".nav-links" in css
    assert "flex-wrap: wrap" in css
    assert "@media (max-width: 640px)" in css
    assert "min-height: 44px" in css
