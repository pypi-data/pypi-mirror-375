# ROFL Client Examples

This directory contains example scripts demonstrating how to use the `oasis-rofl-client` package.

## Prerequisites

Install the package and its dependencies:

```bash
uv sync
```

## Examples

### basic_usage.py

Simple example showing:
- Creating a client with default settings
- Generating a single key

Run with:
```bash
uv run python examples/basic_usage.py
```

### advanced_usage.py

Advanced examples showing:
- Using HTTP URLs instead of Unix sockets
- Custom socket paths
- Concurrent key generation
- Comprehensive error handling

Run with:
```bash
uv run python examples/advanced_usage.py
```

## Note

These examples require a running ROFL service to actually generate keys. Without it, they will demonstrate the client setup and show connection errors.