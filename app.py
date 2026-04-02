from flask import Flask, request, jsonify, render_template
from  auth import generate_token, verify_token
from decision_engine import evaluate_access
from logger import log_decision
from risk_engine import calculate_risk
import json
import os




app = Flask(__name__)

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password" : "user123", "role" : "user"}
    }

@app.route("/")
def home():
    return "Zero Trust AI Security APP Running"

@app.route("/login",methods = ["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    
    user = users.get(username)

    if user and user ["password"]==password:
        token =generate_token(username, user["role"])
        return jsonify({"token": token})
    return jsonify({"error":"Invalid Credentials"}), 401

@app.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Token Missing"}), 403
    
    token = auth_header.split(" ")[1]
    decoded = verify_token(token)
    

    if not decoded:
        return jsonify({"error": "Invalid Token"}),403
    
    risk_score = calculate_risk(
        decoded.get("username"),
        decoded.get("role"),
        "/protected"
    )
    
    allowed, reason  = evaluate_access(
        decoded["username"],
        decoded["role"],
        "/protected"
    )
    if not allowed :
        log_decision(
            decoded.get("username"),
            decoded.get("role"),
            "/protected",
            "DENY",
            reason, 
            risk_score
        )
        return jsonify({
            "error": "Access Denied",
            "reason" : reason,
            "risk_score" : risk_score
        }), 403
    
    log_decision(
        decoded.get("username"),
        decoded.get("role"),
        "/protected",
        "ALLOW",
        reason,
        risk_score
    )

    return jsonify({
        "message": "Access Granted!",
        "user": decoded["username"],
        "role": decoded["role"],
        "risk_score" : risk_score
        
    })

@app.route("/logs", methods=["GET"])
def get_logs():
    try:
        with open ("logs.json", "r") as f:
            logs = json.load(f)
        return jsonify(logs)
    except:
        return jsonify({"error":"No logs found"}),403
  
@app.route("/analytics", methods = ["GET"])
def analytics():
    try:
        with open("logs.json","r") as f:
            logs = json.load(f)

        total = len(logs)
        denied = sum(1 for log in logs if log ["decision"]=="DENY")
        high_risk = sum(1 for log in logs if log["risk_score"]>70)

        return jsonify({
            "total_requests" : total,
            "denied_requests" : denied,
            "high_risk_events" : high_risk
        })
    except:
        return jsonify({"error" : "No logs available"}),404
    

@app.route("/delete-logs", methods=["DELETE"])
def delete_logs():
    try:
        with open("logs.json", "w") as f:
            json.dump([], f)
        return jsonify({"message": "Logs cleared successfully"})
    except:
        return jsonify({"error": "Failed to delete logs"}), 500

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    