import schedule
import time
import requests

def trigger_scan():
    print("Triggering cost scan...")
    # Trigger cost scanner

def trigger_analysis():
    print("Triggering analysis...")
    # Trigger recommendation engine

schedule.every().hour.do(trigger_scan)
schedule.every(6).hours.do(trigger_analysis)

while True:
    schedule.run_pending()
    time.sleep(60)
