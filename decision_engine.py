import datetime
from risk_engine import calculate_risk
from ml_model import detect_anomaly
from redis_client import r


def evaluate_access(user, role, endpoint):

    # Step 1: Base risk
    risk_score = calculate_risk(user, role, endpoint)

    # Step 2: Admin-only endpoint protection
    if endpoint == "/protected" and role != "admin":
        return False, "Access denied: Admin only endpoint"

    # Step 3: Redis tracking (BEFORE ML)
    key = f"user:{user}:requests"
    r.lpush(key, str(datetime.datetime.utcnow()))
    r.ltrim(key, 0, 9)

    timestamps = r.lrange(key, 0, -1)

    # Convert to datetime
    times = [datetime.datetime.fromisoformat(t) for t in timestamps]

    # Step 4: ML anomaly detection (only if enough data)
    if len(times) > 2 and role != "admin":
        if detect_anomaly(times):
            risk_score += 50

    # Step 5: Rate-based risk
    request_count = r.llen(key)
    if request_count > 5:
        risk_score += 40

    # Step 6: Final decision
    if role == "admin" and risk_score > 70:
       print(f"[ALERT] High-risk admin activity detected :{risk_score}")
        
    return True, f"Access granted (risk score: {risk_score})"