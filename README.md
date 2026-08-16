[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)  [![PyPI Version](https://img.shields.io/pypi/v/venta-protocol-v2-device)](https://pypi.org/project/venta-protocol-v2-device/) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/tonyjurg/venta_protocol_v2_device)

# venta_protocol_v2_device

Small Python library to control Venta Air Humidifiers and Washers that use Protocol Version 2 (i.e., the ones using the `/datastructure` endpoint).

This package intentionally mirrors the public API style of
[`venta_protocol_v3_device`](https://github.com/bobiboy/venta_protocol_v3_device)
so migration/addaptation effort is kept at a minimum.

## Example usage (local; without `pip install`)

```python
import sys
sys.path.insert(0, "../")    # relative to notebook dir
import venta_protocol_v2_device
```

## Example usage (using `pip install`)

```python
!pip install venta_protocol_v2_device
from venta_protocol_v2_device import Venta_Protocol_v2_Device

d = Venta_Protocol_v2_Device("192.168.178.87")
print(d.getStatus())
print(d.toJSON())
```

## Notebook examples

For longer, guided examples in Jupyter notebooks, see [`usage/basic_device_control.ipynb`](usage/basic_device_control.ipynb):

- Basic single-device control workflow.

## Supported control methods

- `setPower(bool)`
- `setSleepMode(bool)`
- `setAutomatic(bool)`
- `setFanSpeed(int)`
- `setTargetHum(int)`
- `setLEDStripActive(bool)`
- `setLEDStripMode(int)`
- `setLEDStripColor(str)`
- `setPowerMode(str)`
- `runUpdate(str)`

## Discovery

Based on analyzing sniffed UDP packets, it looks like discovery as found in protocol version `3.0` is not supported for protocol version `2.0` devices. Hence it is not included in this package. Instead use the device IP address directly:

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

d = Venta_Protocol_v2_Device("192.168.178.87")
```

If you need stable addressing, configure a DHCP reservation for the Venta device in your router or access point.

## Network security

Use this package only on a trusted local-area network and in a friendly environment. Venta protocol version 2 communicates over unauthenticated, unencrypted HTTP, so commands and telemetry can be observed or modified by anyone able to intercept local traffic.

- Do not expose the Venta device directly to the internet.
- Restrict device access to trusted hosts, preferably on an isolated home-automation network or VLAN.
- Pass only a private IPv4 address that comes from trusted configuration; never accept a device address directly from an untrusted user or request.
- Treat all device responses as untrusted network data.

## Logging and privacy

Debug logging includes request payloads and complete device responses. These records can contain control actions, sensor telemetry, device identifiers, and MAC addresses. Enable debug logging only on a trusted LAN and in a friendly environment. Protect log files from unauthorized access, retain them only as long as necessary, and redact sensitive values before sharing logs publicly.

## Corrections and/or Additions

Please feel free to raise issues or create pull request for corrections and/or additions.
