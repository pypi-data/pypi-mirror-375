from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class InferenceRequest(BaseModel):
    """Request for LLM inference."""
    model: str = Field(..., description="Model identifier")
    prompt: str = Field(..., description="Input prompt")
    max_tokens: int = Field(500, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    top_p: Optional[float] = Field(None, description="Top-p sampling")
    stream: bool = Field(False, description="Stream response")
    metadata: Optional[Dict[str, Any]] = None


class InferenceResponse(BaseModel):
    """Response from LLM inference."""
    id: str = Field(..., description="Response ID")
    model: str = Field(..., description="Model used")
    text: str = Field(..., description="Generated text")
    tokens_used: int = Field(..., description="Tokens consumed")
    latency_ms: float = Field(..., description="Processing latency")
    cost_blma: float = Field(..., description="Cost in BLMA tokens")
    timestamp: datetime = Field(..., description="Timestamp")


class MiningStatus(BaseModel):
    """Current mining status."""
    state: str = Field(..., description="Mining state")
    jobs_completed: int = Field(0, description="Jobs completed")
    total_earnings: float = Field(0.0, description="Total BLMA earned")
    model: str = Field(..., description="Model being used")
    provider: str = Field(..., description="Model provider")


class MiningStats(BaseModel):
    """Detailed mining statistics."""
    address: str = Field(..., description="Miner address")
    hash_rate: float = Field(0.0, description="Current hash rate")
    jobs_completed: int = Field(0, description="Total jobs completed")
    jobs_failed: int = Field(0, description="Total jobs failed")
    total_earnings: str = Field("0", description="Total BLMA earned")
    pending_rewards: str = Field("0", description="Pending rewards")
    last_job_time: Optional[datetime] = None
    uptime_hours: float = Field(0.0, description="Total uptime")
    reputation_score: float = Field(0.0, description="Miner reputation")


class Rewards(BaseModel):
    """Rewards information."""
    address: str = Field(..., description="Wallet address")
    total_earned: str = Field("0", description="Total BLMA earned")
    total_claimed: str = Field("0", description="Total BLMA claimed")
    pending_rewards: str = Field("0", description="Pending rewards")
    last_claim_time: Optional[datetime] = None
    next_claim_available: Optional[datetime] = None


class Job(BaseModel):
    """Mining job."""
    id: str = Field(..., description="Job ID")
    type: str = Field(..., description="Job type")
    model: str = Field(..., description="Required model")
    input_data: Dict[str, Any] = Field(..., description="Job input")
    max_time_seconds: int = Field(60, description="Maximum processing time")
    reward_blma: float = Field(..., description="Reward amount")
    created_at: datetime = Field(..., description="Creation time")


class Model(BaseModel):
    """Available model information."""
    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider")
    size_gb: float = Field(..., description="Model size")
    context_length: int = Field(..., description="Context length")
    cost_per_token: float = Field(..., description="Cost per token")
    min_memory_gb: int = Field(..., description="Minimum memory required")
    gpu_required: bool = Field(False, description="GPU required")
    supported_tasks: List[str] = Field(..., description="Supported tasks")