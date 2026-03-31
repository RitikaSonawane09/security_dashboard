import json
import os
from datetime import datetime

LOG_FILE = "logs.json"

def log_decision(user, role, endpoint, decision, reason, risk_score):
    log_entry = {
        "user": user,
        "role" : role,
        "endpoint" : endpoint,
        "decision" : decision,
        "reason" : reason,
        "risk_score" : risk_score,
        "timestamp" : datetime.utcnow().isoformat()
    }
    logs = []

    #Load existing logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(log_entry)

    #save back
    with open (LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

