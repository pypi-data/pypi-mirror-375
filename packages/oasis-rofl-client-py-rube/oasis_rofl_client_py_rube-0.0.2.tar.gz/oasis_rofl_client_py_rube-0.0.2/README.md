# oasis-rofl-client-py-rube

[![Publish to PyPI](https://github.com/rube-de/oasis-rofl-client-py/actions/workflows/publish.yml/badge.svg)](https://github.com/rube-de/oasis-rofl-client-py/actions/workflows/publish.yml)
[![PyPI version](https://badge.fury.io/py/oasis-rofl-client-py-rube.svg)](https://badge.fury.io/py/oasis-rofl-client-py-rube)

Python client SDK for Oasis ROFL (Runtime Off-chain Logic).

## Installation

```bash
pip install oasis-rofl-client-py-rube
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
uv add install oasis-rofl-client-py-rube
```

The package requires Python 3.9+ and depends on `httpx` for async HTTP operations.

## Quickstart

The RoflClient provides async methods for interacting with ROFL services:

```python
import asyncio
from oasis_rofl_client import RoflClient

async def main():
    # Create a client (defaults to Unix socket at /run/rofl-appd.sock)
    client = RoflClient()
    
    # Generate a cryptographic key
    key = await client.generate_key("my-key-id")
    print(f"Generated key: {key}")

# Run the async function
asyncio.run(main())
```

## API Reference

### RoflClient

The main client class for interacting with ROFL runtime services.

#### Constructor

```python
RoflClient(url: str = '')
```

- `url`: Optional URL or Unix socket path
  - If empty (default): Uses Unix socket at `/run/rofl-appd.sock`
  - If starts with `http://` or `https://`: Uses HTTP transport
  - Otherwise: Treats as Unix socket path

#### Methods

##### `async generate_key(key_id: str) -> str`

Fetches or generates a secp256k1 cryptographic key from ROFL.

- **Parameters:**
  - `key_id`: Identifier for the key
- **Returns:** The private key as a hex string
- **Raises:** `httpx.HTTPStatusError` if the request fails

## Examples

```python
import asyncio
from oasis_rofl_client import RoflClient

async def generate_keys():
    client = RoflClient()  # Uses /run/rofl-appd.sock
    
    # Generate multiple keys
    keys = {}
    for i in range(3):
        key_id = f"key-{i}"
        keys[key_id] = await client.generate_key(key_id)
    
    return keys

keys = asyncio.run(generate_keys())
for key_id, key in keys.items():
    print(f"{key_id}: {key}")
```

### Error Handling

```python
import asyncio
import httpx
from oasis_rofl_client import RoflClient

async def safe_key_generation():
    client = RoflClient()
    
    try:
        key = await client.generate_key("secure-key")
        print(f"Success: {key}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"Request failed: {e}")

asyncio.run(safe_key_generation())
```

## Development

### Prerequisites

Install the following tools:

#### macOS (using Homebrew)
```bash
# Install Python
brew install python

# Install uv (Python package manager)
brew install uv
```

#### Other platforms
- **Python**: Download from [python.org](https://www.python.org/downloads/)
- **UV**: Follow installation instructions at [docs.astral.sh/uv](https://docs.astral.sh/uv/)

### Setup

Create a virtual environment and install in development mode:

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### Testing

Run a quick sanity check:

```bash
uv run python - <<'PY'
from oasis_rofl_client import Client
print(Client().ping())
PY
```

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Release Process

Publishing to PyPI is fully automated via GitHub Actions. When maintainers merge your PR and create a new release, the package will be automatically published.

For maintainers: See [docs/publish.md](docs/publish.md) for the complete publishing guide.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` for details or visit http://www.apache.org/licenses/LICENSE-2.0.