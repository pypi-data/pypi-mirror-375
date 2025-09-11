# BitLlama Python SDK

<div align="center">
  <img src="https://raw.githubusercontent.com/samthedataman/bitllama/main/assets/logo.png" alt="BitLlama Logo" width="150" height="150" />
  
  <h3>Official Python SDK for the BitLlama Protocol</h3>
  
  <img src="https://img.shields.io/pypi/v/bitllama.svg" />
  <img src="https://img.shields.io/badge/python-%3E%3D3.9-blue.svg" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" />
</div>

## Installation

```bash
pip install bitllama
```

## Quick Start

```python
from bitllama import BitLlama, MiningClient
import asyncio

async def main():
    # Initialize client
    client = BitLlama(
        coordinator_url="https://api.bitllama.ai",
        private_key="your_private_key",
        network="base-mainnet"
    )
    
    # Create inference request
    response = await client.i
    nference.create(
        model="llama3:70b",
        prompt="Explain quantum computing",
        max_tokens=500
    )
    print(response.text)

asyncio.run(main())
```

## Mining

```python
# Initialize mining client
miner = MiningClient(
    client=client,
    model_provider="ollama",
    model_name="llama3:70b"
)

# Start mining
await miner.start()

# Check status
status = await miner.get_status()
print(f"Jobs completed: {status.jobs_completed}")
print(f"Earnings: {status.total_earnings} BLMA")

# Stop mining
await miner.stop()
```

## Documentation

## Links

- **PyPI Package**: [https://pypi.org/project/bitllama/](https://pypi.org/project/bitllama/)
- **GitHub**: [https://github.com/samthedataman/bitllama/tree/main/packages/python-sdk](https://github.com/samthedataman/bitllama/tree/main/packages/python-sdk)
- **Documentation**: [https://docs.bitllama.ai/python-sdk](https://docs.bitllama.ai/python-sdk)