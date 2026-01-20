import os
import pytest
from unittest import mock
from airflow.models import Variable,Connection,DagBag
import psycopg2

@pytest.fixture
def api_key_mock(monkeypatch):
    # Set the environment variable using the built-in monkeypatch fixture
    monkeypatch.setenv("AIRFLOW_VAR_API_KEY", "MOCK_KEY1234")
    return Variable.get('API_KEY')

@pytest.fixture
def channel_handle_mock(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_CHANNEL_HANDLE", "MRCHEESE")
    return Variable.get('CHANNEL_HANDLE')

@pytest.fixture
def mock_postgres_connection():
    # Create a mock Postgres connection
    conn = Connection(
        host='mock_host',
        schema='mock_db',
        login='mock_user',
        password='mock_password',
        port=1234
    )
    conn_uri = conn.get_uri()
    with mock.patch.dict("os.environ", AIRFLOW_CONN_POSTGRES_DB_YT_ELT=conn_uri):
        yield Connection.get_connection_from_secrets(conn_id='POSTGRES_DB_YT_ELT')

@pytest.fixture
def dag_bag():
    yield DagBag()

@pytest.fixture
def airflow_variable():
    def get_variable(variable_name, default_value=None):
        env_var = f"AIRFLOW_VAR_{variable_name.upper()}"
        return os.getenv(env_var, default_value)
    return get_variable

@pytest.fixture
def real_postgres_connection():
    dbname=os.getenv("ELT_DATABASE_NAME")
    user=os.getenv("ELT_DATABASE_USERNAME")
    password=os.getenv("ELT_DATABASE_PASSWORD")
    host=os.getenv("POSTGRES_CONN_HOST")
    port=os.getenv("POSTGRES_CONN_PORT")
    
    conn=None
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        yield conn
    except psycopg2.Error as e:
        pytest.fail(f"Failed to connect to the database: {e}")
    finally:
        if conn:
            conn.close()

