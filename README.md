# CyGlobs Python Client Server Framework

A lightweight Python client/server framework built around this methodology:

- Comparators
- Inverse Operators
- Contingency Planning
- Level Of Indirection
- Best Practices

## Architecture

| Methodology | Framework Role |
|---|---|
| Comparators | Validate protocol versions and payload contracts. |
| Inverse Operators | Map abstract client operations to server-side handlers. |
| Contingency Planning | Provide retries, timeouts, safe fallback envelopes, and error handling. |
| Level Of Indirection | Separate transport, protocol, service logic, configuration, and tests. |
| Best Practices | Type hints, dataclasses, Pydantic envelopes, tests, and clear entry points. |

## Requirements

Recommended Python versions:

- Python 3.10
- Python 3.11
- Python 3.12

Check your version:

```bash
python --version
```

The `requirements.txt` file is in the root directory of this repository:

```text
CyGlobs-Python-Framework-For-Full-Stack-Developers/
├── requirements.txt
├── server.py
├── client.py
├── framework/
└── tests/
```

## Install on Windows

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Install on macOS/Linux

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Troubleshooting: pydantic-core wheel build error

If you see an error like this:

```text
Failed to build installable wheels for some pyproject.toml based projects
╰─> pydantic-core
```

Try these steps:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If it still fails, confirm your Python version:

```bash
python --version
```

Use Python 3.10, 3.11, or 3.12 for the smoothest install. If your system is using a very old Python version or a newer version without matching prebuilt wheels, create a fresh virtual environment with Python 3.12.

## Run server

```bash
uvicorn server:app --reload
```

Open the server in a browser:

```text
http://127.0.0.1:8000
```

FastAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Run client

In another terminal, with the virtual environment activated:

```bash
python client.py
```

## Run tests

```bash
pytest
```

## Example RPC request

```json
{
  "protocol_version": "1.0",
  "operation": "compare",
  "payload": {
    "left": 10,
    "right": 10
  }
}
```

## Example RPC response

```json
{
  "protocol_version": "1.0",
  "status": "ok",
  "result": {
    "left": 10,
    "right": 10,
    "equal": true,
    "inverse_equal": false
  },
  "error": null
}
```

## Add a new operation

1. Create a function in `framework/services.py`.
2. Register it in `server.py` with `operators.register("operation_name", handler)`.
3. Call it from `client.py` with `client.call("operation_name", payload)`.

## Current operations

| Operation | Purpose |
|---|---|
| `health` | Confirms the server is running and returns methodology metadata. |
| `echo` | Returns a message sent by the client. |
| `compare` | Compares two values and returns equality plus inverse equality. |
