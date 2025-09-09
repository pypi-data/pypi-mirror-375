#!/usr/bin/env python
"""Advanced usage examples for oasis-rofl-client."""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import httpx
from oasis_rofl_client import RoflClient, KeyKind

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see transport details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def example_with_http_url():
    """Example using HTTP URL instead of Unix socket."""
    client = RoflClient(url="https://rofl.example.com")
    print(f"Client configured with URL: {client.url}")
    
    try:
        key = await client.generate_key("api-key-1")
        print(f"Generated key via HTTP: {key}")
    except httpx.ConnectError:
        print("Connection failed - ensure ROFL service is running at the specified URL")


async def example_with_custom_socket():
    """Example using custom Unix socket path."""
    client = RoflClient(url="/custom/path/rofl.sock")
    print(f"Client configured with custom socket: {client.url}")
    
    try:
        key = await client.generate_key("socket-key-1")
        print(f"Generated key via custom socket: {key}")
    except Exception as e:
        print(f"Error: {e}")


async def example_multiple_keys():
    """Generate multiple keys concurrently."""
    client = RoflClient()
    
    # Generate multiple keys concurrently
    key_ids = ["user-key", "api-key", "service-key"]
    
    try:
        # Create tasks for concurrent execution
        tasks = [client.generate_key(key_id) for key_id in key_ids]
        keys = await asyncio.gather(*tasks, return_exceptions=True)
        
        for key_id, key in zip(key_ids, keys):
            if isinstance(key, Exception):
                print(f"{key_id}: Failed - {key}")
            else:
                print(f"{key_id}: {key}")
    except Exception as e:
        print(f"Error during batch generation: {e}")


async def example_with_different_key_kinds():
    """Demonstrate generating different types of keys."""
    client = RoflClient()
    
    key_types = [
        ("secp256k1-key", KeyKind.SECP256K1, "SECP256K1 private key"),
        ("ed25519-key", KeyKind.ED25519, "Ed25519 private key"),
        ("entropy-256", KeyKind.RAW_256, "256 bits of raw entropy"),
        ("entropy-384", KeyKind.RAW_384, "384 bits of raw entropy"),
    ]
    
    for key_id, kind, description in key_types:
        try:
            key = await client.generate_key(key_id, kind=kind)
            print(f"{description} ({key_id}): {key[:16]}...")
        except Exception as e:
            print(f"Failed to generate {description}: {e}")


async def example_with_error_handling():
    """Demonstrate comprehensive error handling."""
    client = RoflClient()
    
    try:
        key = await client.generate_key("test-key", kind=KeyKind.SECP256K1)
        print(f"Success: {key}")
        
    except httpx.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
        
    except httpx.ConnectError as e:
        print(f"Connection failed: {e}")
        print("Ensure ROFL service is running and accessible")
        
    except httpx.RequestError as e:
        print(f"Request failed: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")


async def main():
    """Run all examples."""
    print("=== ROFL Client Advanced Examples ===\n")
    
    print("1. HTTP URL Example:")
    await example_with_http_url()
    print()
    
    print("2. Custom Socket Example:")
    await example_with_custom_socket()
    print()
    
    print("3. Multiple Keys Example:")
    await example_multiple_keys()
    print()
    
    print("4. Different Key Kinds Example:")
    await example_with_different_key_kinds()
    print()
    
    print("5. Error Handling Example:")
    await example_with_error_handling()


if __name__ == "__main__":
    asyncio.run(main())