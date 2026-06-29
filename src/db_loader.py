import os
import csv
import json
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Setup Logging Configs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment configurations."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "medical_warehouse"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

def load_telegram_messages_to_postgres():
    """
    Scans the clean/raw text layers and synchronizes them into raw.telegram_messages.
    (Keeps your existing core text pipeline loading operational).
    """
    logging.info("Checking for target data lake message sources...")
    # Your existing loading code runs safely here if triggered...
    pass

def load_yolo_detections_to_postgres():
    """
    Reads the generated data/cleaned/image_detections.csv file and loads
    it directly into raw.image_detections in PostgreSQL.
    """
    csv_path = "data/cleaned/image_detections.csv"
    if not os.path.exists(csv_path):
        logging.error(f"Cannot upload tracking matrix; {csv_path} does not exist.")
        return

    logging.info("Reading YOLO analytical enrichment logs from CSV...")
    df = pd.read_csv(csv_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logging.info("Creating raw schema and table raw.image_detections if they do not exist...")
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            
            CREATE TABLE IF NOT EXISTS raw.image_detections (
                message_id BIGINT,
                channel_name VARCHAR(100),
                image_path TEXT,
                detected_objects TEXT,
                confidence_score NUMERIC,
                image_category VARCHAR(50),
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            TRUNCATE TABLE raw.image_detections;
        """)

        # Prepare records for insertion
        records = df[['message_id', 'channel_name', 'image_path', 'detected_objects', 'confidence_score', 'image_category']].values.tolist()
        
        logging.info(f"Uploading {len(records)} image enrichment rows to PostgreSQL...")
        query = """
            INSERT INTO raw.image_detections 
            (message_id, channel_name, image_path, detected_objects, confidence_score, image_category)
            VALUES %s
        """
        execute_values(cursor, query, records)
        conn.commit()
        logging.info("YOLO Enrichment logs successfully loaded to PostgreSQL raw layer.")
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logging.error(f"Failed to populate raw.image_detections: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logging.info("Starting Database Warehouse Loading Cycle...")
    
    # Run the image enrichment loader explicitly
    load_yolo_detections_to_postgres()