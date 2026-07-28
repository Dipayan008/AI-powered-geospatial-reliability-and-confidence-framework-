from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class DataSource(Base):
    """A single raw data source ingested from satellite/weather/OSM/news/user reports etc."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    raw_content = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    insights = relationship("Insight", back_populates="source")


class Insight(Base):
    """A processed insight derived from a data source, scored by the AI engine (Member 3)."""
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    reliability_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    town_village = Column(String, nullable=True)
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("DataSource", back_populates="insights")


class Alert(Base):
    """Alert raised when insights conflict or confidence drops below a threshold."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=True)
    message = Column(Text, nullable=False)
    severity = Column(String, default="info")
    created_at = Column(DateTime, default=datetime.utcnow)
