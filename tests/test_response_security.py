import pytest

from venta_protocol_v2_device import Venta_Protocol_v2_Device


def test_known_response_fields_are_updated() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")

    device._processResponse(
        {
            "Header": {"ProtocolV": "2.0", "Status": "ok"},
            "Action": {"Power": True, "FanSpeed": 2},
            "Info": {"ServiceT": 1440},
        }
    )

    assert device.ProtocolV == "2.0"
    assert device.Status == "ok"
    assert device.Power is True
    assert device.FanSpeed == 2
    assert device.DaysToService == 179


def test_unknown_response_fields_cannot_clobber_device_state_or_methods() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    original_make_call = device._makeCall

    device._processResponse(
        {
            "Header": {"IP": "127.0.0.1:8080"},
            "getStatus": "disabled",
            "_makeCall": "disabled",
            "__class__": "disabled",
        }
    )

    assert device.IP == "192.168.1.20"
    assert callable(device.getStatus)
    assert device._makeCall == original_make_call
    assert device.__class__ is Venta_Protocol_v2_Device


def test_invalid_known_response_field_type_is_rejected() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")

    with pytest.raises(TypeError, match="Invalid response property FanSpeed"):
        device._processResponse({"Action": {"FanSpeed": "3"}})

    assert device.FanSpeed == 0
