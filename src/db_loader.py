import os
import sqlite3
import pandas as pd

# Define paths
CSV_FILE = "data/cleaned/cleaned_medical_data.csv"
DB_DIR = "data/warehouse"
DB_FILE = os.path.join(DB_DIR, "medical_warehouse.db")

def load_to_warehouse():
    print("🛢 Kicking off Database Ingestion Pipeline...")
    
    # 1. Verify clean CSV data exists
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: Clean data file {CSV_FILE} not found! Run transformer.py first.")
        return
        
    # Read the clean data
    df = pd.read_csv(CSV_FILE)
    
    # 2. Setup Warehouse Directory & Database Connection
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 3. Design Structured Relational Schema
    print("📐 Constructing structured warehouse table schema...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER UNIQUE,
            channel TEXT,
            message_date TEXT,
            cleaned_text TEXT,
            extracted_price_etb REAL,
            has_media INTEGER,
            image_path TEXT,
            views INTEGER,
            forwards INTEGER,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 4. Ingest and Stream rows into SQLite
    print(f"📥 Loading {len(df)} records into warehouse table...")
    
    # Convert has_media boolean explicitly to 1 or 0 for database mapping
    df['has_media'] = df['has_media'].astype(int)
    
    # Use pandas to append/replace rows neatly inside the relational DB
    df.to_sql("telegram_messages", conn, if_exists="replace", index=False)
    
    # Commit changes and secure verification counts
    conn.commit()
    
    # Verify records exist by running a direct SQL statement
    cursor.execute("SELECT COUNT(*) FROM telegram_messages;")
    total_rows = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"🎉 Success! Database built safely at: {DB_FILE}")
    print(f"📊 Total verified rows active in warehouse: {total_rows}")

if __name__ == "__main__":
    load_to_warehouse()