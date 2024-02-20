
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
            "value": 130
        },
        {   
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 130
        }
        ],
    eventData = {
        # Lets collect some speed information to understand what happens - sustained or a peak?
        "Vehicle_Speed_Speed": 100,
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
            "value": 130
        },
        {   
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "gt",
            "value": 130
        }
        ],
    eventData = {
        "Vehicle_Speed_Speed": 1,
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
        # Additional context information, at what speed is the cruise control activated?
        "Vehicle_Speed_Speed": 20,       
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
        # Additional context information, at what speed is the cruise control activated?
        "Vehicle_Speed_Speed": 20,        
        },
    timeout = 0
    )


harsh_braking = EventDefinition(
    name = "harsh_braking",
    eventId = 3.1,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": -2
        },
        {   
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": -2
        }
        ],
    eventData = {
        # Additional context information
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the actions of the user, such as how hard the person is braking and any swerve for post analytics
        "Chassis_Brake_Pressure": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Vehicle_Acceleration_Lateral": 20,
        # Also lets collect some information about the car -Are the TCS and ABS system healthy and did they activate as part of the maneuver?
        "ADAS_ABS_Error": 20,
        "ADAS_ABS_IsEngaged": 20,
        "ADAS_TCS_IsEngaged": 20,        
        },
    timeout = 0
    )

harsh_acceleration = EventDefinition(
    name = "harsh_acceleration",
    eventId = 3.2,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 2
        },
        {   
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 2
        }
        ],
    eventData = {
        # Additional context information
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the actions of the user, such as how hard the person is braking and any swerve for post analytics
        "Chassis_Accelerator_PedalPosition": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Vehicle_Acceleration_Lateral": 20,
        # Also lets collect some information about the car -Are the TCS and ABS system healthy and did they activate as part of the maneuver?
        "ADAS_ABS_Error": 20,
        "ADAS_ABS_IsEngaged": 20,
        "ADAS_TCS_IsEngaged": 20,        
        },
    timeout = 0
    )


harsh_cornering = EventDefinition(
    name = "harsh_cornering",
    eventId = 3.3,
    riskLevel = 1,
    conditions =  [
        {
            "signal_name": "Vehicle_Acceleration_Lateral",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 0.5
        },
        {   
            "signal_name": "Vehicle_Acceleration_Lateral",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 0.5
        }
        ],
    eventData = {
        # Additional context information: What were the G-Forces and what was the vehicle speed
        "Vehicle_Acceleration_Lateral": 20,
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the harsh cornering, such as acceleration and braking profile, steering wheel angle and turn indicator used.
        "Chassis_Brake_Pressure": 20,
        "Chassis_Accelerator_PedalPosition": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Chassis_SteeringWheel_AngleSign": 20,
        "Body_Lights_IsRightIndicatorOn": 20,
        "Body_Lights_IsLeftIndicatorOn": 20,
        # Also lets collect some information about the car: Did the TCS engage? and lets get the wheel speeds too!
        "ADAS_TCS_IsEngaged": 20,
        "Vehicle_Speed_Wheel_FrontLeft": 20,
        "Vehicle_Speed_Wheel_FrontRight": 20,
        "Vehicle_Speed_Wheel_RearLeft": 20,
        "Vehicle_Speed_Wheel_RearRight": 20,
        },
    timeout = 0
    )

# 
