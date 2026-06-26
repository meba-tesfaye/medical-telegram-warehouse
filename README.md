# Medical Telegram Data Warehouse Pipeline

An end-to-end ETL (Extract, Transform, Load) data engineering pipeline designed to securely ingest medical product advertisements, pricing data, and engagement metrics from target Telegram channels, clean the unstructured text, and warehouse it into a queryable relational database.

## 🏗 Data Architecture Flow
1. **Extract (`src/scraper.py`)**: Connects via Telethon API to scrape target channels (`@CheMed123`, `@lobelia4cosmetics`, `@TikvahPharma`), downloading raw message data as JSON files and tracking media assets locally.
2. **Transform (`src/transformer.py`)**: Utilizes Pandas to ingest the raw data lake, clean messy text strings, and execute RegEx filters to extract product pricing metrics (`ETB`/`birr`).
3. **Load (`src/db_loader.py`)**: Maps out a structured schema and pushes the normalized datasets straight into a centralized SQLite relational database (`medical_warehouse.db`).

---

## 🛠 Project Structure
```text
medical-telegram-warehouse/
├── data/
│   ├── raw/                 # Partitioned date folders for JSONs/Images
│   ├── cleaned/             # Consolidated CSV output
│   └── warehouse/           # Persistent SQLite DB
├── src/
│   ├── scraper.py           # Ingestion engine
│   ├── transformer.py       # Data cleansing & regex parsing
│   ├── db_loader.py         # DB schema design & loading
│   └── dashboard_preview.py # SQL analytical KPI engine
├── .env                     # Private API credentials (git-ignored)
├── .gitignore               # Environmental exclusions
└── README.md                # Documentation