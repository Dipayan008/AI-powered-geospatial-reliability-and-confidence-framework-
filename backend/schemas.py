from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    raw_content: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DataSourceOut(DataSourceCreate):
    id: int
    fetched_at: datetime

    class Config:
        from_attributes = True


class InsightCreate(BaseModel):
    source_id: int
    title: str
    summary: str
    reliability_score: Optional[float] = 0.0
    consistency_score: Optional[float] = 0.0
    confidence_score: Optional[float] = 0.0
    explanation: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    town_village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class InsightOut(InsightCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InsightUpdate(BaseModel):
    """Partial update — only send the fields you want to change."""
    title: Optional[str] = None
    summary: Optional[str] = None


class AlertCreate(BaseModel):
    insight_id: Optional[int] = None
    message: str
    severity: Optional[str] = "info"


class AlertOut(AlertCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
