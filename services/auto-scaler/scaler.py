import boto3
import psycopg2
import os

class AutoScaler:
    def __init__(self):
        self.ec2 = boto3.client('ec2', region_name=os.getenv('AWS_REGION'))
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def execute_recommendations(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM recommendations WHERE status='approved'")
        recommendations = cur.fetchall()
        
        for rec in recommendations:
            self.apply_action(rec)
        
        cur.close()
    
    def apply_action(self, recommendation):
        instance_id = recommendation[1]
        self.ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Stopped instance: {instance_id}")

if __name__ == '__main__':
    scaler = AutoScaler()
    scaler.execute_recommendations()
