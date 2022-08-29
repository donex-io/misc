from concurrent import futures
import grpc
from api_pb2 import Response
import api_pb2_grpc

# The class name can be freely chosen:
class Service(api_pb2_grpc.MethodServicer):
    # This method name must have the same name as the RPC you define in your protobuf file:
    def gRPC(self, request, context):
        
        # DO SOMETHING

        return Response(success=True)

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    # This method associates your class with the server. This is like adding a handler for requests:
    api_pb2_grpc.add_MethodServicer_to_server(
        Service(), server
    )

    with open("server.key", "rb") as fp:
        server_key = fp.read()
    with open("server.pem", "rb") as fp:
        server_cert = fp.read()
    with open("ca.pem", "rb") as fp:
        ca_cert = fp.read()
    creds = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True,
    )
    server.add_secure_port("[::]:443", creds)

    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()