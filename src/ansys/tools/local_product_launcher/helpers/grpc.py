from typing import Optional

import grpc
from grpc_health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import HealthStub


def check_grpc_health(channel: grpc.Channel, timeout: Optional[float] = None) -> bool:
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
