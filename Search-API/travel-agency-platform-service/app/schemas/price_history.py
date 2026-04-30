from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class PriceSnapshotSchema(BaseModel):
    recorded_at: datetime
    price: float
    currency: str

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    origin: str
    destination: str
    departure_date: date
    airline_code: Optional[str]
    snapshots: list[PriceSnapshotSchema]
    data_points: int


class PriceRangeResponse(BaseModel):
    origin: str
    destination: str
    departure_date: date
    min_price: float
    min_recorded_at: datetime
    max_price: float
    max_recorded_at: datetime
    currency: str


class PriceComparisonResponse(BaseModel):
    origin: str
    destination: str
    departure_date: date
    airline_code: str
    current_price: float
    historical_average: float
    difference: float
    difference_pct: float
    currency: str
    data_points: int


class InsufficientDataResponse(BaseModel):
    message: str
    data_points: int