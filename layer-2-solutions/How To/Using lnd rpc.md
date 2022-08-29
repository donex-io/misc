# Using lnd rpc

This follows

https://dev.lightning.community/guides/python-grpc/

For this guide you need:

	sudo apt install python3-virtualenv
	sudo apt install curl


Lnd uses the gRPC protocol for communication with clients like lncli. gRPC is based on protocol buffers and as such, you will need to compile the lnd proto file in Python before you can use it to communicate with lnd.

Create a virtual environment for your project

	$ virtualenv lnd

Activate the virtual environment

	$ source lnd/bin/activate
Install dependencies (googleapis-common-protos is required due to the use of google/api/annotations.proto)
	
	(lnd)$ pip install grpcio grpcio-tools googleapis-common-protos

Clone the google api’s repository (required due to the use of google/api/annotations.proto)

	(lnd)$ git clone https://github.com/googleapis/googleapis.git

Copy the lnd rpc.proto file (you’ll find this at lnrpc/rpc.proto) or just download it

	(lnd)$ curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto

More information about Proto files: https://developers.google.com/protocol-buffers/docs/pythontutorial

Add additional proto files like invoices by:

	(lnd)$ curl -o invoices.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/invoicesrpc/invoices.proto

	(lnd)$ curl -o router.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/routerrpc/router.proto

Compile the proto files

	(lnd)$ python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto

	(lnd)$ python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. invoices.proto

	(lnd)$ python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. router.proto


