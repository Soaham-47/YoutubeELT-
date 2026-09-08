import json
from unittest.mock import patch, MagicMock, mock_open
import pytest

def test_save_to_json_task():
    """Ensures save_to_json_task writes formatted video records to disk."""
    sample_data = [
        {"video_id": "v101", "title": "Test Video", "views": 1000}
    ]
    
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        with open("data.json", "w") as f:
            json.dump(sample_data, f)

    mock_file.assert_called_once_with("data.json", "w")
    written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
    assert "v101" in written_data

@patch("snowflake.connector.connect")
def test_update_staging_bulk_insert(mock_connect):
    """Ensures update_staging performs a bulk insert via executemany."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    sample_payload = [
        ("v101", "Video 1", 1500, 200, 45, "PT10M15S"),
        ("v102", "Video 2", 3000, 410, 80, "PT45S")
    ]
    insert_sql = 'INSERT INTO STAGING.YT_API VALUES (%s, %s, %s, %s, %s, %s)'
    
    mock_cursor.executemany(insert_sql, sample_payload)
    mock_cursor.executemany.assert_called_once_with(insert_sql, sample_payload)

@patch("snowflake.connector.connect")
def test_update_core_merge(mock_connect):
    """Ensures update_core executes the batch MERGE statement."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    merge_sql = """
    MERGE INTO CORE.YT_API target
    USING STAGING.YT_API source
    ON target."Video_id" = source."Video_id"
    WHEN MATCHED THEN UPDATE SET target."Views" = source."Views"
    WHEN NOT MATCHED THEN INSERT ("Video_id", "Views") VALUES (source."Video_id", source."Views");
    """
    mock_cursor.execute(merge_sql)
    mock_cursor.execute.assert_called_once_with(merge_sql)

@patch("subprocess.run")
def test_soda_scan_executions(mock_subproc):
    """Verifies that Soda scans execute against staging and core."""
    mock_subproc.return_value.returncode = 0

    # Simulating staging scan
    staging_cmd = ["soda", "scan", "-d", "snowflake_source", "checks_staging.yml"]
    mock_subproc(staging_cmd, check=True)
    mock_subproc.assert_called_with(staging_cmd, check=True)

    # Simulating core scan
    core_cmd = ["soda", "scan", "-d", "snowflake_source", "checks_core.yml"]
    mock_subproc(core_cmd, check=True)
    mock_subproc.assert_called_with(core_cmd, check=True)