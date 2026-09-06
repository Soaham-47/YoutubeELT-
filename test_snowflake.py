import snowflake.connector

USER = "SOAHAM47"               # Your Snowflake username
PASSWORD = "nx6Tc6fT4bEysS4" # The password you created the account with
ACCOUNT = "RPZUJOQ-RG25036"

try:
    conn = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
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