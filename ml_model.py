import numpy as np
from sklearn.ensemble import IsolationForest

# Dummy training data (normal behavior)
# time gaps in seconds
normal_data = np.array([[10], [12], [9], [11], [10], [13]])

model = IsolationForest(contamination=0.2)
model.fit(normal_data)

def detect_anomaly(request_times):
    if len(request_times) < 2:
        return False

    # Convert timestamps to time differences
    time_diffs = []

    for i in range(1, len(request_times)):
        diff = (
            request_times[i-1] - request_times[i]
        ).total_seconds()
        time_diffs.append([abs(diff)])

    prediction = model.predict(time_diffs)

    # -1 = anomaly
    return -1 in prediction