# venta_protocol_v2_device

Small Python library to control Venta Air Humidifiers and Washers that use Protocol Version 2 (i.e., the ones using the `/datastructure` endpoint).

This package intentionally mirrors the public API style of
[`venta_protocol_v3_device`](https://github.com/bobiboy/venta_protocol_v3_device)
so migration/addaptation effort is kept at a minimum.

## Example usage (without `pip install`)

```python
import sys
sys.path.insert(0, "../../")    # relative to notebook dir
import venta_protocol_v2_device
```

## Example usage (once `pip install` is functioning)

```python
from venta_protocol_v2_device import Venta_Protocol_v2_Device

d = Venta_Protocol_v2_Device("192.168.178.87")
print(d.getStatus())
print(d.toJSON())
```


## Notebook examples

For longer, guided examples in Jupyter notebooks, see [`examples/notebooks`](examples/notebooks/README.md):

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

## Corrections and/or Additions

Please feel free to raise issues or create pull request for corrections and/or additions.
