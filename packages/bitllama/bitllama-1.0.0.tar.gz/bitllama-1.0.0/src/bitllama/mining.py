import asyncio
import logging
from typing import Optional, Callable, Any
from enum import Enum
from .client import BitLlama
from .types import MiningStatus, MiningStats, Job
from .exceptions import MiningError

logger = logging.getLogger(__name__)


class MinerState(Enum):
    """Mining state enumeration."""
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class MiningClient:
    """Client for mining operations."""
    
    def __init__(
        self,
        client: BitLlama,
        model_provider: str = "ollama",
        model_name: str = "llama3:70b",
        max_concurrent_jobs: int = 1,
        job_callback: Optional[Callable[[Job], Any]] = None,
    ):
        """
        Initialize the mining client.
        
        Args:
            client: BitLlama client instance
            model_provider: Model provider ('ollama' or 'webllm')
            model_name: Name of the model to use for mining
            max_concurrent_jobs: Maximum number of concurrent jobs
            job_callback: Optional callback for job completion
        """
        self.client = client
        self.model_provider = model_provider
        self.model_name = model_name
        self.max_concurrent_jobs = max_concurrent_jobs
        self.job_callback = job_callback
        
        self.state = MinerState.IDLE
        self._mining_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._jobs_completed = 0
        self._total_earnings = 0.0
    
    async def start(self) -> None:
        """Start the mining process."""
        if self.state == MinerState.RUNNING:
            logger.warning("Mining is already running")
            return
        
        if not self.client.account:
            raise MiningError("Wallet not connected. Please provide a private key.")
        
        logger.info(f"Starting mining with {self.model_provider}:{self.model_name}")
        self.state = MinerState.STARTING
        
        try:
            # Register miner with coordinator
            await self._register_miner()
            
            # Start mining loop
            self._stop_event.clear()
            self._mining_task = asyncio.create_task(self._mining_loop())
            self.state = MinerState.RUNNING
            
            logger.info("Mining started successfully")
        except Exception as e:
            self.state = MinerState.ERROR
            raise MiningError(f"Failed to start mining: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the mining process."""
        if self.state != MinerState.RUNNING:
            logger.warning("Mining is not running")
            return
        
        logger.info("Stopping mining...")
        self.state = MinerState.STOPPING
        
        # Signal stop and wait for task to complete
        self._stop_event.set()
        
        if self._mining_task:
            await self._mining_task
            self._mining_task = None
        
        # Unregister miner
        await self._unregister_miner()
        
        self.state = MinerState.IDLE
        logger.info("Mining stopped")
    
    async def get_status(self) -> MiningStatus:
        """Get current mining status."""
        return MiningStatus(
            state=self.state.value,
            jobs_completed=self._jobs_completed,
            total_earnings=self._total_earnings,
            model=self.model_name,
            provider=self.model_provider,
        )
    
    async def get_stats(self) -> MiningStats:
        """Get detailed mining statistics."""
        if not self.client.account:
            raise MiningError("Wallet not connected")
        
        data = await self.client._request(
            'GET',
            f'/miners/{self.client.account.address}/stats'
        )
        
        return MiningStats(**data)
    
    async def _register_miner(self) -> None:
        """Register miner with the coordinator."""
        data = {
            "address": self.client.account.address,
            "provider": self.model_provider,
            "model": self.model_name,
            "max_concurrent_jobs": self.max_concurrent_jobs,
        }
        
        await self.client._request('POST', '/miners/register', data=data)
    
    async def _unregister_miner(self) -> None:
        """Unregister miner from the coordinator."""
        await self.client._request(
            'POST',
            f'/miners/{self.client.account.address}/unregister'
        )
    
    async def _mining_loop(self) -> None:
        """Main mining loop."""
        while not self._stop_event.is_set():
            try:
                # Request job from coordinator
                job = await self._get_job()
                
                if job:
                    # Process the job
                    result = await self._process_job(job)
                    
                    # Submit result
                    await self._submit_result(job, result)
                    
                    self._jobs_completed += 1
                    
                    # Call callback if provided
                    if self.job_callback:
                        await self.job_callback(job)
                else:
                    # No job available, wait before polling again
                    await asyncio.sleep(5)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in mining loop: {str(e)}")
                await asyncio.sleep(10)
    
    async def _get_job(self) -> Optional[Job]:
        """Get a job from the coordinator."""
        try:
            data = await self.client._request(
                'GET',
                f'/jobs/next?miner={self.client.account.address}'
            )
            
            if data:
                return Job(**data)
            return None
        except Exception as e:
            logger.error(f"Failed to get job: {str(e)}")
            return None
    
    async def _process_job(self, job: Job) -> str:
        """
        Process a mining job.
        
        This is where the actual LLM inference happens.
        In a real implementation, this would call the model provider.
        """
        logger.info(f"Processing job {job.id}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # In real implementation, this would call Ollama/WebLLM
        # For now, return a dummy result
        return f"Processed result for job {job.id}"
    
    async def _submit_result(self, job: Job, result: str) -> None:
        """Submit job result to the coordinator."""
        data = {
            "job_id": job.id,
            "miner": self.client.account.address,
            "result": result,
        }
        
        response = await self.client._request('POST', '/jobs/submit', data=data)
        
        # Update earnings if provided
        if 'reward' in response:
            self._total_earnings += response['reward']
            logger.info(f"Earned {response['reward']} BLMA for job {job.id}")