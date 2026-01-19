from airflow import DAG
import pendulum
from datetime import datetime, timedelta
# Import your already-decorated tasks
from api.video_stats import get_playlist_id, get_video_ids, extract_video_stats, save_to_json
from dataWarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality
# Define the timezone
local_tz = pendulum.timezone("Asia/Kolkata")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 20, tzinfo=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

staging_schema="staging"
core_schema="core"

# DAG 1: YouTube Extraction
with DAG(
    dag_id='youtube_video_stats_dag',
    default_args=default_args,
    description='DAG to extract YouTube video statistics and save to JSON',
    schedule='0 14 * * *',
    catchup=False,
    tags=['youtube', 'etl']
) as dag1:
    
    # Because these are @task decorated, calling them creates the task instance
    p_id = get_playlist_id()
    v_ids = get_video_ids(p_id)
    stats = extract_video_stats(v_ids)
    save_to_json_task = save_to_json(stats)

    # Dependencies are automatically handled by passing variables (p_id -> v_ids)
    # But you can still be explicit:
    p_id >> v_ids >> stats >> save_to_json_task

# DAG 2: Warehouse Update
with DAG(
    dag_id='update_data_warehouse_dag',
    default_args=default_args,
    description='DAG to update staging and core tables in the data warehouse',
    schedule='0 15 * * *',
    catchup=False,
    tags=['dwh']
) as dag2:
    
    # Call the decorated tasks
    update_staging = staging_table()
    update_core = core_table()

    # Define explicit dependency
    update_staging >> update_core

# DAG 3: Data Quality Checks
with DAG(
    dag_id='data_quality_dag',
    default_args=default_args,
    description='DAG to perform data quality checks using Soda',
    schedule='0 16 * * *',
    catchup=False,
    tags=['dwh']
) as dag2:
    
    # Call the decorated tasks
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Define explicit dependency
    soda_validate_staging >> soda_validate_core