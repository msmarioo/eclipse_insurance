# SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
##/ information regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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
