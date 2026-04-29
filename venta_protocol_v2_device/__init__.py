import json
import logging
import math
from typing import Any, Dict, Optional

import requests


class Venta_Protocol_v2_Device:
    """Class representing a Venta device that uses protocol version 2.0.

    This library mirrors the public API style of venta_protocol_v3_device as closely as possible,
    while adapting request/response handling to the V2 endpoint (/datastructure).
    """

    def __init__(self, IP: str):
        self.IP: str = IP

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

    def _setAction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._makeCall("/datastructure", {"Action": payload})

    def _makeCall(self, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"http://{self.IP}{endpoint}"
        logging.debug("Sending payload to endpoint %s: %s", url, payload)
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        obj = response.json()
        self._processResponse(obj)
        return obj

    def _processResponse(self, response: Dict[str, Any]) -> None:
        logging.debug("Processing response: %s", response)
        self._walkProperties(response, callback=lambda prop, value: setattr(self, prop, value))

        if self.ServiceT > 0:
            # V2 does not expose ServiceMax directly; approx from 6 months in minutes.
            service_max = 180 * 24 * 60
            self.DaysToService = max(0, math.ceil((service_max - self.ServiceT) / (24 * 60)))

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
