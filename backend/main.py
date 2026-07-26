from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import ingestion
from database import engine, get_db, Base

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PS07 Geospatial AI Backend", version="1.0")

# Allow the frontend (Next.js) to call this API during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "PS07 backend running"}


# ---------- DATA SOURCES ----------

@app.post("/sources", response_model=schemas.DataSourceOut)
def add_source(source: schemas.DataSourceCreate, db: Session = Depends(get_db)):
    """Ingest one new raw data source (satellite, weather, OSM, news, user report, etc.)"""
    return ingestion.ingest_source(
        db, source.name, source.source_type, source.raw_content,
        source.latitude, source.longitude
    )


@app.get("/sources", response_model=List[schemas.DataSourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(models.DataSource).all()


@app.get("/sources/{source_id}", response_model=schemas.DataSourceOut)
def get_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(models.DataSource).filter(models.DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


# ---------- INSIGHTS (consistency / reliability / confidence) ----------

@app.post("/insights/generate", response_model=schemas.InsightOut)
def generate_insight(title: str, summary: str, source_ids: List[int], db: Session = Depends(get_db)):
    """
    Take multiple source IDs covering the same event/location, score them,
    and store the resulting insight. Now uses the real AI/ML confidence
    engine (ai/model.py) via ingestion.real_ai_score.
    """
    sources = db.query(models.DataSource).filter(models.DataSource.id.in_(source_ids)).all()
    if not sources:
        raise HTTPException(status_code=404, detail="No matching sources found")

<<<<<<< HEAD
    scores = ingestion.real_ai_score(sources)
=======
    scores = ingestion.score_sources(sources)
>>>>>>> af87205729e166732966916dbb20e92e5c31d6ce

    insight = models.Insight(
        source_id=sources[0].id,
        title=title,
        summary=summary,
        reliability_score=scores["reliability_score"],
        consistency_score=scores["consistency_score"],
        confidence_score=scores["confidence_score"],
        explanation=scores["explanation"],
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)

    # Auto-raise an alert if confidence is low
    if insight.confidence_score < 50:
        alert = models.Alert(
            insight_id=insight.id,
            message=f"Low confidence ({insight.confidence_score}%) for insight '{insight.title}'",
            severity="warning",
        )
        db.add(alert)
        db.commit()

    return insight


@app.get("/insights", response_model=List[schemas.InsightOut])
def list_insights(db: Session = Depends(get_db)):
    return db.query(models.Insight).order_by(models.Insight.created_at.desc()).all()


@app.get("/insights/{insight_id}", response_model=schemas.InsightOut)
def get_insight(insight_id: int, db: Session = Depends(get_db)):
    insight = db.query(models.Insight).filter(models.Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    return insight


# ---------- SOURCE COMPARISON PANEL ----------

@app.get("/compare")
def compare_sources(source_ids: str, db: Session = Depends(get_db)):
    """
    Compare multiple sources side by side.
    Usage: GET /compare?source_ids=1,2,3
    """
    ids = [int(i) for i in source_ids.split(",") if i.strip().isdigit()]
    sources = db.query(models.DataSource).filter(models.DataSource.id.in_(ids)).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.source_type,
            "content_preview": s.raw_content[:200],
            "location": {"lat": s.latitude, "lon": s.longitude},
        }
        for s in sources
    ]


# ---------- ALERTS ----------

@app.post("/alerts", response_model=schemas.AlertOut)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    new_alert = models.Alert(**alert.dict())
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@app.get("/alerts", response_model=List[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()


from pydantic import BaseModel


class ObservationIn(BaseModel):
    source_type: str
    content: str
    latitude: float | None = None
    longitude: float | None = None


class AnalyzeRequest(BaseModel):
    title: str
    summary: str
    observations: list[ObservationIn]


@app.post("/analyze")
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Unified endpoint: takes raw observations directly (no need to POST to
    /sources first), stores each as a DataSource, runs them through the real
    AI confidence engine (ai/model.py), stores the resulting Insight, and
    returns the full result in one call. This replaces calling a separate
    AI server directly from the frontend.
    """
    stored_sources = [
        ingestion.ingest_source(db, obs.source_type, obs.source_type, obs.content,
                                 obs.latitude, obs.longitude)
        for obs in request.observations
    ]
    scores = ingestion.score_sources(stored_sources)

    insight = models.Insight(
        source_id=stored_sources[0].id,
        title=request.title,
        summary=request.summary,
        reliability_score=scores["reliability_score"],
        consistency_score=scores["consistency_score"],
        confidence_score=scores["confidence_score"],
        explanation=scores["explanation"],
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)

    if insight.confidence_score < 50:
        db.add(models.Alert(
            insight_id=insight.id,
            message=f"Low confidence ({insight.confidence_score}%) for '{insight.title}'",
            severity="warning",
        ))
        db.commit()

    return {
        "insight_id": insight.id,
        "reliability_score": insight.reliability_score,
        "consistency_score": insight.consistency_score,
        "confidence_score": insight.confidence_score,
        "explanation": insight.explanation,
        "ai_engine_used": ingestion.AI_AVAILABLE,
    }


@app.post("/analyze-batch")
def analyze_batch(requests: list[AnalyzeRequest], db: Session = Depends(get_db)):
    """Run /analyze logic for multiple events in one call — for bulk/demo data."""
    return [analyze(r, db) for r in requests]


@app.get("/analyze-live")
def analyze_live(source_ids: str, db: Session = Depends(get_db)):
    """
    Re-run AI scoring on existing stored sources (already ingested via /sources),
    without creating new DataSource rows. Usage: /analyze-live?source_ids=1,2,3
    """
    ids = [int(i) for i in source_ids.split(",") if i.strip().isdigit()]
    sources = db.query(models.DataSource).filter(models.DataSource.id.in_(ids)).all()
    if not sources:
        raise HTTPException(status_code=404, detail="No matching sources found")
    return ingestion.score_sources(sources)


@app.get("/health/ai")
def ai_health():
    """Quick check for the frontend/demo: is the real AI engine wired in or running on fallback?"""
    return {"ai_module_connected": ingestion.AI_AVAILABLE}

@app.get("/export/insights")
def export_insights(db: Session = Depends(get_db)):
    insights = db.query(models.Insight).all()
    return {
        "total_insights": len(insights),
        "data": [schemas.InsightOut.model_validate(i).model_dump() for i in insights],
    }