# Represents the Risk Event. This is the payload that will be send from the vehicle to the cloud
class RiskEvent:

    def __init__(self, name, riskLevel, value, timestamp, signalList):
        self.name = name
        self.riskLevel = riskLevel
        self.value = value
        self.timestamp = timestamp
        self.signalList = signalList

# For now, a risk detector needs to keep track of their own internal history.
def risk_detector(signal, callback):
    """
    Basic threshold detector
    """
    if signal.name == "Vehicle_Speed_Wheel_FrontRight":
        if signal.value > 100:
            callback(
                RiskEvent(
                    "Speeding",
                    1,
                    signal.value,
                    signal.timestamp,
                    [signal]
                )
            )
