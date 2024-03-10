

# Generates the proto interface for the in-vehicle digital twin
python -m grpc_tools.protoc --proto_path ${ORCHESTRATION_REPO} --python_out=. --grpc_python_out=. ${ORCHESTRATION_REPO}/invehicle_digital_twin/v1/invehicle_digital_twin.proto

# Generates the proto interface for the managed subscribe
python -m grpc_tools.protoc --proto_path ${ORCHESTRATION_REPO} --python_out=. --grpc_python_out=. ${ORCHESTRATION_REPO}/module/managed_subscribe/v1/managed_subscribe.proto

# Generates the proto interface for the service discovery
python -m grpc_tools.protoc --proto_path ${ORCHESTRATION_REPO} --python_out=. --grpc_python_out=. ${ORCHESTRATION_REPO}/service_discovery/v1/service_registry.proto