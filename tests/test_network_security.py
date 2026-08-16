from unittest.mock import MagicMock, patch

import pytest
import requests

from venta_protocol_v2_device import Venta_Protocol_v2_Device


@pytest.mark.parametrize(
    "address",
    ["10.0.0.20", "172.16.0.20", "172.31.255.254", "192.168.1.20"],
)
def test_private_ipv4_addresses_are_accepted(address: str) -> None:
    assert Venta_Protocol_v2_Device(address).IP == address


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "169.254.169.254",
        "192.0.2.10",
        "8.8.8.8",
        "::1",
        "device.example",
        "192.168.1.20:8080",
        "192.168.1.20/path",
    ],
)
def test_non_lan_destinations_are_rejected(address: str) -> None:
    with pytest.raises(ValueError, match="IPv4 address"):
        Venta_Protocol_v2_Device(address)


def test_requests_ignore_environment_credentials_proxies_and_redirects() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = MagicMock(status_code=200)
    response.json.return_value = {}
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    session.post.return_value = response

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        device.getStatus()

    assert session.trust_env is False
    session.post.assert_called_once_with(
        "http://192.168.1.20/datastructure",
        json=None,
        timeout=10,
        allow_redirects=False,
    )


def test_redirect_responses_are_rejected() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = MagicMock(status_code=302)
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    session.post.return_value = response

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        with pytest.raises(requests.TooManyRedirects):
            device.getStatus()


def test_response_ip_cannot_redirect_the_connection() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")

    device._processResponse({"Header": {"IP": "127.0.0.1:8080"}})

    assert device.IP == "127.0.0.1:8080"
    assert device._endpoint.host == "192.168.1.20"
