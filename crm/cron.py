def log_crm_heartbeat():
    from datetime import datetime
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    # Use the exact path the check expects
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

