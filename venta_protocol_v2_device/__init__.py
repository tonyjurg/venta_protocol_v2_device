import json
import logging
import math
from dataclasses import dataclass
from ipaddress import IPv4Address, ip_address, ip_network
from typing import Any, Dict, Optional

import requests


_PRIVATE_IPV4_NETWORKS = (
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
)


@dataclass(frozen=True)
class _DeviceEndpoint:
    host: str


class Venta_Protocol_v2_Device:
    """Class representing a Venta device that uses protocol version 2.0.

    This library mirrors the public API style of venta_protocol_v3_device as closely as possible,
    while adapting request/response handling to the V2 endpoint (/datastructure).
    """

    _RESPONSE_FIELD_TYPES = {
        "DeviceType": int,
        "MacAdress": str,
        "ProtocolV": str,
        "Status": str,
        "Power": bool,
        "FanSpeed": int,
        "TargetHum": int,
        "SleepMode": bool,
        "Automatic": bool,
        "BaLiNormal": int,
        "BaLiSleep": int,
        "BaLiStandby": int,
        "LEDStripActive": bool,
        "LEDStripMode": int,
        "LEDStrip": str,
        "SWMain": str,
        "SWWIFI": str,
        "OperationT": int,
        "DiscIonT": int,
        "CleaningT": int,
        "FilterT": int,
        "ServiceT": int,
        "HwIndexMB": int,
        "HwIndexOption": int,
        "Warnings": int,
        "Temperature": int,
        "Humidity": int,
        "Dust": int,
        "WaterLevel": int,
        "FanRpm": int,
        "FanRpm2": int,
    }

    _MAX_RESPONSE_BYTES = 256 * 1024

    def __init__(self, IP: str):
        validated_ip = self._validate_device_ip(IP)
        self._endpoint = _DeviceEndpoint(validated_ip)
        self.IP: str = validated_ip

        # Header
        self.DeviceType: int = 0
        self.MacAdress: str = ""
        self.ProtocolV: str = ""
        self.Status: str = ""

        # Action
        self.Power: bool = False
        self.FanSpeed: int = 0
        self.TargetHum: int = 0
        self.SleepMode: bool = False
        self.Automatic: bool = False
        self.BaLiNormal: int = 0
        self.BaLiSleep: int = 0
        self.BaLiStandby: int = 0
        self.LEDStripActive: bool = False
        self.LEDStripMode: int = 0
        self.LEDStrip: str = ""

        # Info
        self.SWMain: str = ""
        self.SWWIFI: str = ""
        self.OperationT: int = 0
        self.DiscIonT: int = 0
        self.CleaningT: int = 0
        self.FilterT: int = 0
        self.ServiceT: int = 0
        self.HwIndexMB: int = 0
        self.HwIndexOption: int = 0
        self.Warnings: int = 0

        # Measure
        self.Temperature: int = 0
        self.Humidity: int = 0
        self.Dust: int = 0
        self.WaterLevel: int = 0
        self.FanRpm: int = 0
        self.FanRpm2: int = 0

        # Derived
        self.DaysToService: int = 0

    def getStatus(self) -> Dict[str, Any]:
        return self._makeCall("/datastructure")

    def setAutomatic(self, target: bool) -> bool:
        target = self._require_bool("target", target)
        self._setAction({"Power": True, "SleepMode": False, "Automatic": target})
        return self.Automatic == target

    def setSleepMode(self, target: bool) -> bool:
        target = self._require_bool("target", target)
        self._setAction({"Power": True, "SleepMode": target, "Automatic": False})
        return self.SleepMode == target

    def setFanSpeed(self, target: int) -> bool:
        target = self._require_int("target", target)
        self._setAction({"Power": True, "SleepMode": False, "Automatic": False, "FanSpeed": target})
        return self.FanSpeed == target

    def setTargetHum(self, target: int) -> bool:
        target = self._require_int("target", target)
        self._setAction({"TargetHum": target})
        return self.TargetHum == target

    def setPower(self, target: bool) -> bool:
        target = self._require_bool("target", target)
        if target:
            self._setAction({"Power": True, "SleepMode": False, "Automatic": False, "FanSpeed": max(self.FanSpeed, 1)})
        else:
            self._setAction({"Power": False})
        return self.Power == target

    def setLEDStripActive(self, target: bool) -> bool:
        target = self._require_bool("target", target)
        self._setAction({"LEDStripActive": target})
        return self.LEDStripActive == target

    def setLEDStripMode(self, mode: int) -> bool:
        mode = self._require_int("mode", mode)
        self._setAction({"LEDStripMode": mode})
        return self.LEDStripMode == mode

    def setLEDStripColor(self, color: str) -> bool:
        color = self._require_str("color", color)
        self._setAction({"LEDStrip": color})
        return self.LEDStrip == color

    def setPowerMode(self, mode: str) -> bool:
        mode = self._require_str("mode", mode)
        response = self._setAction({"mode": mode})
        return "Action" in response

    def runUpdate(self, updateAction: str) -> bool:
        updateAction = self._require_str("updateAction", updateAction)
        response = self._setAction({"Update": updateAction})
        return "Action" in response

    @staticmethod
    def _require_bool(name: str, value: Any) -> bool:
        if type(value) is not bool:
            raise TypeError(f"{name} must be bool, got {type(value).__name__}")
        return value

    @staticmethod
    def _require_int(name: str, value: Any) -> int:
        if type(value) is not int:
            raise TypeError(f"{name} must be int, got {type(value).__name__}")
        return value

    @staticmethod
    def _require_str(name: str, value: Any) -> str:
        if type(value) is not str:
            raise TypeError(f"{name} must be str, got {type(value).__name__}")
        return value

    @staticmethod
    def _validate_device_ip(value: Any) -> str:
        if type(value) is not str:
            raise TypeError(f"IP must be str, got {type(value).__name__}")

        try:
            address = ip_address(value)
        except ValueError as exc:
            raise ValueError("IP must be a valid private IPv4 address") from exc

        if not isinstance(address, IPv4Address) or not any(
            address in network for network in _PRIVATE_IPV4_NETWORKS
        ):
            raise ValueError("IP must be a private IPv4 address used on the local network")

        return str(address)

    def _setAction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._makeCall("/datastructure", {"Action": payload})

    def _makeCall(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        connection = self._endpoint
        if not isinstance(connection, _DeviceEndpoint):
            raise RuntimeError("Device connection state is invalid")

        url = f"http://{connection.host}{endpoint}"
        logging.debug("Sending payload to endpoint %s: %s", url, payload)
        with requests.Session() as session:
            session.trust_env = False
            with session.post(
                url,
                json=payload,
                timeout=10,
                allow_redirects=False,
                stream=True,
            ) as response:
                if 300 <= response.status_code < 400:
                    raise requests.TooManyRedirects(
                        "Device responses must not redirect requests"
                    )

                response.raise_for_status()
                obj = self._readResponseJSON(response)

        self._processResponse(obj)
        return obj

    def _readResponseJSON(self, response: requests.Response) -> Dict[str, Any]:
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError as exc:
                raise ValueError("Device returned an invalid Content-Length header") from exc

            if declared_length < 0 or declared_length > self._MAX_RESPONSE_BYTES:
                raise ValueError(
                    f"Device response exceeds the {self._MAX_RESPONSE_BYTES}-byte limit"
                )

        body = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if not chunk:
                continue
            if len(body) + len(chunk) > self._MAX_RESPONSE_BYTES:
                raise ValueError(
                    f"Device response exceeds the {self._MAX_RESPONSE_BYTES}-byte limit"
                )
            body.extend(chunk)

        try:
            obj = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Device returned invalid JSON") from exc

        if not isinstance(obj, dict):
            raise ValueError("Device response must be a JSON object")

        return obj

    def _processResponse(self, response: Dict[str, Any]) -> None:
        logging.debug("Processing response: %s", response)
        self._walkProperties(response, callback=self._setResponseProperty)

        if self.ServiceT > 0:
            # V2 does not expose ServiceMax directly; approx from 6 months in minutes.
            service_max = 180 * 24 * 60
            self.DaysToService = max(0, math.ceil((service_max - self.ServiceT) / (24 * 60)))

    def _setResponseProperty(self, prop: str, value: Any) -> None:
        expected_type = self._RESPONSE_FIELD_TYPES.get(prop)
        if expected_type is None:
            logging.debug("Ignoring unknown response property: %s", prop)
            return

        if type(value) is not expected_type:
            raise TypeError(
                f"Invalid response property {prop}: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

        setattr(self, prop, value)

    def _walkProperties(self, obj: Dict[str, Any], callback: callable, maxDepth: int = 3) -> None:
        if maxDepth <= 0:
            raise ValueError(
                "Error processing response - max recursion depth reached. "
                "This could happen if the device sent an unexpected response."
            )

        for prop, value in obj.items():
            if isinstance(value, dict):
                self._walkProperties(value, callback, maxDepth=maxDepth - 1)
            else:
                callback(prop, value)

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
