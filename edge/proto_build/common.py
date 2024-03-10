from contextlib import closing

import grpc
import service_discovery.v1.service_registry_pb2 as service_registry_pb2
import service_discovery.v1.service_registry_pb2_grpc as service_registry_pb2_grpc

import paho.mqtt.client as mqtt

CHARIOTT_SERVICE_DISCOVERY_URI = "0.0.0.0:50000"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE = "sdv.ibeji"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAME = "invehicle_digital_twin"
INVEHICLE_DIGITAL_TWIN_SERVICE_VERSION = "1.0"

def discoverDigitalTwinService() -> service_registry_pb2.ServiceMetadata:
    """
    Discovers the Digital Twin Service using the CHARIOTT service discovery.

    This function establishes a connection to the CHARIOTT service discovery server
    and sends a DiscoverRequest to find the Digital Twin Service with the specified
    namespace, name, and version.

    Returns:
        The discovered service
    """
    print(f"Discovering Digital Twin Service at {CHARIOTT_SERVICE_DISCOVERY_URI} with namespace {INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE} and name {INVEHICLE_DIGITAL_TWIN_SERVICE_NAME}")


    with closing(grpc.insecure_channel(CHARIOTT_SERVICE_DISCOVERY_URI)) as channel:
        stub = service_registry_pb2_grpc.ServiceRegistryStub(channel)
        request = service_registry_pb2.DiscoverRequest(
            namespace=INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE,
            name=INVEHICLE_DIGITAL_TWIN_SERVICE_NAME,
            version=INVEHICLE_DIGITAL_TWIN_SERVICE_VERSION
        )
        response = stub.Discover(request)
        print(f"Digital Twin Service discovered {response}")

        return response.service
