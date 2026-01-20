def test_api_key(api_key_mock):
    assert api_key_mock == "MOCK_KEY1234"

def test_channel_handle(channel_handle_mock):
    assert channel_handle_mock == "MRCHEESE"

def test_mock_postgres_connection(mock_postgres_connection):
    conn=mock_postgres_connection
    assert conn.host == 'mock_host'
    assert conn.schema == 'mock_db'
    assert conn.login == 'mock_user'
    assert conn.password == 'mock_password'
    assert conn.port == 1234

def test_dag_bag(dag_bag):
    #1
    assert dag_bag.import_errors == {}, f"Import errors found: {dag_bag.import_errors}"
    print("============")
    print(dag_bag.import_errors)

    #2
    expected_dag_ids = ['produce_json', 'update_db', 'data_quality']
    actual_dag_ids = list(dag_bag.dags.keys())
    print("============")
    print(actual_dag_ids)

    for dag_id in expected_dag_ids:
        assert dag_id in actual_dag_ids, f"DAG ID '{dag_id}' is missing"
    
    #3
    assert dag_bag.size() == 3
    print("============")
    print(dag_bag.size())

    #4
    expected_task_counts = {
        'produce_json': 5,
        'update_db': 3,
        'data_quality': 2
    }
    print("============")
    for dag_id, dag in dag_bag.dags.items():
        expected_count=expected_task_counts[dag_id]
        actual_count = len(dag.tasks)
        assert actual_count == expected_count, f"DAG ID '{dag_id}' has {actual_count} tasks; expected {expected_count}"
        print(f"DAG ID: {dag_id}, Expected Tasks: {expected_count}, Actual Tasks: {actual_count}")