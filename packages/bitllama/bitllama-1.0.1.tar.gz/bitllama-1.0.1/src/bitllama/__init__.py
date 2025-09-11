"""
BitLlama Python SDK
~~~~~~~~~~~~~~~~~~~

Python SDK for interacting with the BitLlama Protocol.

Basic usage:
    >>> from bitllama import BitLlama
    >>> client = BitLlama(coordinator_url="https://api.bitllama.ai")
    >>> response = await client.inference.create(model="llama3:70b", prompt="Hello!")
    >>> print(response.text)

Full documentation is available at https://docs.bitllama.ai/python-sdk
"""

__version__ = "1.0.0"
__author__ = "BitLlama Team"
__email__ = "team@bitllama.ai"

from .client import BitLlama
from .mining import MiningClient
from .types import (
    InferenceRequest,
    InferenceResponse,
    MiningStatus,
    MiningStats,
    Rewards,
    Model,
)
from .exceptions import (
    BitLlamaError,
    AuthenticationError,
    NetworkError,
    InferenceError,
    MiningError,
)

__all__ = [
    "BitLlama",
    "MiningClient",
    "InferenceRequest",
    "InferenceResponse",
    "MiningStatus",
    "MiningStats",
    "Rewards",
    "Model",
    "BitLlamaError",
    "AuthenticationError",
    "NetworkError",
    "InferenceError",
    "MiningError",
]