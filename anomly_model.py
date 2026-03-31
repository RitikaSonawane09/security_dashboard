
import numpy as np
from sklearn.ensemble import IsolationForest

# Train simple model
model = IsolationForest(contamination=0.2)

# Dummy training data
X = np.array([
    [10], [15], [20], [12], [18],  # normal
    [80], [90]  # anomalies
])

model.fit(X)

def detect_anomaly(risk_score):
    prediction = model.predict([[risk_score]])
    return prediction[0] == -1  # -1 = anomaly