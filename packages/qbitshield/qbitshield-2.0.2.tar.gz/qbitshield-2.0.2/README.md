# QbitShield Python SDK (v2)

Quantum-native SDK for the QbitShield v2 API.

- Default base URL: `https://api.qbitshield.com/api/v2`
- Auth header: `X-API-Key: <your key>`

## Install

```bash
pip install qbitshield
```

## Quickstart

```python
from qbitshield import QbitShieldClient

client = QbitShieldClient(api_key="qs_your_api_key")

# Generate a key
res = client.qkd.generate_key(security_level=256)
print(res.key_id, res.key[:16] + "...")

# Validate a key (if you captured qasm/hash_proof)
# val = client.qkd.validate_key(key=res.key, qasm=res.qasm, hash_proof=res.hash_proof)

# Metrics
m = client.qkd.get_metrics(hours=24)
print(m)
```

## Async usage

```python
import asyncio
from qbitshield import QbitShieldClient

async def main():
    client = QbitShieldClient(api_key="qs_your_api_key")
    res = await client.qkd.generate_key_async(security_level=256)
    print(res.key_id)

asyncio.run(main())
```

## Configuration
- `base_url` (optional): override API endpoint
- `timeout` (seconds)
- `verify_ssl` (bool)

## License
MIT
