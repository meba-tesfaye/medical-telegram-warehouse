from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api.database import get_db
from api.schemas import ChannelResponse, DetectionResponse, AlertResponse, AlertSummaryResponse

app = FastAPI(
    title="Medical Telegram Warehouse Analytical API",
    description="Production FastAPI backend exposing transformed Telegram telemetry and YOLOv8 data structures.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "Medical Telegram Warehouse API"}

@app.get("/api/channels", response_model=List[ChannelResponse], status_code=status.HTTP_200_OK)
def get_channels(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT channel_id, channel_name, channel_username FROM dim_channels")).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query operation failed: {str(e)}")

@app.get("/api/detections", response_model=List[DetectionResponse], status_code=status.HTTP_200_OK)
def get_detections(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("""
            SELECT detection_id, message_id, channel_id, image_path, detected_item, confidence_score, created_at 
            FROM fct_image_detections
        """)).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query operation failed: {str(e)}")

@app.get("/api/alerts", response_model=List[AlertResponse], status_code=status.HTTP_200_OK)
def get_alerts(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("""
            SELECT alert_id, message_id, channel_id, message_text, alert_type, is_commercial, created_at 
            FROM fct_medical_alerts
        """)).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query operation failed: {str(e)}")

@app.get("/api/alerts/summary", response_model=List[AlertSummaryResponse], status_code=status.HTTP_200_OK)
def get_alerts_summary(db: Session = Depends(get_db)):
    try:
        query = """
            SELECT 
                c.channel_name,
                COUNT(a.alert_id) as total_alerts,
                SUM(CASE WHEN a.is_commercial = TRUE THEN 1 ELSE 0 END) as commercial_count,
                SUM(CASE WHEN a.is_commercial = FALSE THEN 1 ELSE 0 END) as organic_count
            FROM fct_medical_alerts a
            JOIN dim_channels c ON a.channel_id = c.channel_id
            GROUP BY c.channel_name
        """
        result = db.execute(text(query)).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database calculation summary failed: {str(e)}")