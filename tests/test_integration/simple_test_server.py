from concurrent import futures
import sys

import grpc
from grpc_health.v1 import health, health_pb2_grpc

if __name__ == "__main__":
    port = sys.argv[1]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()
