import logging
from concurrent import futures

import grpc
from grpc_health.v1 import health_pb2_grpc, health, health_pb2

from .interceptors import LoggingInterceptor
from .notifier_utils.config import NotifierConfig
from .notifier_utils.pb import notifier_pb2_grpc
from .services.notifier_service import NotifierService

logger = logging.getLogger('telegram_notifier')


def serve(config: NotifierConfig):
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.server_max_workers),
        interceptors=(LoggingInterceptor(),)
    )

    health_servicer = health.HealthServicer()

    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    notifier_pb2_grpc.add_NotifierServiceServicer_to_server(
        NotifierService(max_workers=config.service_max_threads, only_print=config.only_print),
        server
    )

    health_servicer.set(
        service='',  # empty string means overall server health
        status=health_pb2.HealthCheckResponse.SERVING,
    )

    server.add_insecure_port(f'{config.server_url}:{config.server_port}')
    server.start()
    logger.info('telegram notifier server is running...')
    server.wait_for_termination()
