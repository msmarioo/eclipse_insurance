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
import service_discovery.v1.service_registry_pb2 as service_registry_pb2
import service_discovery.v1.service_registry_pb2_grpc as service_registry_pb2_grpc

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

mqttClient = None


def collectRequiredSignalIDs() -> list:
    #return ["dtmi:sdv:Trailer:Weight;1", "dtmi:sdv:Trailer:IsTrailerConnected;1"]
    return ["dtmi:sdv:Trailer:Weight;1"]


def findSignalByID(signalID, digitalTwinServiceMetadata) -> invehicle_digital_twin_pb2.EntityAccessInfo:  

    print(f"Finding signal {signalID} in Digital Twin Service {digitalTwinServiceMetadata.name} at {digitalTwinServiceMetadata.uri}")

    serviceAddress = digitalTwinServiceMetadata.uri.strip("http://").strip("https://")

    with closing(grpc.insecure_channel(serviceAddress)) as channel:
        stub = invehicle_digital_twin_pb2_grpc.InvehicleDigitalTwinStub(channel)
        request = invehicle_digital_twin_pb2.FindByIdRequest(
            id=signalID
        )

        try:
            response = stub.FindById(request)
            print(f"Signal {response}")
        except grpc.RpcError as e:
            print(f"Error finding signal {signalID}: {e}")

    return response.entityAccessInfo

def getSubscriptionInfo(entityAccessInfo) -> managed_subscribe_pb2.SubscriptionInfoResponse:
    print(f"Getting subscription info for {entityAccessInfo.name}")

    serviceAddress = entityAccessInfo.endpointInfoList[0].uri.strip("http://").strip("https://")
    with closing(grpc.insecure_channel(serviceAddress)) as channel:
        stub = managed_subscribe_pb2_grpc.ManagedSubscribeStub(channel)
        request = managed_subscribe_pb2.SubscriptionInfoRequest(
           entityId = entityAccessInfo.id
        )
        response = stub.GetSubscriptionInfo(request)
        print(f"Subscription Info: {response}")

    return response


def subscribe(subscriptionInfo):

    if (subscriptionInfo.protocol == "mqtt_v5"):
        startClient(subscriptionInfo)
        print(f"Subscribing to signal on topic {subscriptionInfo.context} using {subscriptionInfo.protocol} at {subscriptionInfo.uri}")
        mqttClient.subscribe(subscriptionInfo.context)
    

def startClient(subscriptionInfo):
    global mqttClient
    if (mqttClient == None):
        mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
        mqttClient.on_connect = on_connect
        mqttClient.on_message = on_message


        # Extract the address and the port from a string with the form  "mqtt://0.0.0.0:1883"
        address = subscriptionInfo.uri.split("//")[1].split(":")[0]
        port = int(subscriptionInfo.uri.split("//")[1].split(":")[1])

        mqttClient.connect(address, port, 60)
        mqttClient.loop_start()



def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    print("Received message: " + msg.payload.decode())


if __name__ == "__main__":

    digitalTwinServiceMetadata = discoverDigitalTwinService()

    requiredSignalIDs = collectRequiredSignalIDs()

    for signalID in requiredSignalIDs:
        signal = findSignalByID(signalID, digitalTwinServiceMetadata)
        subscriptionInfo = getSubscriptionInfo(signal)
        subscribe(subscriptionInfo)


    mqttClient.loop_forever()


    


