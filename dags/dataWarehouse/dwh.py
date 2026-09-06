import logging
import os
import sys
from airflow.decorators import task

dag_path = os.path.dirname(os.path.abspath(__file__))
if dag_path not in sys.path:
    sys.path.insert(0, dag_path)
    sys.path.insert(0, os.path.join(dag_path, 'api'))
    sys.path.insert(0, os.path.join(dag_path, 'dataWarehouse'))

from dataWarehouse.data_loading import load_data
from dataWarehouse.data_modifications import (
    delete_rows,
    upsert_staging_batch,
    upsert_core_batch,
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

        # 1. Bulk upsert all JSON data in a single shot
        upsert_staging_batch(conn, cursor, YT_data)

        # 2. Bulk delete rows removed from source
        ids_in_json = set(r.get('video_id') or r.get('Video_id') for r in YT_data)
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

        # Read staging data
        cursor.execute(f'SELECT * FROM "YT_ANALYTICS_DB".STAGING.{TABLE};')
        staging_rows = cursor.fetchall()

        # Transform in memory
        transformed_rows = [transform_data(row) for row in staging_rows]

        # Bulk upsert all transformed records
        upsert_core_batch(conn, cursor, transformed_rows)

        logger.info(f"Core table {schema}.{TABLE} updated successfully.")
    except Exception as e:
        logger.error(f"Error in core_table task: {e}")
        raise e
    finally:
        if conn and cursor:
            close_conn_cursor(conn, cursor)
