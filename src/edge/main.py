import argparse
import csv

import basic_threshold


# This script is a very basic simulation of the sequence of events to detect risk events in a vehicle.
# 
# - Vehicle posts signal changes periodically, at a 10-100ms update rate.
# - For each signal change, the risk event detectors are notified
# - Risk event detectors will use the signal change to evaluate a risk event
# - If a risk event is detected, a Risk Event is created and posted
# - Risk event is transmitted to the cloud

# Represents a vehicle signal.
class Signal:

    def __init__(self, name, value, timestamp):
        self.name = name
        self.value = value
        self.timestamp = timestamp

riskEvenDetectortList = [
    # Basic Threshold is a trivial, naive detector that just posts an event if a threshold on a signal is detected.
    basic_threshold.risk_detector
]

# Here we will showcase the telemetry platform part - which is basically just serializing the risk event and sending it to the cloud
def post(riskEvent):    
    print("Posting risk event to cloud, eventually")  

# This is the callback from the risk event detectors
def risk_event_callback(riskEvent):
    print(f"Received a risk event {riskEvent.name} with risk level {riskEvent.riskLevel} and value {riskEvent.value}")
    

# This just creates a Signal object from the CSV line
# This will be replaced by a proper notification from the In-Vehicle Digital Twin
def process_signal(data):
    return Signal(data[1], float(data[3]), float(data[2]))

# Each time that a signal change is posted in the in-vehicle digital twin, the risk event detectors will be notified.
# Each risk event detector has individual logic that decides if it should be triggered
# In case the risk event detects a problem, it will post the notification in the callback
def notify_risk_event_detectors(signal):
    for riskEventDetector in riskEvenDetectortList:
        riskEventDetector(signal, risk_event_callback)    

# This method will read the recording file line by line, create a Signal object and notify the risk event detectors.
# This will be replaced by listening to changes on the in-vehicle digital twin
def process_sample_file(filename):
    
    # Read the file as CSV, line by line
    with open(filename, newline='') as csvfile:
        
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # Ignore the first line, which is the header
        next(reader)
        for row in reader:
            signal = process_signal(row)
            notify_risk_event_detectors(signal)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts the sample process")
    parser.add_argument("-f", "--file", dest="file", help="Path to the file containing the recording.")
    args = parser.parse_args()

    if(args.file):
        process_sample_file(args.file)