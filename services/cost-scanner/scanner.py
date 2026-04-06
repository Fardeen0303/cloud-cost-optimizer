import logging
import json
import boto3
import psycopg2
from datetime import datetime, timedelta, timezone
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CostScanner:
    def __init__(self):
        self.ec2 = boto3.client('ec2', region_name=config.AWS_REGION)
        self.cloudwatch = boto3.client('cloudwatch', region_name=config.AWS_REGION)
        self.ce = boto3.client('ce', region_name=config.AWS_REGION)

    def connect_db(self):
        return psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )

    def scan_ec2_instances(self):
        instances = self.ec2.describe_instances()
        results = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                avg_cpu = self.get_avg_cpu(instance_id)
                results.append({
                    'instance_id': instance_id,
                    'instance_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'avg_cpu': avg_cpu
                })
        return results

    def get_avg_cpu(self, instance_id):
        try:
            now = datetime.now(tz=timezone.utc)
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=now - timedelta(days=7),
                EndTime=now,
                Period=3600,
                Statistics=['Average']
            )
            datapoints = response['Datapoints']
            if not datapoints:
                return None
            return sum(d['Average'] for d in datapoints) / len(datapoints)
        except Exception as e:
            logger.warning(f"Could not get CPU for {instance_id}: {e}")
            return None

    def save_to_db(self, data):
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO scanned_resources (resource_id, resource_type, data, scanned_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (data['instance_id'], 'EC2', json.dumps(data), datetime.now(tz=timezone.utc)))
            conn.commit()

    def run_scan(self):
        logger.info(f"Starting scan at {datetime.now(tz=timezone.utc)}")
        try:
            instances = self.scan_ec2_instances()
            for instance in instances:
                self.save_to_db(instance)
            logger.info(f"Scan completed. Found {len(instances)} instances")
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            raise


if __name__ == '__main__':
    scanner = CostScanner()
    scanner.run_scan()
