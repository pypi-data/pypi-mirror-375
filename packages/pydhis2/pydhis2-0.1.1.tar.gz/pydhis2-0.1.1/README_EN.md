# pydhis2

A reproducible DHIS2 Python SDK designed for LMIC (Low and Middle Income Countries) scenarios.

## Features

- Async HTTP client with automatic retry and rate limiting
- Data Quality Review (DQR) framework based on WHO standards
- Pandas integration for data analysis
- Pipeline system for automated workflows
- Comprehensive testing and benchmarking tools

## Installation

```bash
pip install pydhis2
```

## Quick Start

```python
import asyncio
from pydhis2 import DHIS2Client

async def main():
    client = DHIS2Client(
        base_url="https://play.dhis2.org/dev",
        auth=("admin", "district")
    )
    
    # Get user information
    user_info = await client.get("me")
    print(f"User: {user_info['name']}")

asyncio.run(main())
```

## Documentation

For detailed documentation and examples, visit our [GitHub repository](https://github.com/your-repo/pydhis2).

## License

Apache License 2.0