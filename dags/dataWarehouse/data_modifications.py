import logging

logger = logging.getLogger(__name__)
TABLE = "YT_API"


def _val(row, *keys, default=None):
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return default


def insert_rows(conn, cursor, schema, row):
    schema = schema.upper()
    if schema == "STAGING":
        insert_sql = f"""
            INSERT INTO {schema}.{TABLE} (
                "Video_id", "Video_title", "Published_at", "Duration", "View_count", "Like_count", "Comment_count"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            insert_sql,
            (
                _val(row, "video_id", "Video_id", "id"),
                _val(row, "title", "Video_title", "video_title"),
                _val(row, "publishedAt", "Published_at", "published_at"),
                _val(row, "duration", "Duration"),
                _val(row, "viewCount", "View_count", "view_count"),
                _val(row, "likeCount", "Like_count", "like_count"),
                _val(row, "commentCount", "Comment_count", "comment_count"),
            ),
        )
    else:  # CORE
        insert_sql = f"""
            INSERT INTO {schema}.{TABLE} (
                "Video_id", "Video_title", "Published_at", "Duration", "Video_type", "View_count", "Like_count", "Comment_count"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            insert_sql,
            (
                _val(row, "Video_id", "video_id"),
                _val(row, "Video_title", "title", "video_title"),
                _val(row, "Published_at", "publishedAt", "published_at"),
                _val(row, "Duration", "duration"),
                _val(row, "Video_type", "video_type"),
                _val(row, "View_count", "viewCount", "view_count"),
                _val(row, "Like_count", "likeCount", "like_count"),
                _val(row, "Comment_count", "commentCount", "comment_count"),
            ),
        )
    conn.commit()


def update_rows(conn, cursor, schema, row):
    schema = schema.upper()
    if schema == "STAGING":
        update_sql = f"""
            UPDATE {schema}.{TABLE} SET
                "Video_title" = %s,
                "Published_at" = %s,
                "Duration" = %s,
                "View_count" = %s,
                "Like_count" = %s,
                "Comment_count" = %s
            WHERE "Video_id" = %s;
        """
        cursor.execute(
            update_sql,
            (
                _val(row, "title", "Video_title", "video_title"),
                _val(row, "publishedAt", "Published_at", "published_at"),
                _val(row, "duration", "Duration"),
                _val(row, "viewCount", "View_count", "view_count"),
                _val(row, "likeCount", "Like_count", "like_count"),
                _val(row, "commentCount", "Comment_count", "comment_count"),
                _val(row, "video_id", "Video_id", "id"),
            ),
        )
    else:  # CORE
        update_sql = f"""
            UPDATE {schema}.{TABLE} SET
                "Video_title" = %s,
                "Published_at" = %s,
                "Duration" = %s,
                "Video_type" = %s,
                "View_count" = %s,
                "Like_count" = %s,
                "Comment_count" = %s
            WHERE "Video_id" = %s;
        """
        cursor.execute(
            update_sql,
            (
                _val(row, "Video_title", "title", "video_title"),
                _val(row, "Published_at", "publishedAt", "published_at"),
                _val(row, "Duration", "duration"),
                _val(row, "Video_type", "video_type"),
                _val(row, "View_count", "viewCount", "view_count"),
                _val(row, "Like_count", "likeCount", "like_count"),
                _val(row, "Comment_count", "commentCount", "comment_count"),
                _val(row, "Video_id", "video_id"),
            ),
        )
    conn.commit()


def delete_rows(conn, cursor, schema, ids_to_delete):
    if not ids_to_delete:
        return
    schema = schema.upper()
    formatted_ids = ", ".join([f"'{v_id}'" for v_id in ids_to_delete])
    delete_sql = f'DELETE FROM {schema}.{TABLE} WHERE "Video_id" IN ({formatted_ids});'
    cursor.execute(delete_sql)
    conn.commit()
    logger.info(f"Deleted {len(ids_to_delete)} rows from {schema}.{TABLE}")