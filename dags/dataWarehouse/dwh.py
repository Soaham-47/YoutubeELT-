import logging
import os
import sys
from airflow.decorators import task

# Get the absolute path of the directory containing main.py (the dags folder)
dag_path = os.path.dirname(os.path.abspath(__file__))

# Add the dags folder and its subfolders to the python path
if dag_path not in sys.path:
    sys.path.insert(0, dag_path)
    sys.path.insert(0, os.path.join(dag_path, 'api'))
    sys.path.insert(0, os.path.join(dag_path, 'dataWarehouse'))

from dataWarehouse.data_loading import load_data
from dataWarehouse.data_modifications import (
    delete_rows,
    insert_rows,
    update_rows,
)
from dataWarehouse.data_transformations import transform_data
from dataWarehouse.data_utils import (
    close_conn_cursor,
    create_schema,
    create_table,
    get_conn_cursor,
    get_video_ids,
)

logger = logging.getLogger(__name__)
TABLE = "YT_API"


@task
def staging_table():
    schema = "STAGING"
    conn, cursor = None, None
    try:
        conn, cursor = get_conn_cursor()
        YT_data = load_data()
        create_schema(schema)
        create_table(schema)
        table_ids = get_video_ids(cursor, schema)

        for row in YT_data:
            if row['video_id'] in table_ids:
                update_rows(conn, cursor, schema, row)
            else:
                insert_rows(conn, cursor, schema, row)

        ids_in_json = set(row['video_id'] for row in YT_data)
        ids_to_delete = table_ids - ids_in_json
        if ids_to_delete:
            delete_rows(conn, cursor, schema, ids_to_delete)

        logger.info(f"Staging table {schema}.{TABLE} updated successfully.")

    except Exception as e:
        logger.error(f"Error in staging_table task: {e}")
        raise e
    finally:
        if conn and cursor:
            close_conn_cursor(conn, cursor)


@task
def core_table():
    schema = "CORE"
    conn, cursor = None, None
    try:
        conn, cursor = get_conn_cursor()
        create_schema(schema)
        create_table(schema)
        table_ids = get_video_ids(cursor, schema)

        # Select from uppercase STAGING schema and YT_API table
        cursor.execute(f"SELECT * FROM STAGING.{TABLE};")
        staging_rows = cursor.fetchall()

        for row in staging_rows:
            transformed_row = transform_data(row)
            if transformed_row['Video_id'] in table_ids:
                update_rows(conn, cursor, schema, transformed_row)
            else:
                insert_rows(conn, cursor, schema, transformed_row)

        logger.info(f"Core table {schema}.{TABLE} updated successfully.")

    except Exception as e:
        logger.error(f"Error in core_table task: {e}")
        raise e
    finally:
        if conn and cursor:
            close_conn_cursor(conn, cursor)
