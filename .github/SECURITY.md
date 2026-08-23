# Security Policy

## Supported Versions

Security fixes are provided for the latest published release.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| Older releases | No |

Before reporting a vulnerability, please confirm that it is reproducible with
the latest release or the current `main` branch.

## Reporting a Vulnerability

Please do not disclose suspected vulnerabilities in a public issue, discussion,
pull request, or other public channel.

Report vulnerabilities privately through GitHub's
[security advisory form](https://github.com/tonyjurg/venta_protocol_v2_device/security/advisories/new).
If that option is unavailable, open a public issue asking the maintainer to
establish a private contact channel, but do not include vulnerability details
in that issue.

Include as much of the following information as possible:

- The affected package version or commit.
- A description of the vulnerability and its potential impact.
- Reproduction steps or a minimal proof of concept.
- Relevant device, network, operating-system, and Python-version details.
- Any suggested mitigation or remediation.

The maintainer aims to acknowledge a report within 7 calendar days and provide
an initial assessment or status update within 14 calendar days. Valid reports
will be handled through coordinated disclosure. Please allow reasonable time
for a fix and release before publishing technical details.

## Security Considerations

This package controls physical devices over a local network. Venta protocol v2
uses unauthenticated, unencrypted HTTP, so the protocol does not protect the
confidentiality or integrity of commands and telemetry.

Users should:

- Run the package and device only on a trusted, appropriately isolated network.
- Avoid exposing the device directly to the internet.
- Restrict network access to hosts that are authorized to control the device.
- Treat device responses as untrusted network input.
- Avoid passing device addresses obtained from untrusted users or requests.
- Keep this package and its dependencies updated.

Reports showing that the library makes these protocol limitations materially
worse, bypasses an expected protection, or allows an impact beyond the device
itself are welcome.

## Good-Faith Research

Please act in good faith, avoid privacy violations and service disruption, and
test only against systems and devices you own or are authorized to assess.
