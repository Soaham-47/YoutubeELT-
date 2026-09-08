import pytest

def test_api_key(api_key_mock):
    assert api_key_mock == "MOCK_KEY1234"

def test_channel_handle(channel_handle_mock):
    assert channel_handle_mock == "MRCHEESE"

def test_mock_snowflake_connection(mock_snowflake_connection):
    conn = mock_snowflake_connection
    assert conn.conn_id == "snowflake_default"
    assert conn.conn_type == "snowflake"
    assert conn.login == "mock_user"
    assert conn.password == "mock_password"
    assert conn.schema == "STAGING"
    assert conn.extra_dejson.get("database") == "YT_ANALYTICS_DB"
    assert conn.extra_dejson.get("warehouse") == "COMPUTE_WH"

def test_dag_bag(dag_bag):
    # 1. No import or parse errors
    assert len(dag_bag.import_errors) == 0, f"Import errors found: {dag_bag.import_errors}"

    # 2. Total DAGs count
    assert dag_bag.size() == 3

    # 3. Expected task counts per DAG
    expected_task_counts = {
        'produce_json': 5,
        'update_db': 3,
        'data_quality': 2
    }

    for dag_id, expected_count in expected_task_counts.items():
        assert dag_id in dag_bag.dags, f"DAG '{dag_id}' missing from DagBag"
        dag = dag_bag.get_dag(dag_id)
        actual_count = len(dag.tasks)
        assert actual_count == expected_count, (
            f"DAG '{dag_id}' has {actual_count} tasks; expected {expected_count}"
        )

def test_produce_json_dependencies(dag_bag):
    """Verifies: get_playlist_id >> get_video_ids >> extract_video_stats >> save_to_json >> trigger_update_db"""
    dag = dag_bag.get_dag('produce_json')

    p_id = dag.get_task('get_playlist_id')
    v_ids = dag.get_task('get_video_ids')
    stats = dag.get_task('extract_video_stats')
    save_json = dag.get_task('save_to_json')
    trigger_update = dag.get_task('trigger_update_db')

    assert v_ids in p_id.downstream_list
    assert stats in v_ids.downstream_list
    assert save_json in stats.downstream_list
    assert trigger_update in save_json.downstream_list


def test_update_db_dependencies(dag_bag):
    """Verifies: staging_table >> core_table >> trigger_data_quality"""
    dag = dag_bag.get_dag('update_db')

    update_staging = dag.get_task('staging_table')
    update_core = dag.get_task('core_table')
    trigger_dq = dag.get_task('trigger_data_quality')

    assert update_core in update_staging.downstream_list
    assert trigger_dq in update_core.downstream_list

def test_data_quality_dependencies(dag_bag):
    """Verifies: soda_validate_staging >> soda_validate_core"""
    dag = dag_bag.get_dag('data_quality')

    soda_staging = dag.get_task('soda_test_staging')
    soda_core = dag.get_task('soda_test_core')

    assert soda_core in soda_staging.downstream_list