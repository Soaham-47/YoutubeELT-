import logging
logger = logging.getLogger(__name__)
table="yt_api"

def insert_rows(conn, cursor, schema, row):
    video_id_key = "video_id" if schema == 'staging' else "Video_id"
    try:
        if schema == 'staging':
            cursor.execute(f"""
                INSERT INTO {schema}.{table} (
                    "Video_id", "Video_title", "Published_at", 
                    "Duration", "View_count", "Like_count", "Comment_count"
                )
                VALUES (
                    %(video_id)s, 
                    %(title)s,          -- Changed from video_title
                    %(publishedAt)s,    -- Changed from published_at
                    %(duration)s, 
                    %(viewCount)s,      -- Changed from view_count
                    %(likeCount)s,      -- Changed from like_count
                    %(commentCount)s    -- Changed from comment_count
                )
            """, row)
        else:
            cursor.execute(f"""
                        INSERT INTO {schema}.{table} (
                            "Video_id",
                            "Video_title",
                            "Published_at",
                            "Duration",
                            "Video_type",
                            "View_count",
                            "Like_count",
                            "Comment_count"
                        )
                        VALUES(%(Video_id)s,
                               %(Video_title)s,
                               %(Published_at)s,
                               %(Duration)s,
                               %(Video_type)s,
                               %(View_count)s,
                               %(Like_count)s,
                               %(Comment_count)s
                                 )""",row)
        conn.commit()
        logger.info(f"Inserted row for video_id: {row[video_id_key]}")
    except Exception as e:
        logger.error(f"Error inserting row for video_id {row.get(video_id_key)}")
        raise e

def update_rows(conn, cursor, schema, row):
    try:
        video_id_key = "video_id" if schema == 'staging' else "Video_id"
        if schema == 'staging':
            # Mapping JSON keys to Postgres Named Parameters
            sql = f"""
                UPDATE {schema}.{table}
                SET 
                    "Video_title"=%(title)s,
                    "View_count"=%(viewCount)s,
                    "Like_count"=%(likeCount)s,
                    "Comment_count"=%(commentCount)s
                WHERE "Video_id"=%(video_id)s AND "Published_at"=%(publishedAt)s;
            """
        else:
            # Core uses keys from the previous Postgres select
            sql = f"""
                UPDATE {schema}.{table}
                SET 
                    "Video_title"=%(Video_title)s,
                    "View_count"=%(View_count)s,
                    "Like_count"=%(Like_count)s,
                    "Comment_count"=%(Comment_count)s
                WHERE "Video_id"=%(Video_id)s AND "Published_at"=%(Published_at)s;
            """

        cursor.execute(sql, row)
        conn.commit() 
        logger.info(f"Updated row for video_id: {row[video_id_key]}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating row in {schema}: video_id {row.get(video_id_key)}")
        raise e
def delete_rows(conn,cursor,schema,video_ids):
    try:
        video_ids=f"""({','.join(f"'{id}'" for id in video_ids)})""" # Format video_ids as a tuple string for SQL IN clause
        cursor.execute(f"""
                    DELETE FROM {schema}.{table}
                    WHERE "Video_id" IN {video_ids};
                    """)
        conn.commit()
        logger.info(f"Deleted rows for video_ids: {video_ids}")
    except Exception as e:
        logger.error(f"Error deleting rows for video_ids {video_ids}")
        raise e 
