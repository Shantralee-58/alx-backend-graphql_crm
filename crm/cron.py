import schedule
import time
from datetime import datetime
import os

# Log file in project root
log_file_path = os.path.join(os.getcwd(), "crm_heartbeat_log.txt")

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    with open(log_file_path, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")
    print(f"{timestamp} CRM is alive")

# Schedule every 5 minutes
schedule.every(5).minutes.do(log_crm_heartbeat)

print(f"Heartbeat logger started. Logging to {log_file_path}")

while True:
    schedule.run_pending()
    time.sleep(1)

