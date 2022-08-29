# gRPC blueprint

Setting up an API

## Sources

[Real Python article](https://realpython.com/python-microservices-grpc/)

[Real Python code](https://github.com/realpython/materials/tree/master/python-microservices-with-grpc)

[gRPC.io](https://grpc.io/docs/what-is-grpc/introduction/)

## What to expect?

The idea is to build a microservice. This example is for Python but gRPC is independent of programming languages.

## Protocol buffers for server application

1. **Definition of API**: 
   
    Create a [protobufs](/protobufs/) folder and a [api.proto](/protobufs/api.proto) file where you define the API (incl. request, response and method).

    ```java
    // api.proto
    syntax = "proto3";
    message Request {
        int32 id = 1;
    }
    message Response {
        bool success = 1;
    }
    service Method {
        rpc gRPC (Request) returns (Response);
    }
    ```

2. **Install grpcio-tools**: 
   
   Create an [app](/app/) folder and a [requirements.txt](/app/requirements.txt) file which imports the latest gRPC library. 
   ```python
   # requirements.txt
   grpcio-tools ~= 1.30
   ```
   Note that [app/requirements.txt](/app/requirements.txt) might need more packages if required by the server application.

   Run the code locally in virtual environment:
    ```console
    $ python3 -m venv venv

    $ source venv/bin/activate

    (venv)$ python -m pip install -r app/requirements.txt
    ```

3. **Generate protobufs**: 

    ```console
    (venv)$ cd app

    (venv)$ python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/api.proto
    ```
    Now, the two python libraries `api_pb2.py` and `api_pb2_grpc.py` are created inside the [app](/app/) folder. Note that these files can be generated for multiple programming languages, so that these can use/provide the same API!

## Security

Create a certificate authority (CA) which owns a public key [ca.pem](/ca.pem) and a private key [ca.key](/ca.key) by

```console
$ openssl req -x509 -nodes -newkey rsa:4096 -keyout ca.key -out ca.pem -subj /O=me
```

Then create a certificate for the server

```console
$ openssl req -nodes -newkey rsa:4096 -keyout server.key -out server.csr  -subj /CN=app
```

which creates an intermediate file [server.csr](/server.csr) and the server’s private key [server.key](/server.key). Consequently, create a certificate by

```console
$ openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -set_serial 1 -out server.pem
```

which creates the server’s public certificate [server.pem](/server.pem).

## Python RPC server

* **Packages**:

    In python, the `grpc` package is needed. Since gRPC needs a thread pool, also `future` from the `concurrent` package is required. Finally, the API `Response` from [api_pb2](app/api_pb2.py) and the [api_pb2_grpc](app/api_pb2_grpc.py) is needed.

* **Microservice**:

    The microservice needs to be integrated using the subclass `MethodServicer` of [app_pb2_grpc](app/api_pb2_grpc.py).

* **Server**:

    In order to run the service constantly, a `grpc.server` has to be started which needs to be associates with the microservice class by `add_MethodServicer_to_server`. 

```python
# app/app.py
from concurrent import futures
import grpc
from api_pb2 import Response
import api_pb2_grpc

class AService(api_pb2_grpc.MethodServicer):
    # This method name must have the same name as the RPC you define in your protobuf file:
    def gRPC(self, request, context):
        
        # DO SOMETHING

        return Response(success=True)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )
    api_pb2_grpc.add_MethodServicer_to_server(
        Service(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
```
Save the complete file [app/app.py](/app/app.py). The port to connect to the server was defined by `server.add_insecure_port`. Note that there can also be a "secure" version! This is can be found in [app/app_secure.py](/app/app_secure.py).

To run the serivce, you can excecute:
```console
(venv)$ python app/app.py
```

## Python RPC client

Follow steps 2. to 3. to create the proto files also in the [client](/client/) folder (or just copy them from the [app](/app/) folder). Note that [client/requirements.txt](/client/requirements.txt) might need more packages if required by the client application.

* **Packages**:

    In python, the `grpc` package is needed. The API `Request` from [api_pb2](client/api_pb2.py) and `MethodStub` from [api_pb2_grpc](client/api_pb2_grpc.py) are needed.

* **Connection**:

    The connection to the server is establised by `grpc.insecure_channel` and `MethodStub`.

* **Sending request**:

    An API call can then be send by building a `Request` and sending it via the rpc defined in the [api.proto](/protobufs/api.proto) file.

```python
# client/client.py
import grpc
from api_pb2 import Request
from api_pb2_grpc import MethodStub

# For Docker, you can set an environment variable:
import os
host = os.getenv("APP_HOST", "localhost")

channel = grpc.insecure_channel(f"{host}:50051")
client = MethodStub(channel)

request = Request(id=1)
client.gRPC(request)
```

Save the complete file [client/client.py](/client/client.py).

To run the client, you can excecute:
```console
(venv)$ python client/client.py
```

## Docker image for microservice

Create a [Dockerfile](/app/Dockerfile) in the [app](/app/) folder:

```Dockerfile
# syntax = docker/dockerfile:1.0-experimental

FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY app/ /service/app/
COPY ca.pem /service/app/

WORKDIR /service/app
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/api.proto
RUN openssl req -nodes -newkey rsa:4096 -subj /CN=app -keyout server.key -out server.csr
RUN --mount=type=secret,id=ca.key openssl x509 -req -in server.csr -CA ca.pem -CAkey /run/secrets/ca.key -set_serial 1 -out server.pem

EXPOSE 50051
ENTRYPOINT [ "python", "app.py" ]
```

Then build the Docker image by

```console
$ sudo docker build . -f app/Dockerfile -t app
```

## Docker image for client

Create a [Dockerfile](/client/Dockerfile) in the [client](/client/) folder:
```Dockerfile
FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY client/ /service/client/
WORKDIR /service/client
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/api.proto

EXPOSE 5000
ENTRYPOINT [ "python", "client.py" ]
```

Then build the Docker image by

```console
$ sudo docker build . -f client/Dockerfile -t app
```