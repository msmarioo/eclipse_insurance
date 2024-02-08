import argparse
import csv

from event_detector import risk_event_detector
import event_definitions


# This script is a very basic simulation of the seuence of events to detect risk events in a vehicle.
# 
# - Vehicle posts signal changes periodically, at a 10-100ms update rate.
# - For each signal change, the risk event detectors are notified
# - Risk event detectors will use the signal change to evaluate a risk event
# - If a risk event is detected, a Risk Event is created and posted
# - Risk event is transmitted to the cloud

def setup_timeout_dict(event_list):
    return {e.name:0 for e in event_list}
    
def setup_signal_dict(event_list):
    relevant_signals = []
    for event in event_list:
        relevant_signals = relevant_signals + event.relevant_signals
        relevant_signals = relevant_signals + list(event.eventData.keys())
    relevant_signals = set(relevant_signals)
    signal_dict = {}
    for s in relevant_signals:
        signal_dict[s] = []
        # Alternative setup:
        # signal_dict[s] = [np.nan]*hist_signals
    return signal_dict

def update_signal_value(signal_dict, signal, hist_signals):
    signal_dict[signal.name].append(signal.value)
    signal_dict[signal.name] = signal_dict[signal.name][-hist_signals:]
    return signal_dict

# Alternative setup:
# def update_signal_value(signal_dict, signal):
#     signal_dict[signal.name].append(signal.value)
#     del signal_dict[signal.name][0]
#     return signal_dict

# Represents a vehicle signal.
class Signal:

    def __init__(self, name, value, timestamp):
        self.name = name
        self.value = value
        self.timestamp = timestamp


# Here we will showcase the telemetry platform part - which is basically just serializing the risk event and sending it to the cloud
def post(riskEvent):    
    print("Posting risk event to cloud, eventually")  

# This is the callback from the risk event detectors
def risk_event_callback(riskEvent):
    print(f"Received a risk event {riskEvent.name} at {riskEvent.timestamp} with risk level {riskEvent.riskLevel} and value {riskEvent.eventData}")
    

# This just creates a Signal object from the CSV line
# This will be replaced by a proper notification from the In-Vehicle Digital Twin
def process_signal(data):
    return Signal(data[1], float(data[3]), float(data[2]))

# Each time that a signal change is posted in the in-vehicle digital twin, the risk event detectors will be notified.
# Each risk event detector has individual logic that decides if it should be triggered
# In case the risk event detects a problem, it will post the notification in the callback


# This method will read the recording file line by line, create a Signal object and notify the risk event detectors.
# This will be replaced by listening to changes on the in-vehicle digital twin
def process_sample_file(filename):
    
    # Read the file as CSV, line by line
    with open(filename, newline='') as csvfile:
        
        hist_signals = 10
        timeout_dict = setup_timeout_dict(event_list)
        signal_dict = setup_signal_dict(event_list)
        
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # Ignore the first line, which is the header
        next(reader)
        for row in reader:
            signal = process_signal(row)
            if signal.name in signal_dict:
                update_signal_value(signal_dict, signal, hist_signals)
                if len(signal_dict[signal.name]) >= hist_signals:
                    risk_event_detector(event_list, timeout_dict, signal, signal_dict, risk_event_callback)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts the sample process")
    parser.add_argument("-f", "--file", dest="file", help="Path to the file containing the recording.")
    args = parser.parse_args()
    
    event_list = [
        event_definitions.speeding_start,
        event_definitions.speeding_end,
        event_definitions.cruise_control_activated,
        event_definitions.cruise_control_deactivated,
        ]
    
    if(args.file):
        process_sample_file(args.file)

