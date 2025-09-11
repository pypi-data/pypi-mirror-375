"""
BitLlama SDK Exceptions
~~~~~~~~~~~~~~~~~~~~~~

Custom exception classes for the BitLlama Python SDK.
"""


class BitLlamaError(Exception):
    """Base exception for all BitLlama SDK errors."""
    pass


class AuthenticationError(BitLlamaError):
    """Raised when authentication fails."""
    pass


class NetworkError(BitLlamaError):
    """Raised when network operations fail."""
    pass


class InferenceError(BitLlamaError):
    """Raised when inference operations fail."""
    pass


class MiningError(BitLlamaError):
    """Raised when mining operations fail."""
    pass


class ValidationError(BitLlamaError):
    """Raised when validation fails."""
    pass


class ContractError(BitLlamaError):
    """Raised when smart contract interactions fail."""
    pass


class RateLimitError(BitLlamaError):
    """Raised when rate limits are exceeded."""
    pass


class InsufficientFundsError(BitLlamaError):
    """Raised when wallet has insufficient funds."""
    pass