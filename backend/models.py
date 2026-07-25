from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class DataSource(Base):
    """A single raw data source ingested from satellite/weather/OSM/news/user reports etc."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)          # e.g. "Sentinel-2", "OpenWeatherMap"
    source_type = Column(String, nullable=False)    # satellite | weather | osm | news | user_report
    raw_content = Column(Text, nullable=False)       # text/JSON payload of the insight
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
    reliability_score = Column(Float, default=0.0)     # 0-100
    consistency_score = Column(Float, default=0.0)      # 0-100
    confidence_score = Column(Float, default=0.0)        # 0-100 (final combined score)
    explanation = Column(Text, nullable=True)             # LLM-generated "why" explanation
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("DataSource", back_populates="insights")


class Alert(Base):
    """Alert raised when insights conflict or confidence drops below a threshold."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=True)
    message = Column(Text, nullable=False)
    severity = Column(String, default="info")   # info | warning | critical
    created_at = Column(DateTime, default=datetime.utcnow)
