from unittest.mock import MagicMock, patch
from typing import Dict, List, Optional

import pytest

from venta_protocol_v2_device import Venta_Protocol_v2_Device


def _response(chunks: List[bytes], headers: Optional[Dict[str, str]] = None) -> MagicMock:
    response = MagicMock()
    response.status_code = 200
    response.headers = headers or {}
    response.iter_content.return_value = chunks
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


def _session(response: MagicMock) -> MagicMock:
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    session.post.return_value = response
    return session


def test_valid_bounded_response_is_processed() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response([b'{"Action":{"Power":true}}'])
    session = _session(response)

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        result = device.getStatus()

    assert result == {"Action": {"Power": True}}
    assert device.Power is True
    assert session.trust_env is False
    session.post.assert_called_once_with(
        "http://192.168.1.20/datastructure",
        json=None,
        timeout=10,
        allow_redirects=False,
        stream=True,
    )


def test_oversized_declared_response_is_rejected_before_reading() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response(
        [b"{}"],
        {"Content-Length": str(device._MAX_RESPONSE_BYTES + 1)},
    )
    session = _session(response)

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        with pytest.raises(ValueError, match="exceeds"):
            device.getStatus()

    response.iter_content.assert_not_called()


def test_oversized_streamed_response_is_rejected() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response([b"x" * device._MAX_RESPONSE_BYTES, b"x"])
    session = _session(response)

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        with pytest.raises(ValueError, match="exceeds"):
            device.getStatus()


@pytest.mark.parametrize(
    "chunks, message",
    [
        ([b"not-json"], "invalid JSON"),
        ([b"[]"], "must be a JSON object"),
    ],
)
def test_invalid_response_shape_is_rejected(chunks: List[bytes], message: str) -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response(chunks)
    session = _session(response)

    with patch("venta_protocol_v2_device.requests.Session", return_value=session):
        with pytest.raises(ValueError, match=message):
            device.getStatus()
