from datetime import datetime
from redis_client import r


#simple in-memory tracking (can upgrade later)

user_activity ={}

def calculate_risk(user, role, endpoint):
    risk_score = 0

    #Rule 1: Role based Risk
    if role != "admin":
        risk_score += 40

    #Rule 2 : Sensitive endpoint
    if endpoint =="/protected":
        risk_score += 30

    #Rule 3 : Frequency based anomly
    now = datetime.utcnow()

    if user not in user_activity:
        user_activity[user] = []
    
    user_activity[user].append(now)

    #Keep last 5 request

    user_activity[user] = user_activity[user][-5:]

    #If too many requests quckily -> suspicious

    if len(user_activity[user]) >= 3:
        time_diff = (user_activity[user][-1] - user_activity[user] [0] ).seconds
        if time_diff <10:
            risk_score += 50
    
    key = f"user:{user}:requests"

    r.lpush(key, str(datetime.utcnow()))
    r.ltrim(key, 0, 4)  # keep last 5

    requests = r.lrange(key, 0, -1)

    if len(requests) >= 3:
        risk_score += 50

    return risk_score

