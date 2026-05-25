---
title: Venta Protocol V2 Device
description: A small Python package for controlling Venta air humidifiers and air washers that use protocol version 2.
---

# Venta Protocol V2 Device

[![GitHub repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/tonyjurg/venta_protocol_v2_device) [![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)  [![PyPI Version](https://img.shields.io/pypi/v/venta-protocol-v2-device)](https://pypi.org/project/venta-protocol-v2-device/) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/tonyjurg/venta_protocol_v2_device)

`venta-protocol-v2-device` is a small Python package for controlling Venta air humidifiers and air washers on your local network.

It is made for Venta devices that use **protocol version 2** and expose the `/datastructure` endpoint. You give the package the device IP address, and it lets you read the current status or send simple control commands from Python. If you want to control devices using **protocol version 3**, you can examine [`bobiboy/venta_protocol_v3_device`](https://github.com/bobiboy/venta_protocol_v3_device).

## What This Package Does

This package helps you automate common Venta device actions, including:

- Turning the device on or off
- Enabling or disabling sleep mode
- Enabling or disabling automatic mode
- Changing the fan speed
- Setting the target humidity
- Reading current device status
- Reading sensor values such as temperature, humidity, water level, dust, and fan RPM
- Controlling supported LED strip settings
- Running supported update actions

The package keeps the interface close to `venta_protocol_v3_device`, so code written for Venta protocol v3 devices should feel familiar.

## Who It Is For

This package is useful if you want to:

- Control a Venta device from a Python script
- Include a Venta humidifier or air washer in a home automation workflow
- Read device status for logging or dashboards
- Experiment with Venta protocol version 2 devices on your own network

## Installation

Install the package with pip:

```bash
pip install venta-protocol-v2-device
```

## Quick Example

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

device = Venta_Protocol_v2_Device("192.168.178.87")

status = device.getStatus()
print(status)

device.setPower(True)
device.setFanSpeed(2)
device.setTargetHum(50)
```

Replace `192.168.178.87` with the IP address of your own Venta device.

## Reading Device Data

After calling `getStatus()`, the package stores the returned values on the device object.

```python
device.getStatus()

print(device.Power)
print(device.FanSpeed)
print(device.Humidity)
print(device.Temperature)
print(device.WaterLevel)
```

You can also export the current object state as formatted JSON:

```python
print(device.toJSON())
```

## Supported Commands

The main control methods are:

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

Each method sends a request to the Venta device and returns `True` when the requested value is reflected in the device response.

## Device Discovery

Protocol version 2 devices do not appear to support the same discovery mechanism used by protocol version 3 devices. Because of that, this package does not include automatic discovery.

Use the device IP address directly:

```python
device = Venta_Protocol_v2_Device("192.168.178.87")
```

For reliable automation, it is best to reserve a fixed IP address for the Venta device in your router or access point.

## Notes

- The package communicates with devices over the local network.
- The device must be reachable from the machine running the Python code.
- Network calls can fail if the device is offline, busy, or has changed IP address.
- The package is intended for Venta devices using protocol version 2, not protocol version 3.

## License

This project is released under the MIT License.
