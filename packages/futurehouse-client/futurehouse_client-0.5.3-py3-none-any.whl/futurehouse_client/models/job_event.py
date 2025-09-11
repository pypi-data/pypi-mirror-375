"""Job event models for cost and usage tracking."""

from datetime import datetime
from enum import StrEnum, auto
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExecutionType(StrEnum):
    """Type of execution for job events."""

    TRAJECTORY = auto()
    SESSION = auto()


class CostComponent(StrEnum):
    """Cost component types for job events."""

    LLM_USAGE = auto()
    EXTERNAL_SERVICE = auto()
    STEP = auto()


class JobEventCreateRequest(BaseModel):
    """Request model for creating a job event matching crow-service schema."""

    execution_id: UUID = Field(description="UUID for trajectory_id or session_id")
    execution_type: ExecutionType = Field(
        description="Either 'TRAJECTORY' or 'SESSION'"
    )
    cost_component: CostComponent = Field(
        description="Cost component: 'LLM_USAGE', 'EXTERNAL_SERVICE', or 'STEP'"
    )
    started_at: datetime = Field(description="Start time of the job event")
    ended_at: datetime = Field(description="End time of the job event")
    crow: str | None = Field(default=None, description="unique identifier for the crow")
    amount_acu: float | None = Field(default=None, description="Cost amount in ACUs")
    amount_usd: float | None = Field(default=None, description="Cost amount in USD")
    rate: float | None = Field(default=None, description="Rate per token/call in USD")
    input_token_count: int | None = Field(
        default=None, description="Input token count for LLM calls"
    )
    completion_token_count: int | None = Field(
        default=None, description="Completion token count for LLM calls"
    )
    metadata: dict[str, Any] | None = Field(default=None)


class JobEventUpdateRequest(BaseModel):
    """Request model for updating a job event matching crow-service schema."""

    amount_acu: float | None = Field(default=None, description="Cost amount in ACUs")
    amount_usd: float | None = Field(default=None, description="Cost amount in USD")
    rate: float | None = Field(default=None, description="Rate per token/call in USD")
    input_token_count: int | None = Field(
        default=None, description="Input token count for LLM calls"
    )
    completion_token_count: int | None = Field(
        default=None, description="Completion token count for LLM calls"
    )
    metadata: dict[str, Any] | None = Field(default=None)
    started_at: datetime | None = Field(
        default=None, description="Start time of the job event"
    )
    ended_at: datetime | None = Field(
        default=None, description="End time of the job event"
    )


class JobEventCreateResponse(BaseModel):
    """Response model for job event creation."""

    id: UUID = Field(description="UUID of the created job event")
