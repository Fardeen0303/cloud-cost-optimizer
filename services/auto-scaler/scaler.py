import logging
import os
from datetime import datetime, timezone
import boto3
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoScaler:
    def __init__(self):
        self.ec2 = boto3.client('ec2', region_name=os.getenv('AWS_REGION', 'us-east-1'))

    def _connect(self):
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

    def execute_recommendations(self):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM recommendations WHERE status='approved'")
                recommendations = cur.fetchall()

            for rec in recommendations:
                self.apply_action(conn, rec)

            conn.commit()

    def apply_action(self, conn, recommendation):
        rec_id = recommendation[0]
        instance_id = recommendation[1]
        action_type = recommendation[2]
        status = 'success'
        result = ''

        try:
            self.ec2.stop_instances(InstanceIds=[instance_id])
            result = f"Stopped instance {instance_id}"
            logger.info(result)

            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE recommendations SET status='completed' WHERE id=%s", (rec_id,)
                )
        except Exception as e:
            status = 'failed'
            result = str(e)
            logger.error(f"Failed to stop {instance_id}: {e}")

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO optimization_actions (recommendation_id, action_type, executed_at, status, result)
                VALUES (%s, %s, %s, %s, %s)
            """, (rec_id, action_type or 'stop_instance', datetime.now(tz=timezone.utc), status, result))


if __name__ == '__main__':
    scaler = AutoScaler()
    scaler.execute_recommendations()
