from __future__ import annotations

import os

import psycopg2


DB_CONFIG = {
    "dbname": os.getenv("PGDATABASE", "camera_ai"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
}


DEMO_DETECTIONS = [
    ("demo_camera", 0, "person", 0.91, 24, 42, 330, 440, "demo/person_001.jpg", "demo_yolo", 100, 1),
    ("demo_camera", 0, "person", 0.87, 40, 55, 318, 430, "demo/person_002.jpg", "demo_yolo", 130, 1),
    ("demo_camera", 56, "chair", 0.72, 360, 210, 520, 470, "demo/chair_001.jpg", "demo_yolo", 130, 2),
    ("demo_camera", 63, "laptop", 0.81, 210, 260, 420, 390, "demo/laptop_001.jpg", "demo_yolo", 160, 3),
    ("demo_camera", 67, "cell phone", 0.84, 450, 260, 510, 340, "demo/phone_001.jpg", "demo_yolo", 190, 4),
    ("demo_camera", 0, "person", 0.89, 28, 48, 334, 446, "demo/person_003.jpg", "demo_yolo", 220, 1),
]


def main() -> None:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM alerts WHERE camera_id = 'demo_camera'")
            cur.execute("DELETE FROM detection_events WHERE camera_id = 'demo_camera'")
            cur.execute("DELETE FROM detections WHERE camera_id = 'demo_camera'")

            cur.executemany(
                """
                INSERT INTO detections
                (camera_id, class_id, object_name, confidence, x1, y1, x2, y2, image_path, model_name, frame_id, track_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                DEMO_DETECTIONS,
            )

            events = [
                ("demo_camera", 0, "person", "demo_yolo", 1, 100, 220, 3, 0.91, 0.89, "active", ""),
                ("demo_camera", 56, "chair", "demo_yolo", 2, 130, 130, 1, 0.72, 0.72, "active", ""),
                ("demo_camera", 63, "laptop", "demo_yolo", 3, 160, 160, 1, 0.81, 0.81, "closed", ""),
                ("demo_camera", 67, "cell phone", "demo_yolo", 4, 190, 190, 1, 0.84, 0.84, "closed", ""),
            ]
            event_ids: dict[str, int] = {}
            for event in events:
                cur.execute(
                    """
                    INSERT INTO detection_events
                    (
                        camera_id, class_id, object_name, model_name, track_id, first_frame_id, last_frame_id,
                        detection_count, max_confidence, last_confidence, status, snapshot_path
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    event,
                )
                event_ids[event[2]] = cur.fetchone()[0]

            alerts = [
                (
                    "demo_camera",
                    "person_detected",
                    "person",
                    event_ids["person"],
                    "person detected on demo_camera",
                    0.91,
                    "",
                    "new",
                    1,
                ),
                (
                    "demo_camera",
                    "phone_detected",
                    "cell phone",
                    event_ids["cell phone"],
                    "cell phone detected on demo_camera",
                    0.84,
                    "",
                    "acknowledged",
                    4,
                ),
            ]
            cur.executemany(
                """
                INSERT INTO alerts
                (camera_id, alert_type, object_name, event_id, message, confidence, snapshot_path, status, track_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                alerts,
            )

    print("Seeded demo data for camera_id=demo_camera")


if __name__ == "__main__":
    main()
