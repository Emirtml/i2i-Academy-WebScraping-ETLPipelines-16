#i2i-Academy-WebScraping&ETLPipelines-16
# End-to-End Web Scraping & ETL Data Pipeline

An automated, standalone, end-to-end data pipeline natively built in Python that interacts with a containerized PostgreSQL infrastructure. This project demonstrates industrial best practices in web scraping, structured data transformation, idempotent database storage, and structured execution logging.

---

## 📌 Project Overview

The objective of this project is to build a reliable and robust ETL (Extract, Transform, Load) pipeline to ingest unstructured data from the web, apply strict data-cleaning rules, and safely load the structured information into a relational database running inside a Docker container. 

The target data source is a live book catalog platform (`books.toscrape.com`). The pipeline extracts real-time book metadata, addresses encoding variations, standardizes data types, ensures strict data integrity, and implements an upsert mechanism to guarantee pipeline idempotency.

---

## 🏗️ System Architecture

The workflow follows the standard three-layer data engineering architecture:

1. **Extraction (Web Scraper):** Programmatically fetches raw HTML using `Requests` and parses structural data across items using `BeautifulSoup`.
2. **Transformation (Data Cleaning):** Loads unstructured data into a `Pandas` DataFrame, applies Regular Expressions (Regex) to purge encoding anomalies, standardizes formats, and appends metadata.
3. **Loading (Database Storage):** Establishes an active gateway via `SQLAlchemy` to load data into a containerized `PostgreSQL` engine running on a custom localized port.

---

## 🛠️ Tech Stack & Key Libraries

* **Core Language:** Python 3.12+
* **Data Extraction:** BeautifulSoup4, Requests
* **Data Manipulation:** Pandas
* **Database Driver & ORM Engine:** SQLAlchemy, Psycopg2-binary
* **Infrastructure Containerization:** Docker, Docker Compose
* **Database Engine:** PostgreSQL 16

---

## 📈 Detailed Pipeline Stages

### 1. Data Extraction
The extraction layerTargets a live public sandbox catalog. It safely navigates the DOM structure to capture three distinct entity fields:
* **Product Name (Title):** Extracted from the structural anchor properties.
* **Price:** Extracted as a raw string currency representation.
* **Availability State:** Captured from structural text blocks and trimmed of formatting whitespace.

### 2. Data Transformation
Raw web elements are frequently dirty and loosely typed. The transformation stage resolves these issues before ingestion:
* **Regex Cleaning:** Web requests frequently capture byte order marks or corrupted characters (e.g., converting `£` anomalies like `Â51.77`). A strict numerical regex (`r'[^\d.]'`) eliminates everything except digits and decimal points.
* **Type Casting:** Prices are safely cast from `String` to numerical `Float` to support mathematical calculations.
* **Data Quality Check:** A `.dropna()` filter actively drops any records missing essential fields.
* **Execution Timestamping:** Every row is stamped with a precise execution `datetime` mark to track ingestion historical lineages.

### 3. Containerized Infrastructure & Idempotency
To prevent local operating system port pollution, PostgreSQL is deployed inside an isolated Docker container mapped to port `5433`. 

Database storage is engineered around the principle of **Idempotency** (ensuring that running the pipeline multiple times produces the same stable state without multiplying records):
* **Schema Constraints:** The `title` column is designated as the table's `PRIMARY KEY`.
* **UPSERT Logic:** Instead of crashing or writing duplicate rows on consecutive script runs, the engine executes an `ON CONFLICT (title) DO UPDATE` instruction. If a book already exists, its pricing, availability, and ingestion timestamp are instantly updated to the newest version.

---

## 🚀 How to Set Up and Run

Follow these step-by-step instructions to initialize and run the pipeline on your local environment:

### Prerequisites
* Ensure Python 3.12 or newer is installed.
* Ensure Docker Desktop is installed and running in the background.

### Step 1: Clone the Repository
```bash
git clone [https://github.com/Emirtml/i2i-Academy-WebScraping-ETLPipelines-16.git](https://github.com/Emirtml/i2i-Academy-WebScraping-ETLPipelines-16.git)
cd i2i-Academy-WebScraping-ETLPipelines-16
