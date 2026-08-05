import psycopg2
from psycopg2.extras import RealDictCursor

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)


class Database:

    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor,
            )

        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def save_detection(self, detection: dict):
        conn = self.connect()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO detections (
                        batch_number,
                        batch_folder,
                        detected_at,
                        total_frames,
                        detected_frames,
                        avg_confidence,
                        presence_ratio,
                        longest_streak,
                        suspicion_score,
                        status,
                        whatsapp_sent
                    )
                    VALUES (
                        %(batch_number)s,
                        %(batch_folder)s,
                        %(detected_at)s,
                        %(total_frames)s,
                        %(detected_frames)s,
                        %(avg_confidence)s,
                        %(presence_ratio)s,
                        %(longest_streak)s,
                        %(suspicion_score)s,
                        %(status)s,
                        %(whatsapp_sent)s
                    )
                    """,
                    detection,
                )
            conn.commit()

        except Exception:
            conn.rollback()
            raise

    def test_connection(self):

        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(version)

            return True

        except Exception as e:
            print(e)

            return False

    def get_all(self):
        conn=self.connect()
        try:

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM detections
                    ORDER BY detected_at DESC
                    """
                )
                return cur.fetchall()

        except Exception:
            conn.rollback()
            raise

    def get_by_id(self, detection_id):
        conn = self.connect()

        try:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT *
                    FROM detections
                    WHERE id=%s
                    """,
                    (detection_id,)
                )

                return cur.fetchone()

        except Exception:

            conn.rollback()
            raise


    def get_by_date(self, start_date, end_date):

        conn=self.connect()

        try:

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM detections

                    WHERE detected_at
                    BETWEEN %s AND %s

                    ORDER BY detected_at DESC
                    """,
                    (start_date, end_date),
                )

                return cur.fetchall()

        except Exception:
            conn.rollback()
            raise

    def get_dashboard(self):

        conn = self.connect()

        try:

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        COUNT(*) AS total_batch,
                        SUM(detected_frames) AS total_detected_frames,
                        COUNT(*) FILTER (
                            WHERE status='Normal'
                        ) AS normal,
                        COUNT(*) FILTER (
                            WHERE status='Perlu Dipantau'
                        ) AS monitoring,
                        COUNT(*) FILTER (
                            WHERE status='Mencurigakan'
                        ) AS suspicious,
                        COUNT(*) FILTER (
                            WHERE whatsapp_sent=TRUE
                        ) AS whatsapp_sent
                    FROM detections;
                """)

                return cur.fetchone()

        except Exception:
            conn.rollback()
            raise

    def get_paginated(
        self,
        page=1,
        limit=20,
        status=None,
        start=None,
        end=None,
        keyword=None
    ):
        conn = self.connect()
        try:
            offset = (page - 1) * limit

            query = """
                SELECT *
                FROM detections
                WHERE 1=1
            """

            params = []

            if status:
                query += " AND status = %s"
                params.append(status)

            if start:
                query += " AND detected_at >= %s"
                params.append(start)

            if end:
                query += " AND detected_at <= %s"
                params.append(end)

            if keyword:
                query += """
                    AND (
                        batch_number::TEXT ILIKE %s
                        OR status ILIKE %s
                        OR detected_at::TEXT ILIKE %s
                    )
                """

                params.extend([
                    f"%{keyword}%",
                    f"%{keyword}%",
                    f"%{keyword}%"
                ])

            count_query = f"""
                SELECT COUNT(*)
                FROM ({query}) filtered
            """

            query += """
                ORDER BY detected_at DESC
                LIMIT %s OFFSET %s
            """

            with conn.cursor() as cur:

                cur.execute(count_query, params)
                total = cur.fetchone()["count"]

                cur.execute(
                    query,
                    params + [limit, offset]
                )

                rows = cur.fetchall()

            return {
                "rows": rows,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit
            }

        except Exception:
            conn.rollback()
            raise


    def get_files_info(self, detection_id):
        conn=self.connect()

        try:

            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        batch_folder,
                        batch_number
                    FROM detections
                    WHERE id=%s
                """,(detection_id,))

                return cur.fetchone()
        
        except Exception:
            conn.rollback()
            raise

    def delete_detection(self, detection_id):
        conn = self.connect()

        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM detections
                WHERE id=%s
                """,
                (detection_id,),
            )
            conn.commit()


    def truncate(self):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE detections
                RESTART IDENTITY;
                """
            )
            conn.commit()

    # Migrate data from old folder structure
    def exists_batch_folder(self, batch_folder):
        conn = self.connect()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM detections
                    WHERE batch_folder = %s
                    LIMIT 1
                    """,
                    (batch_folder,)
                )
                return cur.fetchone() is not None

        except Exception:
            raise

    def insert_detection(self, data):
        conn = self.connect()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO detections
                    (
                        batch_number,
                        detected_at,
                        total_frames,
                        detected_frames,
                        avg_confidence,
                        presence_ratio,
                        longest_streak,
                        suspicion_score,
                        status,
                        batch_folder,
                        whatsapp_sent
                    )
                    VALUES
                    (
                        %(batch_number)s,
                        %(detected_at)s,
                        %(total_frames)s,
                        %(detected_frames)s,
                        %(avg_confidence)s,
                        %(presence_ratio)s,
                        %(longest_streak)s,
                        %(suspicion_score)s,
                        %(status)s,
                        %(batch_folder)s,
                        %(whatsapp_sent)s
                    )
                    """,
                    data,
                )
            conn.commit()

        except Exception:
            conn.rollback()
            raise


    def update_detection_from_whatsapp(
        self,
        batch_number,
        detected_at,
        avg_confidence,
        presence_ratio,
        longest_streak,
        suspicion_score,
        status
    ):

        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE detections

                    SET
                        avg_confidence = %s,
                        presence_ratio = %s,
                        longest_streak = %s,
                        suspicion_score = %s,
                        status = %s,
                        whatsapp_sent = TRUE

                    WHERE
                        batch_number = %s
                    AND
                        detected_at = %s
                    """,
                    (
                        avg_confidence,
                        presence_ratio,
                        longest_streak,
                        suspicion_score,
                        status,
                        batch_number,
                        detected_at,
                    ),
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise