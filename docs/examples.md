---
title: Examples
description: Python examples for reading Venta device state, changing modes, and testing without hardware.
permalink: /examples/
---

# Examples

Install the package using [Getting Started]({{ '/getting-started/' | relative_url }}). Except for the final mocked example, these scripts contact a real device. Replace `192.168.1.20` with your device's trusted private IPv4 address. Control examples change device settings.

## Read a status snapshot

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
response = device.getStatus()
print("Response:", response)
print("Cached humidity:", device.Humidity)
print("Cached fan speed:", device.FanSpeed)
```

The returned dictionary contains the fields supplied in that response. Object attributes retain defaults or earlier values when fields are absent. See [cached state]({{ '/user-guide/#read-device-state' | relative_url }}) before treating them as a fresh measurement.

## Automatic humidity control

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
device.getStatus()
print("Target matches:", device.setTargetHum(50))
print("Automatic mode matches:", device.setAutomatic(True))
```

Enabling automatic mode powers the device on and disables sleep mode. The target is an example; the package validates its type, not the device's supported range. Do not follow this sequence with `setFanSpeed()` if you want automatic mode to remain enabled.

## Manual fan control

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
print("Fan speed matches:", device.setFanSpeed(1))
```

This also powers on and disables automatic and sleep modes. To request sleep mode afterwards, use `device.setSleepMode(True)`; that powers on and disables automatic mode. See [command results]({{ '/user-guide/#command-results' | relative_url }}) for the limitations of boolean return values.

## LED strip controls

For a device that supports these LED settings, the existing notebook demonstrates color strings such as `"#080808"` and mode 3:

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
print("LED enabled:", device.setLEDStripActive(True))
print("LED mode matches:", device.setLEDStripMode(3))
print("LED color matches:", device.setLEDStripColor("#080808"))
```

The implementation requires an integer for the mode. An older notebook cell passes `"3"` as a string; with the current code that raises `TypeError`. The package does not define what each mode means or validate the color format, so verify both against your device.

## Existing notebook

Open [usage/basic_device_control.ipynb]({{ site.github_url }}/blob/main/usage/basic_device_control.ipynb) for the longer guided workflow and sample output. Its introduction reports testing on an LW74. Saved outputs reflect that session and may differ from the current package or your device.

For a local checkout, install the package and JupyterLab from the repository root, then open the notebook:

```bash
python -m pip install -e . jupyterlab
python -m jupyterlab usage/basic_device_control.ipynb
```

Use the notebook kernel for the environment where you installed the package. Replace its `10.0.XX.YY` placeholder with a real private IPv4 address and use the corrected integer LED mode shown above. The notebook intentionally includes an invalid fan-speed argument to demonstrate `TypeError`; running every cell unattended will encounter that example.

## Try a response without hardware

This self-contained example replaces the HTTP session with a mock. It exercises the real status parsing and attribute updates without making a network connection, following the approach used by the repository tests.

```python
from unittest.mock import MagicMock, patch
from venta_protocol_v2_device import Venta_Protocol_v2_Device

response = MagicMock(status_code=200)
response.headers = {}
response.iter_content.return_value = [
    b'{"Action":{"Power":true,"FanSpeed":1},"Measure":{"Humidity":50}}'
]
response.__enter__.return_value = response
session = MagicMock()
session.__enter__.return_value = session
session.post.return_value = response

with patch("venta_protocol_v2_device.requests.Session", return_value=session):
    device = Venta_Protocol_v2_Device("192.168.1.20")
    status = device.getStatus()

assert status["Measure"]["Humidity"] == 50
assert device.Humidity == 50
assert device.Power is True
print("Mock response processed successfully")
```

For application error handling, see the [User Guide]({{ '/user-guide/#handling-errors' | relative_url }}). For the full hardware-free test suite, see [Contributing]({{ '/contributing/#run-tests' | relative_url }}).
