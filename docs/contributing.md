---
title: Contributing
description: Set up a development checkout, run hardware-free tests, and propose documentation or code changes.
permalink: /contributing/
---

# Contributing

Corrections, examples, and code improvements are welcome. Use [GitHub issues]({{ site.github_url }}/issues) to report a problem or discuss a change, and submit a pull request for review. The project is distributed under the [MIT License]({{ site.github_url }}/blob/main/LICENSE).

## Set up a checkout

Fork the repository if you do not have push access. Clone your fork, or clone the project to inspect and test it locally:

```bash
git clone https://github.com/tonyjurg/venta_protocol_v2_device.git
cd venta_protocol_v2_device
python -m venv .venv
```

Activate the environment using the [command for your shell]({{ '/getting-started/#install' | relative_url }}), then install the package in editable mode and the test dependency:

```bash
python -m pip install -e . pytest
```

Editable installation makes imports use your checkout. `pytest` is a development dependency, not a package runtime requirement. CI currently tests on Python 3.12; the package metadata declares Python 3.8 or later, so preserve that compatibility when proposing implementation changes.

## Run tests

From the repository root:

```bash
python -m pytest
```

The existing tests use mocked HTTP sessions and synthetic responses. They do not need Venta hardware and do not contact a device.

| Test file | Coverage |
| --- | --- |
| `tests/test_network_security.py` | Private IPv4 destinations, environment isolation, redirects, and connection-address protection |
| `tests/test_response_security.py` | Recognized fields, unknown-field isolation, and response type checks |
| `tests/test_response_limits.py` | Response size limits, JSON parsing, and response shape |

For behavior changes, add focused tests for the affected behavior and run the suite. Use synthetic responses with no real device identifiers. Do not run the hardware notebook as an automated test; its cells can change device settings and include intentional errors.

## Report a problem

Include the package version, Python version, device model, relevant firmware version if known, the expected result, and the actual result. Provide a small reproduction and say whether it was tested with hardware or a mock. You can find the installed package version with:

```bash
python -m pip show venta-protocol-v2-device
```

Before posting logs, notebook output, or JSON dumps, remove IP and MAC addresses, device identifiers, and private telemetry. Debug logs contain complete payloads and responses. See [logging guidance]({{ '/user-guide/#network-security-and-logging' | relative_url }}).

## Update documentation

The project pages live in `docs/` and use Jekyll with a shared layout. Each page declares its title, description, and permalink in YAML front matter. Navigation is maintained in `docs/_data/navigation.yml`.

Use Jekyll's `relative_url` filter for internal links so they include `/venta_protocol_v2_device/` on GitHub Pages. Keep existing page URLs and heading anchors working when moving content. Verify method names, argument types, and examples against the Python implementation; label device-specific observations rather than presenting them as universal protocol guarantees.

The website does not execute code examples during its build. Keep documentation dependencies separate from runtime dependencies and make examples testable with mocks. The Jekyll configuration reserves `docs/api/` for a separately built API reference; the Sphinx setup and local combined-build instructions are deferred to the later documentation PRs.

## Submit a pull request

Create a focused branch, describe the problem and resulting behavior, and include the checks you ran. State any hardware-specific assumptions or validation gaps. Preserve the public API and security checks unless the change explicitly addresses them.

The current [test workflow]({{ site.github_url }}/blob/main/.github/workflows/tests.yml) runs for pull requests to `main` and `development`. Passing package tests does not validate the Jekyll build. The existing Pages workflow deploys documentation changes after a merge to `main`; report documentation build results separately when reviewing a documentation change.

Package publication is handled by `publish.yml`, independently of website deployment. A documentation pull request should not publish a package or create a release.
