import logging

logger = logging.getLogger(__name__)
TABLE = "YT_API"


def _val(row, *keys, default=None):
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return default


def upsert_staging_batch(conn, cursor, records):
    """Bulk upserts staging records in a single round-trip."""
    if not records:
        return

    # Create a temporary table to receive the batch instantly
    cursor.execute("""
        CREATE TEMPORARY TABLE STAGING.YT_API_TEMP LIKE STAGING.YT_API;
    """)

    insert_sql = """
        INSERT INTO STAGING.YT_API_TEMP (
            "Video_id", "Video_title", "Published_at", "Duration", "View_count", "Like_count", "Comment_count"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    params = [
        (
            _val(r, "video_id", "Video_id", "id"),
            _val(r, "title", "Video_title", "video_title"),
            _val(r, "publishedAt", "Published_at", "published_at"),
            _val(r, "duration", "Duration"),
            _val(r, "viewCount", "View_count", "view_count"),
            _val(r, "likeCount", "Like_count", "like_count"),
            _val(r, "commentCount", "Comment_count", "comment_count"),
        )
        for r in records
    ]
    cursor.executemany(insert_sql, params)

    # Perform set-based MERGE in Snowflake warehouse memory (sub-second)
    merge_sql = """
        MERGE INTO STAGING.YT_API AS target
        USING STAGING.YT_API_TEMP AS source
        ON target."Video_id" = source."Video_id"
        WHEN MATCHED THEN UPDATE SET
            target."Video_title" = source."Video_title",
            target."Published_at" = source."Published_at",
            target."Duration" = source."Duration",
            target."View_count" = source."View_count",
            target."Like_count" = source."Like_count",
            target."Comment_count" = source."Comment_count"
        WHEN NOT MATCHED THEN INSERT (
            "Video_id", "Video_title", "Published_at", "Duration", "View_count", "Like_count", "Comment_count"
        ) VALUES (
            source."Video_id", source."Video_title", source."Published_at", source."Duration",
            source."View_count", source."Like_count", source."Comment_count"
        );
    """
    cursor.execute(merge_sql)
    cursor.execute("DROP TABLE IF EXISTS STAGING.YT_API_TEMP;")
    conn.commit()
    logger.info(f"Successfully batch-upserted {len(records)} rows into STAGING.")


def upsert_core_batch(conn, cursor, records):
    if not records:
        return

    cursor.execute("""
        CREATE TEMPORARY TABLE "YT_ANALYTICS_DB".CORE.YT_API_TEMP LIKE "YT_ANALYTICS_DB".CORE.YT_API;
    """)

    insert_sql = """
        INSERT INTO "YT_ANALYTICS_DB".CORE.YT_API_TEMP (
            "Video_id", "Video_title", "Published_at", "Duration", "Video_type", "View_count", "Like_count", "Comment_count"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    params = [
        (
            _val(r, "Video_id", "video_id"),
            _val(r, "Video_title", "title", "video_title"),
            str(_val(r, "Published_at", "publishedAt", "published_at")),
            _val(r, "Duration", "duration"),
            _val(r, "Video_type", "video_type"),
            _val(r, "View_count", "viewCount", "view_count"),
            _val(r, "Like_count", "likeCount", "like_count"),
            _val(r, "Comment_count", "commentCount", "comment_count"),
        )
        for r in records
    ]
    cursor.executemany(insert_sql, params)

    merge_sql = """
        MERGE INTO "YT_ANALYTICS_DB".CORE.YT_API AS target
        USING "YT_ANALYTICS_DB".CORE.YT_API_TEMP AS source
        ON target."Video_id" = source."Video_id"
        WHEN MATCHED THEN UPDATE SET
            target."Video_title" = source."Video_title",
            target."Published_at" = source."Published_at",
            target."Duration" = source."Duration",
            target."Video_type" = source."Video_type",
            target."View_count" = source."View_count",
            target."Like_count" = source."Like_count",
            target."Comment_count" = source."Comment_count"
        WHEN NOT MATCHED THEN INSERT (
            "Video_id", "Video_title", "Published_at", "Duration", "Video_type", "View_count", "Like_count", "Comment_count"
        ) VALUES (
            source."Video_id", source."Video_title", source."Published_at", source."Duration",
            source."Video_type", source."View_count", source."Like_count", source."Comment_count"
        );
    """
    cursor.execute(merge_sql)
    cursor.execute('DROP TABLE IF EXISTS "YT_ANALYTICS_DB".CORE.YT_API_TEMP;')
    conn.commit()
    logger.info(f"Successfully batch-upserted {len(records)} rows into CORE.")

def delete_rows(conn, cursor, schema, ids_to_delete):
    if not ids_to_delete:
        return
    schema = schema.upper()
    formatted_ids = ", ".join([f"'{v_id}'" for v_id in ids_to_delete])
    delete_sql = f'DELETE FROM {schema}.{TABLE} WHERE "Video_id" IN ({formatted_ids});'
    cursor.execute(delete_sql)
    conn.commit()
    logger.info(f"Deleted {len(ids_to_delete)} rows from {schema}.{TABLE}")