import logging

import grpc

logger = logging.getLogger('telegram_notifier')


class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # Call the next handler in the chain
        handler = continuation(handler_call_details)
        if handler and handler.unary_unary:
            def new_handler(request, context):
                logger.info(f'Call {handler_call_details.method}')
                try:
                    return handler.unary_unary(request, context)
                except Exception:
                    logger.exception('Exception: ')
                    raise

            return grpc.unary_unary_rpc_method_handler(
                new_handler,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler
