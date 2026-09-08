import os
import pytest
from airflow.models import DagBag, Connection

@pytest.fixture
def api_key_mock(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "MOCK_KEY1234")
    return "MOCK_KEY1234"

@pytest.fixture
def channel_handle_mock(monkeypatch):
    monkeypatch.setenv("CHANNEL_HANDLE", "MRCHEESE")
    return "MRCHEESE"

@pytest.fixture
def mock_snowflake_connection():
    """Mocks Airflow Connection object for Snowflake."""
    conn = Connection(
        conn_id="snowflake_default",
        conn_type="snowflake",
        login="mock_user",
        password="mock_password",
        schema="STAGING",
        extra={
            "account": "xy12345.us-east-1",
            "warehouse": "COMPUTE_WH",
            "database": "YT_ANALYTICS_DB",
            "role": "ACCOUNTADMIN",
        }
    )
    return conn

@pytest.fixture(scope="session")
def dag_bag():
    """Loads all Airflow DAGs from your dags folder."""
    dag_folder = os.path.join(os.path.dirname(__file__), "../dags")
    return DagBag(dag_folder=dag_folder, include_examples=False)

