import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME', 'cost_optimizer')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))
