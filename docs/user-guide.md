---
title: User Guide
description: Read device state, control settings, and handle Venta protocol V2 responses.
permalink: /user-guide/
---

# User Guide

Start with [Getting Started]({{ '/getting-started/' | relative_url }}) for installation and network requirements. The methods below belong to `Venta_Protocol_v2_Device`.

## Read device state

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
response = device.getStatus()
print(response)
print(device.Power, device.FanSpeed, device.Humidity)
```

`getStatus()` returns the device's response dictionary. Recognized fields from nested sections also update attributes on the object. The [existing notebook]({{ site.github_url }}/blob/main/usage/basic_device_control.ipynb) shows `Header`, `Action`, `Info`, and `Measure` sections.

| Data | Example attributes |
| --- | --- |
| Identity and status | `DeviceType`, `MacAdress`, `ProtocolV`, `Status` |
| Controls | `Power`, `FanSpeed`, `TargetHum`, `SleepMode`, `Automatic` |
| Lighting | `LEDStripActive`, `LEDStripMode`, `LEDStrip`, `BaLiNormal`, `BaLiSleep`, `BaLiStandby` |
| Firmware and maintenance | `SWMain`, `SWWIFI`, `ServiceT`, `OperationT`, `Warnings` |
| Measurements | `Temperature`, `Humidity`, `Dust`, `WaterLevel`, `FanRpm`, `FanRpm2` |

Attribute spelling follows the protocol, including `MacAdress`. Values are stored as received, without sensor-unit conversion. Do not assume that a field such as `WaterLevel` is a percentage, or that every device supplies every field.

Attributes start at `0`, `False`, or an empty string. Fields omitted from a later response keep their previous values. A value on the object is therefore cached state, not proof that the latest response included that field. For freshness-sensitive decisions, inspect the returned dictionary and the fields it actually contains.

`DaysToService` is an estimate calculated when `ServiceT > 0`: it assumes a 180-day service interval and treats `ServiceT` as elapsed minutes, rounds remaining days up, and clamps at zero. It is not a service interval reported by the device. When `ServiceT` is zero, the calculation is skipped and `DaysToService` retains its previous value.

## Control settings

Commands are synchronous network calls. The following table describes the payload each method sends, including changes to other settings.

| Method | Argument | Requested changes |
| --- | --- | --- |
| `setPower(target)` | `bool` | `False` sends power off. `True` also disables sleep and automatic modes and sets fan speed to at least 1, using the cached speed. |
| `setAutomatic(target)` | `bool` | Powers on, disables sleep, and sets automatic mode. |
| `setSleepMode(target)` | `bool` | Powers on, disables automatic mode, and sets sleep mode. |
| `setFanSpeed(target)` | `int` | Powers on, disables sleep and automatic modes, and sets fan speed. |
| `setTargetHum(target)` | `int` | Sets target humidity without changing modes. |
| `setLEDStripActive(target)` | `bool` | Enables or disables the LED strip. |
| `setLEDStripMode(mode)` | `int` | Sends the LED strip mode. |
| `setLEDStripColor(color)` | `str` | Sends the color as the `LEDStrip` field. |
| `setPowerMode(mode)` | `str` | Sends the protocol's lowercase `mode` field. |
| `runUpdate(updateAction)` | `str` | Sends the protocol's `Update` field. |

Types must match exactly: use `True` rather than `1` for a boolean, and `3` rather than `"3"` for an integer. Boolean values are also rejected where an integer is required. The package does not validate supported numeric ranges, color syntax, mode names, or update action names. Those depend on the device; the implementation does not define an authoritative list.

For automatic humidity control, set a target and then enable automatic mode. Calling `setFanSpeed()` afterwards would disable it. See the [control examples]({{ '/examples/#automatic-humidity-control' | relative_url }}).

### Command results

Most setters return whether the corresponding cached attribute equals the requested value after processing the response. `False` means that comparison did not match; network or validation failures raise exceptions instead. A `True` result can reflect a previous value if the response omits the relevant field, so it is not an independent acknowledgement of a physical change.

`setPowerMode()` and `runUpdate()` have different semantics: they return `True` if the response dictionary contains an `Action` key. They do not verify the selected mode or completion of an update. Use only action strings whose meaning you have verified for your device, and avoid automatically retrying update actions after an uncertain result.

## Export cached state

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
device.getStatus()
print(device.toJSON())
```

`toJSON()` returns a sorted, indented JSON string of the object's attributes. It makes no network call and is not the original response: it includes defaults, derived state, the IP address, and internal connection state. Treat this as diagnostic output rather than a stable interchange format. For a dashboard or data export, select the fields you need explicitly.

## Handling errors

```python
import requests
from venta_protocol_v2_device import Venta_Protocol_v2_Device

try:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = device.getStatus()
except requests.RequestException as exc:
    print("Device request failed:", exc)
except (TypeError, ValueError) as exc:
    print("Invalid configuration or device response:", exc)
else:
    print("Device response:", response)
```

- `TypeError` can indicate an incorrect argument type or a recognized response field with an unexpected type.
- `ValueError` can indicate an invalid address, malformed JSON, a non-object JSON response, an invalid or oversized response length, or excessive nesting.
- Requests exceptions cover connection failures, timeouts, HTTP error statuses, and rejected redirects.

The request uses `timeout=10`, which is a Requests connection/read timeout rather than a total wall-clock deadline. The package has no automatic retry loop. If you add retries, keep them bounded and consider whether repeating the command is appropriate.

Response updates are not transactional: a type or nesting error can occur after earlier fields have been assigned. After a failed call, do not treat cached attributes as a complete fresh snapshot.

## Network security and logging

Use the package only on a trusted local network. Protocol V2 uses unauthenticated, unencrypted HTTP. Restrict access to trusted hosts, preferably on an isolated home-automation network or VLAN, and never expose the device directly to the internet. Obtain the IP address from trusted configuration, not directly from an untrusted user or request.

Each call uses a Requests session with environment-derived proxies and credentials disabled. Redirects are rejected. Responses are limited to 256 KiB and only recognized, correctly typed fields can update device attributes. These checks do not make an untrusted network safe.

Debug logging includes request payloads and full parsed responses. Logs and JSON dumps can reveal device identifiers, MAC addresses, IP addresses, control actions, and sensor telemetry. Restrict access, retain logs only as long as needed, and redact them before sharing.

For implementation details, continue to [Architecture]({{ '/architecture/' | relative_url }}).
