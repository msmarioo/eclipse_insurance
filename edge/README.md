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