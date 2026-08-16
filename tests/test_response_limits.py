from unittest.mock import MagicMock, patch
from typing import Dict, List, Optional

import pytest

from venta_protocol_v2_device import Venta_Protocol_v2_Device


def _response(chunks: List[bytes], headers: Optional[Dict[str, str]] = None) -> MagicMock:
    response = MagicMock()
    response.headers = headers or {}
    response.iter_content.return_value = chunks
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


def test_valid_bounded_response_is_processed() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response([b'{"Action":{"Power":true}}'])

    with patch("venta_protocol_v2_device.requests.post", return_value=response) as post:
        result = device.getStatus()

    assert result == {"Action": {"Power": True}}
    assert device.Power is True
    post.assert_called_once_with(
        "http://192.168.1.20/datastructure",
        json=None,
        timeout=10,
        stream=True,
    )


def test_oversized_declared_response_is_rejected_before_reading() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response(
        [b"{}"],
        {"Content-Length": str(device._MAX_RESPONSE_BYTES + 1)},
    )

    with patch("venta_protocol_v2_device.requests.post", return_value=response):
        with pytest.raises(ValueError, match="exceeds"):
            device.getStatus()

    response.iter_content.assert_not_called()


def test_oversized_streamed_response_is_rejected() -> None:
    device = Venta_Protocol_v2_Device("192.168.1.20")
    response = _response([b"x" * device._MAX_RESPONSE_BYTES, b"x"])

    with patch("venta_protocol_v2_device.requests.post", return_value=response):
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

    with patch("venta_protocol_v2_device.requests.post", return_value=response):
        with pytest.raises(ValueError, match=message):
            device.getStatus()
