from typing import Literal

from pydantic import BaseModel, Field


class TradeRequest(BaseModel):
    action: Literal["buy", "sell"]
    ticker: str = Field(min_length=1, max_length=8)
    shares: float = Field(gt=0)
    dark_pool: bool = False
    leverage: float = Field(default=1.0, ge=1.0, le=2.0)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class AdvanceRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=250)
