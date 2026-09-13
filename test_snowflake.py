import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse="YT_WH",
        database="YT_ANALYTICS_DB",
        schema="STAGING",
        role="ACCOUNTADMIN"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();")
    version, wh, db, schema = cursor.fetchone()

    print(" Snowflake Connection Successful!")
    print(f"Version:   {version}")
    print(f"Warehouse: {wh}")
    print(f"Database:  {db}")
    print(f"Schema:    {schema}")

    cursor.close()
    conn.close()

except Exception as e:
    print(" Connection Failed:")
    print(e)