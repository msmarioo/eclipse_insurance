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

import argparse

import grpc

from common import discoverDigitalTwinService

import invehicle_digital_twin.v1.invehicle_digital_twin_pb2 as invehicle_digital_twin_pb2
import invehicle_digital_twin.v1.invehicle_digital_twin_pb2_grpc as invehicle_digital_twin_pb2_grpc

import module.managed_subscribe.v1.managed_subscribe_pb2 as managed_subscribe_pb2
import module.managed_subscribe.v1.managed_subscribe_pb2_grpc as managed_subscribe_pb2_grpc

import paho.mqtt.client as mqtt
import csv
import json
import time

CHARIOTT_SERVICE_DISCOVERY_URI = "0.0.0.0:50000"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE = "sdv.ibeji"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAME = "invehicle_digital_twin"
INVEHICLE_DIGITAL_TWIN_SERVICE_VERSION = "1.0"

MQTT_SERVER = "0.0.0.0"
MQTT_PORT = 1883


def registerSignals(digitalTwinServiceMetadata, twinFile):
    print(f"Registering signals with Digital Twin Service {digitalTwinServiceMetadata.name} at {digitalTwinServiceMetadata.uri}")

    # Read the required signal IDs from the dtdl json file
    
    # Read the json file
    with open(twinFile) as f:
        data = json.load(f)

        # Iterate over the signals
        for signal in data['contents']:
            if (signal['@type'] == "Property"):
                # Register the signal with the digital twin service
                registerSignal(signal, digitalTwinServiceMetadata)



def registerSignal(signal, digitalTwinServiceMetadata):	
    print(f"Registering signal {signal['@id']} in Digital Twin Service {digitalTwinServiceMetadata.name} at {digitalTwinServiceMetadata.uri}")

    serviceAddress = digitalTwinServiceMetadata.uri.strip("http://").strip("https://")

    with closing(grpc.insecure_channel(serviceAddress)) as channel:
        stub = invehicle_digital_twin_pb2_grpc.InvehicleDigitalTwinStub(channel)

        # Create the context by replacing all _ to / from the signal name
        context = signal['name'].replace("_", "/")        

        request = invehicle_digital_twin_pb2.RegisterRequest(
            entityAccessInfoList = [
                invehicle_digital_twin_pb2.EntityAccessInfo(
                    name=signal['name'],
                    id=signal['@id'],
                    description="",
                    endpointInfoList=[
                        invehicle_digital_twin_pb2.EndpointInfo(
                            protocol="mqtt_v5",
                            operations = ["subscribe"],
                            uri=f"mqtt://{MQTT_SERVER}:{MQTT_PORT}",
                            context=context
                        )
                    ]
                )
            ]
        )
        
        response = stub.Register(request)
        print(f"Signal Registered {response}")


def sendData(recordingFile):
    print(f"Sending data from {recordingFile}")

    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5, client_id="provider")
    mqttClient.on_connect = on_connect
    mqttClient.on_publish = on_publish

    mqttClient.connect(MQTT_SERVER, MQTT_PORT, 60)

    # iterate over the CSV file and publish the data to the mqtt broker
    with open(recordingFile, newline='') as csvfile:
      
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # Ignore the first line, which is the header
        next(reader)

        previoustimestamp = 0

        for row in reader:
            topic = row[1].replace("_", "/")
            data = float(row[3])
            timestamp = float(row[2])

            sleepTime = timestamp - previoustimestamp
            time.sleep(sleepTime)
            print(f"Publishing {data} to {topic} with timestamp {timestamp} and sleep time {sleepTime} s")
            ret, mid = mqttClient.publish(topic, data, qos=1)
            
            previoustimestamp = timestamp

            


def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected to MQTT broker with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Published message with id {mid}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Starts the sample process")
    parser.add_argument("-r", "--recording", dest="recordingFile")
    parser.add_argument("-t", "--twin", dest="twinFile")
    args = parser.parse_args()

    digitalTwinServiceMetadata = discoverDigitalTwinService()

    if (args.twinFile):
        registerSignals(digitalTwinServiceMetadata, twinFile=args.twinFile)

    if (args.recordingFile):
        sendData(args.recordingFile)
    

