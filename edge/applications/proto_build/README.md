# Proto files to interface with vehicle stack

Contains the proto files used by python applications to talk to the stack.
These proto files are build from the orchestration blue print.

To recreate the proto files, check out the orchestration blue print, and from outside the devcontainer
set the ORCHESTRATION_REPO variable and call the generate_proto.sh

Assuming that the orchestration repo is in ~/repos and checked out as maestro-challenge

```bash
export ORCHESTRATION_REPO=~/repos/maestro-challenge/in-vehicle-stack/interfaces
./generate_proto.sh
```
