import logging
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

import logging
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "snowflake_datasource"


def yt_elt_data_quality(schema):
    schema_upper = schema.upper()
    schema_lower = schema.lower()
    try:
        task = BashOperator(
            task_id=f'soda_test_{schema_lower}',
            bash_command=(
                f'soda scan -d {DATASOURCE} '
                f'-c {SODA_PATH}/configuration.yml '
                f'-v SCHEMA={schema_upper} '
                f'{SODA_PATH}/checks_{schema_lower}.yml'
            ),
        )
        return task
    except Exception as e:
        logger.error(
            f"Error creating Soda data quality task for schema {schema_upper}: {e}"
        )
        raise e