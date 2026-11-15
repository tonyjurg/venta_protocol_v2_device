---
title: Architecture
description: How the Python client validates requests, communicates with a Venta device, and updates state.
permalink: /architecture/
---

# Architecture

The package is a synchronous Python client implemented in [venta_protocol_v2_device/__init__.py]({{ site.github_url }}/blob/main/venta_protocol_v2_device/__init__.py). It exports `Venta_Protocol_v2_Device` and uses `requests` for HTTP. There is no background polling service, discovery process, or persistent connection pool.

## Request and response flow

```text
Python caller
    |
    +-- getStatus() ---------------------+
    |                                   |
    +-- setter -> type check            |
                  -> Action payload ----+
                                        |
                              POST /datastructure
                                        |
                              bounded JSON response
                                        |
                              recognized field updates
                                        |
                              dictionary or boolean result
```

1. **Create the client.** The constructor validates a private IPv4 address, stores it in a frozen `_DeviceEndpoint`, and initializes attributes. It performs no network I/O. The public `IP` attribute is informational; assigning a new value to it does not change the connection destination. Create a new client to use another address.
2. **Prepare the call.** `getStatus()` calls `_makeCall()` without an action payload. Setters validate exact argument types and pass their fields to `_setAction()`, which wraps them in an `Action` object.
3. **Send HTTP.** `_makeCall()` opens a new Requests session, disables `trust_env`, and posts to `http://<address>/datastructure` with `timeout=10`, `allow_redirects=False`, and `stream=True`. This applies to status reads as well as commands. The session closes at the end of the call.
4. **Validate the response.** Redirect responses are rejected, HTTP error statuses raise, and `_readResponseJSON()` enforces the byte limit before returning a JSON dictionary.
5. **Update state.** `_processResponse()` walks nested dictionaries, assigns recognized fields with exact type checks, and calculates `DaysToService` when applicable.
6. **Return to the caller.** A status call returns the parsed dictionary; setters return their documented comparison or `Action`-presence result.

For example, `setTargetHum(50)` sends this JSON payload:

```json
{"Action": {"TargetHum": 50}}
```

Status reads pass `json=None` to Requests. They use HTTP POST, not GET.

## Response boundaries

`_readResponseJSON()` accepts at most 262,144 bytes (256 KiB). It checks `Content-Length` when provided and separately checks the accumulated bytes while reading the stream. Invalid JSON and top-level values other than dictionaries are rejected.

`_walkProperties()` starts with a depth limit of 3. It visits the root and up to two nested dictionary levels; entering another dictionary level raises `ValueError`. Leaf fields are passed to `_setResponseProperty()`.

`_RESPONSE_FIELD_TYPES` is the allowlist for attribute updates. Unknown leaf fields are ignored for state updates but remain in the dictionary returned by `getStatus()`. Known fields with incorrect types raise `TypeError`; for example, `"FanSpeed": "3"` is rejected. A response cannot use an unknown field to overwrite a method or change the connection address.

State updates happen as fields are visited. They are not rolled back if a later field is invalid, and omitted fields retain their previous values. The [User Guide]({{ '/user-guide/#read-device-state' | relative_url }}) explains what this means for applications using cached attributes.

## Repository structure

| Location | Purpose |
| --- | --- |
| `venta_protocol_v2_device/__init__.py` | Client, input checks, HTTP calls, response parsing, and cached state |
| `pyproject.toml` | Package metadata, Python requirement, and runtime dependency |
| `tests/` | Hardware-free tests for network restrictions and response validation |
| `usage/basic_device_control.ipynb` | Guided examples that contact a real device |
| `docs/` | Jekyll website source |
| `.github/workflows/tests.yml` | Package installation and pytest checks |
| `.github/workflows/deploy-pages.yml` | Current Jekyll build and GitHub Pages deployment |
| `.github/workflows/publish.yml` | Python package publication to PyPI |

The website build does not execute the Python examples and needs no Venta hardware. Package publication and site deployment are separate workflows. Sphinx API documentation and version selection are planned as separate changes; this page describes the current implementation.

## Protocol compatibility

The public method names follow the style of [venta_protocol_v3_device](https://github.com/bobiboy/venta_protocol_v3_device), while the transport targets the V2 `/datastructure` endpoint. Similar method names do not make the wire protocols interchangeable. This package implements no V3 discovery mechanism and does not negotiate protocol versions.

See [Contributing]({{ '/contributing/' | relative_url }}) for the test workflow and [Examples]({{ '/examples/' | relative_url }}) for application code.
