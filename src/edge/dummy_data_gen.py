import random
import time
import uuid

# List of vehicle ids
vehicleIds = []

for i in range(10):
    vehicleId = str(uuid.uuid4())
    vehicleIds.append(vehicleId)

def generate_sample_data(vehicleId):
    data = {
        "vehicleId": vehicleId,
        "name": "speeding_start",
        "eventId": round(random.uniform(1, 2), 1),
        "riskLevel": random.randint(1, 5),
        "timestamp": round(time.time(), 6),
        "eventData": {
            "Vehicle_Speed_Speed": round(random.uniform(50, 150), 2)
        }
    }
    return data

# Generate a sample data
events = []

for vehicleId in vehicleIds:
    event = generate_sample_data(vehicleId)
    events.append(event)

for e in events:
    print(e)