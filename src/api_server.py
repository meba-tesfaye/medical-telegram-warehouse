import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

# Force Python to recognize the current directory structure for Windows sub-processes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Medical Telegram Warehouse Analytical API",
    description="FastAPI backend exposing transformed Telegram telemetry and YOLOv8 object detection data.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="medical_warehouse",
            user="postgres",
            password="MyRealPassword123",
            host="localhost",
            port="5432",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Telegram Warehouse Analytical API", "status": "Online"}

@app.get("/api/channels")
def get_channels():
    """Retrieve all monitored Telegram channels."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM main.dim_channels;")
    channels = cursor.fetchall()
    cursor.close()
    conn.close()
    return channels

@app.get("/api/detections")
def get_detections(limit: int = 20):
    """Retrieve the latest YOLOv8 object detection records joined with channel metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.channel_name, f.image_path, f.detected_objects
        FROM main.fct_image_detections f
        JOIN main.dim_channels c ON f.channel_key = c.channel_key
        LIMIT %s;
    """
    cursor.execute(query, (limit,))
    detections = cursor.fetchall()
    cursor.close()
    conn.close()
    return detections

@app.get("/api/alerts/summary")
def get_alerts_summary():
    """Retrieve performance summary indicators from the warehouse."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            COUNT(*) as total_alerts,
            SUM(CASE WHEN is_commercial_ad = TRUE THEN 1 ELSE 0 END) as commercial_ads,
            SUM(CASE WHEN is_commercial_ad = FALSE THEN 1 ELSE 0 END) as organic_alerts
        FROM main.fct_medical_alerts;
    """
    cursor.execute(query)
    summary = cursor.fetchone()
    cursor.close()
    conn.close()
    return summary

if __name__ == "__main__":
    import uvicorn
    # Using the direct app reference instead of a string completely bypasses the reload import bug
    uvicorn.run(app, host="127.0.0.1", port=8000)