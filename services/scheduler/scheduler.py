import logging
import os
import schedule
import time
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCANNER_URL = os.getenv('SCANNER_URL', 'http://cost-scanner:8001')
ENGINE_URL = os.getenv('ENGINE_URL', 'http://recommendation-engine:8002')


def trigger_scan():
    try:
        response = requests.post(f"{SCANNER_URL}/scan", timeout=30)
        response.raise_for_status()
        logger.info("Scan triggered successfully")
    except Exception as e:
        logger.error(f"Failed to trigger scan: {e}")


def trigger_analysis():
    try:
        response = requests.post(f"{ENGINE_URL}/analyze", timeout=30)
        response.raise_for_status()
        logger.info("Analysis triggered successfully")
    except Exception as e:
        logger.error(f"Failed to trigger analysis: {e}")


schedule.every().hour.do(trigger_scan)
schedule.every(6).hours.do(trigger_analysis)

logger.info("Scheduler started")
while True:
    schedule.run_pending()
    time.sleep(60)
