from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from snowflake.connector import DictCursor

DB = "YT_ANALYTICS_DB"
TABLE = "YT_API"
CONN_ID = "snowflake_default"


def get_conn_cursor():
    hook = SnowflakeHook(snowflake_conn_id=CONN_ID)
    conn = hook.get_conn()
    cursor = conn.cursor(DictCursor)
    cursor.execute(f'USE DATABASE "{DB}";')
    return conn, cursor


def close_conn_cursor(conn, cursor):
    cursor.close()
    conn.close()


def create_schema(schema):
    schema = schema.upper()
    conn, cursor = get_conn_cursor()
    schema_sql = f'CREATE SCHEMA IF NOT EXISTS "{DB}"."{schema}";'
    cursor.execute(schema_sql)
    conn.commit()
    close_conn_cursor(conn, cursor)


def create_table(schema):
    schema = schema.upper()
    conn, cursor = get_conn_cursor()

    if schema == "STAGING":
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS "{DB}"."{schema}".{TABLE} (
                "Video_id" VARCHAR(50),
                "Video_title" VARCHAR(500),
                "Published_at" TIMESTAMP_NTZ,
                "Duration" VARCHAR(50),
                "View_count" NUMBER(38,0),
                "Like_count" NUMBER(38,0),
                "Comment_count" NUMBER(38,0)
            );
        """
    else:
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS "{DB}"."{schema}".{TABLE} (
                "Video_id" VARCHAR(50),
                "Video_title" VARCHAR(500),
                "Published_at" TIMESTAMP_NTZ,
                "Duration" VARCHAR(50),
                "Video_type" VARCHAR(50),
                "View_count" NUMBER(38,0),
                "Like_count" NUMBER(38,0),
                "Comment_count" NUMBER(38,0)
            );
        """
    cursor.execute(table_sql)
    conn.commit()
    close_conn_cursor(conn, cursor)


def get_video_ids(cursor, schema):
    schema = schema.upper()
    cursor.execute(f'SELECT "Video_id" FROM "{DB}"."{schema}".{TABLE};')
    ids = cursor.fetchall()
    video_ids = {row["Video_id"] for row in ids}
    return video_ids