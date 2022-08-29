import grpc
from api_pb2 import Request
from api_pb2_grpc import MethodStub

import os

host = os.getenv("APP_HOST", "localhost")
channel = grpc.insecure_channel(
    f"{host}:50051"
)
client = MethodStub(channel)

request = Request(id=1)
client.gRPC(request)