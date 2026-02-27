import boto3
import psycopg2
from datetime import datetime
import config

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
                results.append({
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime']
                })
        return results
    
    def get_cpu_utilization(self, instance_id):
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=datetime.now() - timedelta(days=7),
            EndTime=datetime.now(),
            Period=3600,
            Statistics=['Average']
        )
        return response['Datapoints']
    
    def save_to_db(self, data):
        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scanned_resources (resource_id, resource_type, data, scanned_at)
            VALUES (%s, %s, %s, %s)
        """, (data['instance_id'], 'EC2', str(data), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
    
    def run_scan(self):
        print(f"Starting scan at {datetime.now()}")
        instances = self.scan_ec2_instances()
        for instance in instances:
            self.save_to_db(instance)
        print(f"Scan completed. Found {len(instances)} instances")

if __name__ == '__main__':
    scanner = CostScanner()
    scanner.run_scan()
