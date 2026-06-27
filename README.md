# Medical Telegram Data Warehouse Pipeline

An end-to-end ELT (Extract, Load, Transform) data engineering pipeline designed to securely ingest medical product advertisements, pricing data, and engagement metrics from target Telegram channels, clean the unstructured text, and warehouse it into a queryable PostgreSQL dimensional data mart using dbt.

---

## 🏗 Data Architecture Flow

1. **Extract & Load (`src/`)**: 
   * `scraper.py`: Connects via Telethon API to scrape target channels (`@CheMed123`, `@lobelia4cosmetics`, `@TikvahPharma`), saving raw payloads partitioned by date.
   * `db_loader.py`: Connects to a local/remote PostgreSQL instance via `psycopg2` to ingest the raw staging data safely with robust error-handling safeguards.
2. **Transform (`dbt_medical_warehouse/`)**:
   * Uses **dbt (Data Build Tool)** to execute sequential SQL transformations directly inside PostgreSQL.
   * Cleans messy text strings, parses currency metrics (`ETB`/`birr`), and maps data structures into an optimized **Star Schema** dimensional layer (`marts/`).
3. **Data Quality Framework (`tests/`)**:
   * Executes continuous automated checks via dbt testing layers (schema declarations and custom data integrity scripts) to validate strict constraints before analytical serving.

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
│   └── db_loader.py          # PostgreSQL staging data loading & upsert engine
├── dbt_medical_warehouse/    # dbt Core Root Project
│   ├── models/
│   │   ├── staging/          # Staging views representing raw ingestion schemas
│   │   └── marts/            # Production Dimensional Mart Layer (fct_ and dim_)
│   │       └── schema.yml    # Schema test assertions (unique, not_null, constraints)
│   ├── tests/                # Custom data validation SQL test scripts
│   ├── dbt_project.yml       # dbt project architecture configs
│   └── profiles.yml          # Warehouse connection routing profile
├── .env                      # Database & API environment flags (Git-ignored)
├── .gitignore                # Repository exception mappings
├── requirements.txt          # Explicit production package dependencies
└── README.md                 # System documentation