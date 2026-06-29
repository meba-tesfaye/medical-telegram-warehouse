# Medical Telegram Data Warehouse & Orchestration Pipeline

An end-to-end data engineering, computer vision, and automated orchestration pipeline built to securely ingest medical product data from target Ethiopian Telegram channels, enrich visual content using machine learning, transform unstructured telemetry into a queryable relational Star Schema, and expose analytic datasets via a production API layer.

---

## 🏗 Data Architecture Flow

1. **Data Ingestion & Extraction (Task 1 & 2)**: 
   * Connects via the Telethon API (`src/scraper.py`) to extract media strings and raw message payloads from target channels (`@CheMed123`, `@lobelia4cosmetics`, `@TikvahPharma`).
2. **Data Enrichment with YOLOv8 (Task 3)**:
   * Deploys a **YOLOv8** computer vision pipeline (`src/yolo_detect.py`) over unstructured image binaries to identify product classifications (e.g., medical bottles) and log detection frequencies.
3. **Staging & dbt Star Schema Transformations (Task 1 & 2)**:
   * Batches raw rows into a localized PostgreSQL instance via `src/db_loader.py`.
   * Leverages **dbt (Data Build Tool)** to execute staging formatting (`stg_telegram_messages`) and materialize a clean, high-performance dimensional layer (`dim_channels`, `fct_medical_alerts`, `fct_image_detections`).
4. **Analytical Service API Layer (Task 4)**:
   * Serves an interactive backend using **FastAPI** (`src/api_server.py`) to expose multi-dimensional warehouse assets directly over structured JSON endpoints.
5. **Data Pipeline Orchestration (Task 5)**:
   * Monitored entirely through a centralized **Dagster** asset lineage workflow graph (`src/orchestrator.py`), enforcing automated data quality checks and execution dependencies.

---

## 🛠 Project Structure

```text
medical-telegram-warehouse/
├── data/
│   ├── raw/                  # Partitioned folders for raw media/JSON payloads
│   └── cleaned/              # Intermediary backup tracking files
├── src/
│   ├── scraper.py            # Telegram API client ingestion engine (Task 1 & 2)
│   ├── yolo_detect.py        # YOLOv8 object detection processing engine (Task 3)
│   ├── db_loader.py          # PostgreSQL staging data loading engine (Task 1 & 2)
│   ├── api_server.py         # FastAPI Analytical endpoint server (Task 4)
│   └── orchestrator.py       # Dagster Pipeline asset orchestration graph (Task 5)
├── dbt_medical_warehouse/    # dbt Core Root Transformation Directory
│   ├── models/
│   │   ├── staging/          # Ingestion cleaning layer views (stg_telegram_messages)
│   │   └── marts/            # Production Dimensional Star Schema (fct_ and dim_)
│   │       ├── dim_channels.sql          # Master managed channel dimension entity
│   │       ├── fct_medical_alerts.sql    # Organic vs. commercial ad telemetry metrics
│   │       └── fct_image_detections.sql  # YOLO computer vision detection records
│   ├── tests/                # Custom data validation SQL test scripts
│   ├── dbt_project.yml       # dbt project architecture configs
│   └── profiles.yml          # Warehouse connection routing profile
├── yolov8n.pt                # Computer Vision trained threshold weights
├── .env                      # Relational connection & system API parameters
├── requirements.txt          # Explicit production package dependencies
└── README.md                 # System documentation