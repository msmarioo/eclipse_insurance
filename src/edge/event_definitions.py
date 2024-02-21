
import numpy as np


def process_signal_data(condition, signal_data):
    method = condition["method"]
    context_length = condition["context_length"]
    if method:
        if context_length <= 1:
            raise ValueError("Context length must be above 1 when a method is applied.")
        
        if method == "prev":
            processed_signal_value = signal_data[-context_length]
        elif method == "mean":
            processed_signal_value = np.mean(signal_data[-context_length:])
        elif method == "min":
            processed_signal_value = min(signal_data[-context_length:])
        elif method == "max":
            processed_signal_value = max(signal_data[-context_length:])
        else:
            raise ValueError(f"Method {method} is not supported. Supported methods are: [prev, mean, min, max].")
    
    else:
        if context_length != 1:
            raise ValueError("Context length must be 1 if no method is applied.")
        
        processed_signal_value = signal_data[-1]
        
    return processed_signal_value
        
        
class EventDefinition:

    def __init__(self, name, eventId, riskLevel, conditions, eventData, timeout):
        self.name = name
        self.eventId = eventId
        self.riskLevel = riskLevel
        self.conditions = conditions
        self.eventData = eventData
        self.timeout = timeout
        
        self.relevant_signals = list(set([c["signal_name"] for c in self.conditions]))
    
    def check_condition(self, signal_dict):
        for cond in self.conditions:
            signal_value = process_signal_data(cond, signal_dict[cond["signal_name"]])
            if signal_value != signal_value:
                # Prevent positive events with nan
                return False
            elif cond["operator"] == "eq":
                if signal_value != cond["value"]:
                    return False
            elif cond["operator"] == "gt":
                if signal_value <= cond["value"]:
                    return False
            elif cond["operator"] == "lt":
                if signal_value >= cond["value"]:
                    return False
            elif cond["operator"] == "bt":
                cond_value = cond["value"]
                if type(cond_value) != tuple:
                    raise ValueError(f"Value must be a tuple when operator is 'bt'. Given is: {cond_value}")
                if signal_value <= cond_value[0] or signal_value >= cond_value[1]:
                    return False
            else:
                raise ValueError(f"Condition parameter {cond[0]} unsupported. Supported are [eq, gt, lt, bt].")
        return True
    
    def collect_callback_data(self, signal_dict):
        callback_data = {}
        for s, l in self.eventData.items():
            if l == 1:
                callback_data[s] = signal_dict[s][-1]
            elif l > 1:
                callback_data[s] = signal_dict[s][-l:]
            else:
                raise ValueError("Length of callback data must be greater 0.")
        return callback_data

##############################################################################

speeding_start = EventDefinition(
    name = "speeding_start",
    eventId = 1.1,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 100
        },
        {   
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 100
        }
        ],
    eventData = {
        "Vehicle_Speed_Speed": 1,
        # "OdometerValue": 1
        },
    timeout = 0
    )

speeding_end = EventDefinition(
    name = "speeding_end",
    eventId = 1.2,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "lt",
            "value": 100
        },
        {   
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "gt",
            "value": 100
        }
        ],
    eventData = {
        "Vehicle_Speed_Speed": 1,
        # "OdometerValue": 1
        },
    timeout = 0
    )



cruise_control_activated = EventDefinition(
    name = "cruise_control_activated",
    eventId = 2.1,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1
        },
        {   
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": "prev",
            "context_length": 2,
            "operator": "eq",
            "value": 2
        }
        ],
    eventData = {
        "ADAS_CruiseControl_IsActive": 1,
        # "OdometerValue": 1
        },
    timeout = 0
    )

cruise_control_deactivated = EventDefinition(
    name = "cruise_control_deactivated",
    eventId = 2.2,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 2
        },
        {   
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": "prev",
            "context_length": 2,
            "operator": "eq",
            "value": 1
        }
        ],
    eventData = {
        "ADAS_CruiseControl_IsActive": 1,
        # "OdometerValue": 1
        },
    timeout = 0
    )


