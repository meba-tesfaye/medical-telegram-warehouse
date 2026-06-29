# Medical Telegram Data Warehouse & AI Pipeline

An end-to-end data engineering, computer vision, and AI-driven retrieval pipeline designed to securely ingest medical product advertisements, images, and telemetry data from target Ethiopian Telegram channels, clean the unstructured inputs, warehouse them into a queryable PostgreSQL dimensional data mart using dbt, visualize operational insights via Power BI, and query data using a semantic RAG chatbot interface.

---

## 🏗 Data Architecture Flow

1. **Extract, Load & Vision (`src/`)**: 
   * `scraper.py`: Connects via Telethon API to scrape target channels (`@CheMed123`, `@lobelia4cosmetics`, `@TikvahPharma`), saving raw payloads and media.
   * `yolo_detect.py`: Deploys a **YOLOv8** object detection model (`yolov8n.pt`) over ingested media streams to automatically extract medical product metadata, equipment arrays, and operational bounding logs.
   * `db_loader.py`: Connects to a local PostgreSQL instance via `psycopg2` to ingest the raw staging text data and computer vision logs safely with robust error-handling safeguards.
2. **Transform (`dbt_medical_warehouse/`)**:
   * Uses **dbt (Data Build Tool)** to execute sequential SQL transformations directly inside PostgreSQL under a dedicated `main` schema.
   * Cleans messy text strings, parses currency metrics (`ETB`/`birr`), and maps data structures into an optimized, unified **Star Schema** dimensional layer (`marts/`).
3. **Business Intelligence Analytics (Power BI)**:
   * Establishes a native relational gateway link directly to the clean dbt schemas.
   * Standardizes active $1 \rightarrow *$ relationship chains connecting a master channel dimension table out to transactional fact layers to enable deep dynamic cross-filtering.
4. **Semantic AI Interface (RAG Engine)**:
   * Pipelines real-time warehouse data from the `main` schema into memory vectors using the `all-MiniLM-L6-v2` Sentence-Transformer architecture.
   * Indexes embedded tokens into a localized **FAISS** database layout (`IndexFlatL2`) to anchor a terminal chat interface using natural language questions.

---

## 🛠 Project Structure

```text
medical-telegram-warehouse/
├── data/
│   ├── raw/                  # Partitioned folders for raw media/JSON payloads
│   └── cleaned/              # Intermediary backup tracking files
├── src/
│   ├── scraper.py            # Telegram API client ingestion engine
│   ├── transformer.py        # Python utility for local regex testing
│   ├── yolo_detect.py        # YOLOv8 object detection processing engine
│   ├── db_loader.py          # PostgreSQL staging data loading & upsert engine
│   └── rag_search.py         # Semantic vector indexer and interactive RAG chat interface
├── dbt_medical_warehouse/    # dbt Core Root Project
│   ├── models/
│   │   ├── staging/          # Staging views representing raw ingestion schemas (stg_telegram_messages)
│   │   └── marts/            # Production Dimensional Mart Layer (fct_ and dim_)
│   │       ├── dim_channels.sql          # Master managed channel dimension entity
│   │       ├── fct_medical_alerts.sql    # Organic vs. commercial ad telemetry metrics
│   │       ├── fct_image_detections.sql  # YOLO computer vision detection records
│   │       └── schema.yml    # Schema test assertions (unique, not_null, constraints)
│   ├── tests/                # Custom data validation SQL test scripts
│   ├── dbt_project.yml       # dbt project architecture configs
│   └── profiles.yml          # Warehouse connection routing profile
├── yolov8n.pt                # Trained computer vision weight thresholds
├── .env                      # Database & API environment flags (Git-ignored)
├── .gitignore                # Repository exception mappings
├── requirements.txt          # Explicit production package dependencies
└── README.md                 # System documentation