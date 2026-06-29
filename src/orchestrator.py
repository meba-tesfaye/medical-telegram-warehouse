import subprocess
from dagster import asset, Definitions

@asset(description="Extract step: Scrape data from target Telegram channels via Telethon API.")
def telegram_raw_data():
    print("[DAGSTER] Starting step: Ingesting raw Telegram payloads...")
    # This invokes your source scraping script safely
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARNING/ERROR] Scraper log details: {result.stderr}")
    return "Raw ingestion logs finalized."

@asset(
    deps=[telegram_raw_data],
    description="Enrichment step: Deploy YOLOv8 over media files to extract product matrices."
)
def yolo_image_enrichment():
    print("[DAGSTER] Starting step: Extracting product matrices via YOLOv8 computer vision...")
    result = subprocess.run(["python", "src/yolo_detect.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARNING/ERROR] YOLO log details: {result.stderr}")
    return "YOLO computer vision arrays extracted."

@asset(
    deps=[yolo_image_enrichment],
    description="Load step: Pipeline strings and computer vision metadata logs straight to PostgreSQL."
)
def postgres_warehouse_load():
    print("[DAGSTER] Starting step: Syncing staging records to PostgreSQL warehouse...")
    result = subprocess.run(["python", "src/db_loader.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[WARNING/ERROR] DB Loader log details: {result.stderr}")
    return "Database loads finalized."

@asset(
    deps=[postgres_warehouse_load],
    description="Transform step: Trigger dbt models inside the data warehouse."
)
def dbt_warehouse_transformations():
    print("[DAGSTER] Starting step: Triggering dbt star-schema model generation...")
    # Adjust path mapping context to target your dbt Core directory explicitly
    result = subprocess.run(["dbt", "run"], cwd="dbt_medical_warehouse", capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"dbt build sequence failed: {result.stderr}")
    return "dbt Star Schema modeling structures initialized successfully."

# Combine assets into a single cohesive system definition mapping structure
defs = Definitions(
    assets=[
        telegram_raw_data, 
        yolo_image_enrichment, 
        postgres_warehouse_load, 
        dbt_warehouse_transformations
    ]
)