from grpc_health.v1 import health_pb2_grpc, health_pb2

from .client import Client


class HealthClient(Client):

    def get_stub(self):
        return health_pb2_grpc.HealthStub(self.channel)

    def healthcheck(self):
        response = self.unary_call(self.get_stub().Check, health_pb2.HealthCheckRequest(service=''))
        if response.status == health_pb2.HealthCheckResponse.SERVING:
            return True
        return False
