##YouTube Data Pipeline (ELT):
A robust, containerized ELT (Extract, Load, Transform) pipeline designed to ingest, process, and validate YouTube channel analytics. This project showcases enterprise-grade data orchestration using Apache Airflow, Docker, and PostgreSQL.

🏗️ Architecture
The pipeline follows a modular 3-DAG (Directed Acyclic Graph) architecture to ensure separation of concerns and reliability:

produce_json: Extracts raw video statistics from the YouTube Data API and persists them as JSON. Scheduled daily at 14:00 IST.

update_db: Triggered upon successful extraction. It parses the JSON data and loads it into a PostgreSQL data warehouse with partitioned staging and core schemas.

data_quality: Triggered after the database update to perform automated validation using Soda, ensuring no null values or schema drifts occur.

🛠️ Tech Stack
Orchestration: Apache Airflow (2.9.2)

Database: PostgreSQL (Staging & Core schemas)

Containerization: Docker & Docker Compose

Data Validation: Soda SQL

Language: Python 3.11+

API: YouTube Data API v3

📂 Database Schema Design
The project implements a clean data layering strategy:

Staging: Temporary landing zone for raw data to minimize transformation overhead on the source.

Core: Production-ready schema with enforced types and constraints for downstream analytics.

🚀 Getting Started
Prerequisites
Docker & Docker Compose

YouTube API Key (Google Cloud Console)

Installation
Clone the repository:

'''Bash
git clone https://github.com/Soaham-47/YoutubeELT-s
cd youtube-elt-pipeline
Environment Setup: Create a .env file and add your credentials:

Code snippet:
# Airflow params 
AIRFLOW_UID="50000"
AIRFLOW_WWW_USER_USERNAME="airflow"
AIRFLOW_WWW_USER_PASSWORD="airflow1234"
FERNET_KEY=generate_using_fernet.py

# Youtube parameters
API_KEY=your_api_key_here 
CHANNEL_HANDLE='MrBeast'

# Postgres connection - POSTGRES_CONN_USERNAME set to the default postgres user to not create another db
POSTGRES_CONN_USERNAME=postgres
POSTGRES_CONN_PASSWORD=your_password
POSTGRES_CONN_HOST=postgres
POSTGRES_CONN_PORT=5432

Spin up the containers:

Bash
docker-compose up -d
Access Airflow UI: Navigate to http://localhost:8080 (Default credentials: admin/admin).

📊 Pipeline Monitoring
Timezone Aware: Scheduled specifically for the Asia/Kolkata timezone to align with Indian business cycles.

Error Handling: Implemented retry logic and Slack/Email notifications (optional) for failed tasks.

Validation: Every run is followed by a Soda scan to guarantee data 100% integrity before it reaches the core layer.