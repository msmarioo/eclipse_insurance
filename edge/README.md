<!--
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
-->
# Edge components

This code implements risk event detectors that categorize driving style.

![Edge Overview](/docs/images/edge-overview.svg)

# Structure of the directory

The directory has the follopwing structure

- *applications / insurance_event_detector* contains the python code for the main application
- *digital-twin-providers / vehicle_properties_provider* contains the python code that registers the signals and simulates the vehicle, described as 2b in the diagram
- *digital-twin-model* contains a DTDL representation of the COVESA signal specification used in the project.
- *proto-build* contains all Python gRPC interfaces to the different components (service_discovery, invehicle_digital_twin, module)

## Risk Events Detector

Each Risk event detector monitors vehicle signals everytime that they change, at a given refresh rate. The algorithm of each event detector varies - in some cases it requires analyzing previous data, or it can be a simple ramp up or ramp down threshold detection.

Once an event is triggered, the event detector will capture additional signals before and after the event.

The following events react on a flank up or flank down

| Event             | Monitored Signals             |   Additional Captured Signals    |
|-------------------|-------------------------------|-----------------------|
| speeding_start | Vehicle Speed    | 
| speeding_end | Vehicle Speed |
| cruise_control_activated |ADAS_CruiseControl_IsActive | Vehicle Speed
| cruise_control_deactivated | ADAS_CruiseControl_IsActive | Vehicle Speed
| harsh_braking | Vehicle_Acceleration_Lateral | Vehicle Acceleration Longitudinal / Lateral, Speed, Brake Pressure, Steering Wheel Angle, ADAS ABS Error, ADAS ABS Is Engaged, ADAS TCS IsEngaged
| harsh_acceleration | Vehicle_Acceleration_Lateral | Vehicle Acceleration Longitudinal / Lateral, Speed, Accelerator Pedal Position, Steering Wheel Angle, ADAS ABS Error, ADAS ABS Is Engaged, ADAS TCS IsEngaged
| harsh_cornering | Vehicle_Acceleration_Longitudinal | Vehicle Acceleration Longitudinal / Lateral, Speed, Brake Pressure, Accelerator Pedal Position, Steering Wheel Angle, Steering Wheel Angle Sign, Left Turn Light Indicator, Right Turn Light Indicator, ADAS TCS IsEngaged. Vehicle Speed Wheel Front Left / Front Right / Rear Left / Rear Right

## Integration with Orchestration Blueprint

The Insurance Event Detector uses charriot to discover the digital twin service. It will collect all necessary signals and use the digital twin service to detemrine if they exist. Once the signals are discovered, it will use the managed subscribed (through the digital twin service) to read the metadata and connect.

![Edge Overview](/docs/images/eclipse-orchestration-integration.svg)

To provide simulation, a vehicle provider will register signals (described in a DTDL file) and provide updates using a sample CSV file. The CSV file has the following structure:

``` csv
source_id, signal, timestamp, value
"b7ed5744-8715-4b3d-a322-7c7e0c399f69","Vehicle_Speed_Wheel_RearLeft","142.785732","53.715"
"b7ed5744-8715-4b3d-a322-7c7e0c399f69","Vehicle_Speed_Wheel_FrontRight","142.785732","54.3975"
"b7ed5744-8715-4b3d-a322-7c7e0c399f69","Vehicle_Speed_Wheel_FrontLeft","142.785732","53.685"
"b7ed5744-8715-4b3d-a322-7c7e0c399f69","Vehicle_Speed_Wheel_RearRight","142.785732","54.225"
```

# Running the application

As a prerequisite to run he application, it is necessary to run the base modules of the orchestration blueprint. Make sure that the network is the same (e.g. host).

The following modules should be running - for example, when running using Eclipse Ankaios using docker and the local network from the Eclupse Orchestration project (asumming the code is checked out in ~/repos/maestro-challenge).

``` bash
docker run -it --privileged --name custom_ankaios_dev -v ~/repos/maestro-challenge/eclipse-ankaios:/workspaces/app -v ~/repos/maestro-challenge/in-vehicle-stack:/workspaces/app/in-vehicle-stack --network host -p 25551:25551 --workdir /workspaces/app custom-ankaios-dev:0.1  /bin/bash
```

follow the instructions to run the base workloads using the run_maestro.sh script. listing the workloads

```bash
/workspaces/app# ank get workloads
 WORKLOAD NAME              AGENT     RUNTIME   EXECUTION STATE
 digital_twin_cloud_sync    agent_A   podman    Running
 digital_twin_vehicle       agent_A   podman    Running
 dynamic_topic_management   agent_A   podman    Running
 mqtt_broker                agent_A   podman    Running
 service_discovery          agent_A   podman    Running
```

Once this is running it is possible to run the vehicle_provider and the insurance_event_detector applications

As an example, assuming that the folder .sampledata contains a file harshdriving_1_bf827518de5942aea7727c064dcd381e.csv as a recording, the following calls will register the digital twin, start the insurance application and then start the replay.

```bash

python -m digital_twin_providers.vehicle_properties_provider.main -t ./digital-twin-model/dtdl/vehicle.json

python -m  applications.insurance_event_detector.main -f ../.sampledata/harshdriving_1_bf827518de5942aea7727c064dcd381e.csv

python -m digital_twin_providers.vehicle_properties_provider.main -r ../.sampledata/harshdriving_1_bf827518de5942aea7727c064dcd381e.csv

```