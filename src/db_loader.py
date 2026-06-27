import os
import csv
import logging
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# 1. Setup Logging Production Guardrails
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_execution.log"),
        logging.StreamHandler()
    ]
)

# 2. Load environment configurations
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "medical_warehouse")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """Establishes a secure connection pool handshake with PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection initialization failed: {e}")
        raise e

def initialize_staging_table(cursor):
    """Creates the raw landing layer with strict constraints."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS staging_telegram_alerts (
        message_id BIGINT PRIMARY KEY,
        channel_name VARCHAR(100) NOT NULL,
        message_text TEXT,
        cleaned_text TEXT,
        extracted_price_etb NUMERIC,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)

def load_cleaned_data_to_postgres(csv_file_path):
    """Ingests clean CSV logs and performs transactional upserts into Postgres."""
    if not os.path.exists(csv_file_path):
        logging.warning(f"Target payload file not found at path: {csv_file_path}. Skipping batch.")
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            initialize_staging_table(cursor)
            
            # Upsert query template utilizing ON CONFLICT DO UPDATE (deduplication)
            upsert_query = """
            INSERT INTO staging_telegram_alerts (message_id, channel_name, message_text, cleaned_text, extracted_price_etb, scraped_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) 
            DO UPDATE SET 
                cleaned_text = EXCLUDED.cleaned_text,
                extracted_price_etb = EXCLUDED.extracted_price_etb,
                scraped_at = EXCLUDED.scraped_at;
            """
            
            success_count = 0
            with open(csv_file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Map keys safely; handle missing pricing data cleanly
                        price_val = row.get('extracted_price_etb') or row.get('price')
                        if price_val == '' or price_val is None:
                            price_val = None
                        else:
                            try:
                                price_val = float(price_val)
                            except ValueError:
                                price_val = None

                        cursor.execute(upsert_query, (
                            int(row.get('message_id') or row.get('id')),
                            row.get('channel_name') or row.get('channel'),
                            row.get('message_text') or row.get('text'),
                            row.get('cleaned_text') or row.get('cleaned'),
                            price_val,
                            row.get('scraped_at') or datetime.now().isoformat()
                        ))
                        success_count += 1
                    except Exception as row_error:
                        logging.error(f"Skipping corrupt record row entry: {row_error}")
                        continue
            
            conn.commit()
            logging.info(f"Successfully processed CSV batch. Ingested/Updated {success_count} rows into PostgreSQL.")
            
    except Exception as batch_error:
        conn.rollback()
        logging.error(f"Transactional batch processing failed radically. Rolled back changes. Error: {batch_error}")
    finally:
        conn.close()

if __name__ == "__main__":
    SAMPLE_CLEANED_DATA = "data/cleaned/cleaned_medical_data.csv"
    logging.info("Starting Python Data Ingestion Service Engine...")
    load_cleaned_data_to_postgres(SAMPLE_CLEANED_DATA)