import logging
from typing import Callable

import grpc

logger = logging.getLogger('telegram_notifier')


class Client:
    def __init__(self, server_url: str, server_port: int):
        self.server_url = server_url
        self.server_port = server_port
        self.channel = grpc.insecure_channel(f'{self.server_url}:{self.server_port}')

    @staticmethod
    def unary_call(func: Callable, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as rpc_error:
            logger.error(f'rpc call failed: code = {rpc_error.code()}, details = {rpc_error.details()}')
            return rpc_error.code()

    def get_stub(self):
        raise NotImplementedError()
