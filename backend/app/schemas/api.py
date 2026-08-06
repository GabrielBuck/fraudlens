from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AlertStatus = Literal["novo", "em análise", "fraude confirmada", "falso positivo", "encerrado"]


class AlertUpdate(BaseModel):
    status: AlertStatus
    reviewer_note: str | None = Field(default=None, max_length=1000)


class FeedbackCreate(BaseModel):
    classification: Literal["fraude confirmada", "falso positivo", "inconclusivo"]
    comment: str = Field(min_length=2, max_length=1000)


class AdminRequest(BaseModel):
    accounts: int = Field(default=120, ge=8, le=10_000)
    transactions: int = Field(default=5000, ge=80, le=500_000)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: object | None
    correlation_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetails


class FeedbackResponse(BaseModel):
    id: str
    alert_id: str
    classification: str
    comment: str
    created_at: datetime
