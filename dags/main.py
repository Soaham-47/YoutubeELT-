from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import pendulum

# Import your already-decorated tasks
from api.video_stats import (
    extract_video_stats,
    get_playlist_id,
    get_video_ids,
    save_to_json,
)
from dataquality.soda import yt_elt_data_quality
from dataWarehouse.dwh import core_table, staging_table

# Define the timezone
local_tz = pendulum.timezone("Asia/Kolkata")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 21, tzinfo=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Snowflake schemas are uppercase
staging_schema = "STAGING"
core_schema = "CORE"

# DAG 1: YouTube Extraction
with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='DAG to extract YouTube video statistics and save to JSON',
    schedule='0 14 * * *',
    catchup=False,
    tags=['youtube', 'etl'],
) as dag_produce:

    p_id = get_playlist_id()
    v_ids = get_video_ids(p_id)
    stats = extract_video_stats(v_ids)
    save_to_json_task = save_to_json(stats)

    trigger_update_db = TriggerDagRunOperator(
        task_id='trigger_update_db',
        trigger_dag_id='update_db',
    )

    p_id >> v_ids >> stats >> save_to_json_task >> trigger_update_db

# DAG 2: Warehouse Update
with DAG(
    dag_id='update_db',
    default_args=default_args,
    description='DAG to update staging and core tables in Snowflake data warehouse',
    catchup=False,
    schedule=None,
    tags=['dwh', 'snowflake'],
) as dag_update:

    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id='trigger_data_quality',
        trigger_dag_id='data_quality',
    )

    update_staging >> update_core >> trigger_data_quality

# DAG 3: Data Quality Checks
with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='DAG to perform data quality checks using Soda',
    catchup=False,
    schedule=None,
    tags=['dwh'],
) as dag_quality:

    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    soda_validate_staging >> soda_validate_core