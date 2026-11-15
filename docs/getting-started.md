---
title: Getting Started
description: Install Venta Protocol V2 Device and read a device on your local network.
permalink: /getting-started/
---

# Getting Started

`venta-protocol-v2-device` controls Venta humidifiers and air washers that use protocol version 2 and expose the `/datastructure` endpoint. You supply the device's IP address; the package does not discover devices automatically.

## Before you begin

- Use a Venta device that supports protocol version 2. The [example notebook]({{ site.github_url }}/blob/main/usage/basic_device_control.ipynb) reports testing with an LW74; this is not a compatibility list for every Venta model.
- Run Python on a machine that can reach the device on your trusted local network.
- Find the device's IPv4 address in your router or access point. A DHCP reservation helps keep it stable.

The constructor accepts addresses in `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Pass the address alone, such as `192.168.1.20`. Hostnames, URLs, ports, IPv6 addresses, and public IPv4 addresses are rejected.

The package metadata declares Python 3.8 or later. Use a maintained Python release; the repository's test workflow currently uses Python 3.12.

## Install

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it with the command for your shell:

| Shell | Command |
| --- | --- |
| Linux/macOS shell | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |

Then install the package:

```bash
python -m pip install venta-protocol-v2-device
```

The package uses `requests`, which pip installs as a dependency. Jupyter is optional and only needed for notebook examples.

## Read the device

Replace the example address with your own device's private IPv4 address:

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.1.20")
status = device.getStatus()
print(status)
print(device.Humidity)
print(device.Temperature)
```

Creating the object validates the address and initializes attributes; it does not contact the device. `getStatus()` makes the network request, returns the parsed response dictionary, and updates recognized attributes on the object.

## Change a setting

After the read example above, you can set a fan speed:

```python
matched = device.setFanSpeed(2)
print("Fan speed matches request:", matched)
```

This command also powers the device on and disables sleep and automatic modes. The value `2` is an example, not a guarantee that every device supports that speed. Consult your device's supported settings and the [User Guide]({{ '/user-guide/' | relative_url }}) before automating controls.

## If the first request fails

Check the IP address, device power, and network reachability. The package communicates over HTTP, rejects redirects, and uses a 10-second Requests timeout. It does not retry failed calls automatically. See [error handling]({{ '/user-guide/#handling-errors' | relative_url }}) for a script that handles connection and response errors.

Protocol version 2 has no transport encryption or authentication. Keep the device on a trusted LAN, do not expose it to the internet, and use addresses from trusted configuration. Read the [network and logging guidance]({{ '/user-guide/#network-security-and-logging' | relative_url }}) before sharing diagnostic output.

Next: explore the [User Guide]({{ '/user-guide/' | relative_url }}) or try the [Examples]({{ '/examples/' | relative_url }}).
