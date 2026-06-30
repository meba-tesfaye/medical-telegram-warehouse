from dagster import (
    AssetSelection,
    Definitions,
    define_asset_job,
    ScheduleDefinition,
    asset
)

# ------------------------------------------------------------------
# 1. Pipeline Asset Stubs (Connected to your actual internal logic)
# ------------------------------------------------------------------

@asset(compute_kind="python", description="Extract step: Scrape data from target Telegram channels")
def telegram_raw_data():
    # Your Telethon scraping execution logic goes here
    print("Scraping Telegram channels...")
    pass

@asset(deps=[telegram_raw_data], compute_kind="yolov8", description="Enrichment step: Deploy YOLOv8 over media files")
def yolo_image_enrichment():
    # Your object detection engine logic goes here
    print("Running YOLOv8 enrichment...")
    pass

@asset(deps=[yolo_image_enrichment], compute_kind="postgresql", description="Load step: Pipeline strings and computer vision metrics into DB")
def postgres_warehouse_load():
    # Your database batch loading logic goes here
    print("Loading data to PostgreSQL...")
    pass

@asset(deps=[postgres_warehouse_load], compute_kind="dbt", description="Transform step: Trigger dbt models inside the warehouse")
def dbt_warehouse_transformations():
    # Your dbt run execution logic goes here
    print("Executing dbt core transformations...")
    pass


# ------------------------------------------------------------------
# 2. Automation: Job & Cadence Scheduling Definition (Task 5 Fix)
# ------------------------------------------------------------------

# Group all pipeline assets into an executable automation block
medical_pipeline_job = define_asset_job(
    name="medical_pipeline_job",
    selection=AssetSelection.all()
)

# Define a daily cron cadence execution trigger (runs every day at midnight)
daily_pipeline_schedule = ScheduleDefinition(
    name="daily_medical_pipeline_schedule",
    job=medical_pipeline_job,
    cron_schedule="0 0 * * *",
    execution_timezone="Africa/Addis_Ababa"
)


# ------------------------------------------------------------------
# 3. Top-Level Definitions Register
# ------------------------------------------------------------------

defs = Definitions(
    assets=[
        telegram_raw_data, 
        yolo_image_enrichment, 
        postgres_warehouse_load, 
        dbt_warehouse_transformations
    ],
    jobs=[medical_pipeline_job],
    schedules=[daily_pipeline_schedule]  # <--- CRITICAL: Registers the automated calendar cadence
)