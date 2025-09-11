import os
import asyncio
from typing import Optional, Dict, Any
from web3 import Web3
from eth_account import Account
import aiohttp
from .types import InferenceRequest, InferenceResponse, Rewards
from .exceptions import BitLlamaError, AuthenticationError, NetworkError


class BitLlama:
    """Main client for interacting with the BitLlama Protocol."""
    
    def __init__(
        self,
        coordinator_url: str,
        private_key: Optional[str] = None,
        network: str = "base-mainnet",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the BitLlama client.
        
        Args:
            coordinator_url: URL of the BitLlama coordinator service
            private_key: Ethereum private key for signing transactions
            network: Network to connect to ('base-mainnet' or 'base-sepolia')
            api_key: Optional API key for authenticated requests
        """
        self.coordinator_url = coordinator_url.rstrip('/')
        self.network = network
        self.api_key = api_key or os.getenv('BITLLAMA_API_KEY')
        
        # Initialize Web3
        if network == "base-mainnet":
            self.w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        else:
            self.w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
        
        # Set up account if private key provided
        self.account = None
        if private_key:
            self.account = Account.from_key(private_key)
        
        # Initialize sub-clients
        self.inference = InferenceClient(self)
        self.rewards = RewardsClient(self)
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated request to the coordinator."""
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        if self.account:
            headers['X-Wallet-Address'] = self.account.address
        
        url = f"{self.coordinator_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                    **kwargs
                ) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid API key or authentication failed")
                    elif response.status >= 500:
                        raise NetworkError(f"Server error: {response.status}")
                    elif response.status >= 400:
                        error_data = await response.json()
                        raise BitLlamaError(f"Request failed: {error_data.get('error', 'Unknown error')}")
                    
                    return await response.json()
            except aiohttp.ClientError as e:
                raise NetworkError(f"Network error: {str(e)}")


class InferenceClient:
    """Client for inference operations."""
    
    def __init__(self, client: BitLlama):
        self.client = client
    
    async def create(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> InferenceResponse:
        """
        Create an inference request.
        
        Args:
            model: Model identifier (e.g., 'llama3:70b')
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional model parameters
        
        Returns:
            InferenceResponse object containing the generated text
        """
        request = InferenceRequest(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        data = await self.client._request(
            'POST',
            '/inference/create',
            data=request.dict()
        )
        
        return InferenceResponse(**data)
    
    async def get_models(self) -> list:
        """Get list of available models."""
        data = await self.client._request('GET', '/models')
        return data.get('models', [])


class RewardsClient:
    """Client for rewards operations."""
    
    def __init__(self, client: BitLlama):
        self.client = client
    
    async def get_earnings(self) -> Rewards:
        """Get current earnings for the connected wallet."""
        if not self.client.account:
            raise AuthenticationError("Wallet not connected")
        
        data = await self.client._request(
            'GET',
            f'/rewards/{self.client.account.address}'
        )
        
        return Rewards(**data)
    
    async def claim(self) -> str:
        """
        Claim pending rewards.
        
        Returns:
            Transaction hash of the claim transaction
        """
        if not self.client.account:
            raise AuthenticationError("Wallet not connected")
        
        data = await self.client._request(
            'POST',
            f'/rewards/{self.client.account.address}/claim'
        )
        
        return data.get('tx_hash')