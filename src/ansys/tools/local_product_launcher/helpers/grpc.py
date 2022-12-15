"""Helpers for interacting with gRPC servers."""

from typing import Optional

import grpc
from grpc_health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import HealthStub


def check_grpc_health(channel: grpc.Channel, timeout: Optional[float] = None) -> bool:
    """Check that a gRPC server is responding to health check requests.

    Parameters
    ----------
    channel :
        Channel to the gRPC server.
    timeout :
        Timeout for the gRPC health check request.

    Returns
    -------
    :
        ``True`` if the health check succeeded, otherwise ``False``.
    """
    try:
        res = HealthStub(channel).Check(
            request=HealthCheckRequest(),
            timeout=timeout,
        )
        if res.status == HealthCheckResponse.ServingStatus.SERVING:
            return True
    except grpc.RpcError:
        pass
    return False
