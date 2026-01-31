# YouTube Analytics ELT Pipeline

A robust, containerized ELT (Extract, Load, Transform) pipeline designed to ingest, process, and validate YouTube channel analytics. This project demonstrates enterprise-grade data orchestration, focusing on **idempotency**, **data quality**, and **modular architecture**.

## System Architecture

The pipeline utilizes a decoupled **3-DAG architecture** to ensure high reliability and clear separation of concerns:

1.  **`produce_json`**: Interacts with the **YouTube Data API v3** to extract raw video metrics. Data is persisted as localized JSON files to act as a landing buffer. 
    * *Schedule:* Daily at 14:00 IST.
2.  **`update_db`**: Triggered automatically upon extraction success. It handles the transformation logic and loads data into a **PostgreSQL** warehouse using a multi-layered schema approach.
3.  **`data_quality`**: The final gatekeeper. Executes automated **Soda SQL** scans to detect null values, schema drift, or volume anomalies before the data is marked as "Production Ready."

---

## Tech Stack

| Component | Technology |
| :--- | :--- |
| **Orchestration** | Apache Airflow 2.9.2 |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL (Staging & Core layers) |
| **Containerization** | Docker & Docker Compose |
| **Data Validation** | Soda SQL |
| **Source** | YouTube Data API v3 |

---

##  Database Schema Design

The project implements a **Medallion-lite** architecture to ensure data integrity:

* **Staging Schema**: A temporary landing zone where data is kept in its near-raw state. This minimizes transformation overhead on the source API and allows for easy re-runs.
* **Core Schema**: The production-ready warehouse. It features enforced data types, primary keys, and constraints optimized for downstream BI tools or ML models.

---

##  Getting Started

### Prerequisites
* Docker & Docker Compose installed.
* A Google Cloud Project with the **YouTube Data API v3** enabled and an API Key generated.

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Soaham-47/YoutubeELT-s](https://github.com/Soaham-47/YoutubeELT-s)
   cd youtube-elt-pipeline
   pip install -r requirements.txt
2. **Environment Configuration:**
Create a .env file in the root directory.

Airflow Configuration:
AIRFLOW_UID=50000,
FERNET_KEY=your_generated_key,
AIRFLOW_WWW_USER_USERNAME="airflow",
AIRFLOW_WWW_USER_PASSWORD="airflow1234"

YouTube API Configuration:
API_KEY=your_youtube_api_key,
CHANNEL_HANDLE='MrBeast',

Database Configuration:
POSTGRES_CONN_USERNAME=postgres,
POSTGRES_CONN_PASSWORD=your_secure_password,
POSTGRES_CONN_HOST=postgres,
POSTGRES_CONN_PORT=5432,

3.**Launch the Pipeline:**

'''Bash
docker-compose up -d
Access the Airflow UI at http://localhost:8080(after waiting for 60 sec for the containers to run)

## Monitoring & Reliability
Timezone Awareness: Configured for Asia/Kolkata to align with Indian business cycles.

Data Integrity: Integrated Soda SQL ensures 100% schema compliance. If a scan fails, the pipeline halts, preventing "bad data" from reaching the Core layer.

Error Handling: Implemented retry logic and task-level monitoring to handle API rate limits or network hiccups gracefully.