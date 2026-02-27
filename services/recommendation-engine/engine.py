import psycopg2
import os
from datetime import datetime

class RecommendationEngine:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def analyze_resources(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM scanned_resources WHERE resource_type='EC2'")
        resources = cur.fetchall()
        
        for resource in resources:
            if self.is_underutilized(resource):
                self.create_recommendation(resource)
        
        cur.close()
    
    def is_underutilized(self, resource):
        # Logic to check CPU < 20%
        return True
    
    def create_recommendation(self, resource):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO recommendations (resource_id, recommendation_type, potential_savings, priority)
            VALUES (%s, %s, %s, %s)
        """, (resource[1], 'downsize', 45.00, 'medium'))
        self.conn.commit()
        cur.close()

if __name__ == '__main__':
    engine = RecommendationEngine()
    engine.analyze_resources()
