from contextlib import closing

import grpc
import service_discovery.v1.service_registry_pb2 as service_registry_pb2
import service_discovery.v1.service_registry_pb2_grpc as service_registry_pb2_grpc

import invehicle_digital_twin.v1.invehicle_digital_twin_pb2 as invehicle_digital_twin_pb2
import invehicle_digital_twin.v1.invehicle_digital_twin_pb2_grpc as invehicle_digital_twin_pb2_grpc

CHARIOTT_SERVICE_DISCOVERY_URI = "0.0.0.0:50000"

INVEHICLE_DIGITAL_TWIN_SERVICE_NAMESPACE = "sdv.ibeji"
INVEHICLE_DIGITAL_TWIN_SERVICE_NAME = "invehicle_digital_twin"
INVEHICLE_DIGITAL_TWIN_SERVICE_VERSION = "1.0"

#INVEHICLE_DIGITAL_TWIN_SERVICE_COMMUNICATION_KIND = "grpc+proto"
#INVEHICLE_DIGITAL_TWIN_SERVICE_COMMUNICATION_REFERENCE = "https://github.com/eclipse-ibeji/ibeji/blob/main/interfaces/digital_twin/v1/digital_twin.proto"



def discoverDigitalTwinService():
    """
    Discovers the Digital Twin Service using the CHARIOTT service discovery.

    This function establishes a connection to the CHARIOTT service discovery server
    and sends a DiscoverRequest to find the Digital Twin Service with the specified
    namespace, name, and version.

    Returns:
        None
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


def collectRequiredSignalIDs() -> list:
    return ["dtmi:sdv:Trailer:Weight;1", "dtmi:sdv:Trailer:IsTrailerConnected;1"]


def findSignalByID(signalID, digitalTwinServiceMetadata):  

    print(f"Finding signal {signalID} in Digital Twin Service")

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



def subscribe(signalID):
    print(f"Subscribing to signal {signalID}")


if __name__ == "__main__":

    digitalTwinServiceMetadata = discoverDigitalTwinService()

    requiredSignalIDs = collectRequiredSignalIDs()

    for signalID in requiredSignalIDs:
        signal = findSignalByID(signalID, digitalTwinServiceMetadata)
        subscribe(signalID)




    


