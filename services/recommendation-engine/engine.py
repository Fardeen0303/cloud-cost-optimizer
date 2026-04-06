import logging
import os
import json
import sys
from datetime import datetime, timezone
import psycopg2

sys.path.insert(0, '/app/notifier')
from notifier import alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', 20.0))
SAVINGS_PER_DOWNSIZE = float(os.getenv('SAVINGS_PER_DOWNSIZE', 45.00))


class RecommendationEngine:
    def _connect(self):
        return psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

    def analyze_resources(self):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM scanned_resources WHERE resource_type='EC2'")
                resources = cur.fetchall()

            count = 0
            for resource in resources:
                if self.is_underutilized(resource):
                    self.create_recommendation(conn, resource)
                    count += 1

            conn.commit()
        logger.info(f"Analysis complete. Created {count} recommendations.")

    def is_underutilized(self, resource):
        try:
            data = resource[3]
            if isinstance(data, str):
                data = json.loads(data)
            avg_cpu = data.get('avg_cpu')
            if avg_cpu is None:
                return False
            return avg_cpu < CPU_THRESHOLD
        except Exception as e:
            logger.warning(f"Could not evaluate resource {resource[1]}: {e}")
            return False

    def create_recommendation(self, conn, resource):
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recommendations (resource_id, recommendation_type, potential_savings, priority, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (resource[1], 'downsize', SAVINGS_PER_DOWNSIZE, 'medium', datetime.now(tz=timezone.utc)))
        logger.info(f"Recommendation created for resource: {resource[1]}")
        alert(
            title="💡 New Cost Recommendation",
            message=f"Resource `{resource[1]}` is underutilized. Recommended action: *downsize*. Potential savings: *${SAVINGS_PER_DOWNSIZE}/mo*",
            level="warning"
        )


if __name__ == '__main__':
    engine = RecommendationEngine()
    engine.analyze_resources()
