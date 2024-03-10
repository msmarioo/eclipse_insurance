"""
SPDX-FileCopyrightText: 2023 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""
from contextlib import closing

import grpc

from common import discoverDigitalTwinService

import invehicle_digital_twin.v1.invehicle_digital_twin_pb2 as invehicle_digital_twin_pb2
import invehicle_digital_twin.v1.invehicle_digital_twin_pb2_grpc as invehicle_digital_twin_pb2_grpc


import module.managed_subscribe.v1.managed_subscribe_pb2 as managed_subscribe_pb2
import module.managed_subscribe.v1.managed_subscribe_pb2_grpc as managed_subscribe_pb2_grpc

import paho.mqtt.client as mqtt

CHARIOTT_SERVICE_DISCOVERY_URI = "0.0.0.0:50000"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE = "sdv.ibeji"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAME = "invehicle_digital_twin"
INVEHICLE_DIGITAL_TWIN_SERVICE_VERSION = "1.0"


def registerSignals(digitalTwinServiceMetadata):
    print(f"Registering signals with Digital Twin Service {digitalTwinServiceMetadata.name} at {digitalTwinServiceMetadata.uri}")


def sendData(digitalTwinServiceMetadata):
    print(f"Sending data to Digital Twin Service {digitalTwinServiceMetadata.name} at {digitalTwinServiceMetadata.uri}")

if __name__ == "__main__":

    digitalTwinServiceMetadata = discoverDigitalTwinService()

    registerSignals(digitalTwinServiceMetadata)

    sendData(digitalTwinServiceMetadata)
    

