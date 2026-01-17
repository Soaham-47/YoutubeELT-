from airflow import DAG
import pendulum
from datetime import datetime,timedelta
from api.video_stats import get_playlist_id, get_video_ids,extract_video_stats,save_to_json

local_tz=pendulum.timezone("Asia/Kolkata")

default_args={
    'owner':'airflow',
    'depends_on_past':False,
    'email_on_failure':False,
    'email_on_retry':False,
    'start_date':datetime(2025,6,20, tzinfo=local_tz),
    # 'retries':1,
    # 'retry_delay':timedelta(minutes=5),
    'max_active_runs':1,
    'dagrun_timeout':timedelta(minutes=60)
}

with DAG(
    dag_id='youtube_video_stats_dag',
    default_args=default_args,
    description='A DAG to extract YouTube video statistics and save to JSON',
    schedule='0 14 * * *',
    catchup=False,
    tags=['youtube','video','stats','etl']
) as dag:
    
    #define tasks
    playlist_id = get_playlist_id()
    
    if not playlist_id:
        print("Could not retrieve playlist ID.")
    
    video_ids = get_video_ids(playlist_id)
    
    if not video_ids:
        print("No videos found in playlist")
    
    extracted_data = extract_video_stats(video_ids)

    if not extracted_data:
        print("No data was successfully extracted")

    save_to_json_task=save_to_json(extracted_data)

    #define task dependencies
    playlist_id >> video_ids >> extracted_data >> save_to_json_task
