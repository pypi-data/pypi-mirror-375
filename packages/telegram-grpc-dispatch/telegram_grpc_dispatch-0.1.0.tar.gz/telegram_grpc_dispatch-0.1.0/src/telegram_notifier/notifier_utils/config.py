import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .set_logger import setup_logging


@dataclass
class NotifierConfig:
    server_url: str
    server_port: int
    server_max_workers: int
    service_max_threads: int
    only_print: bool


def get_notifier_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', default='[::]', required=False, help='gRPC server url')
    parser.add_argument('--port', default=50051, type=int, required=False, help='gRPC server port')
    parser.add_argument('--workers', default=10, type=int, required=False, help='Server max workers')
    parser.add_argument('--threads', default=10, type=int, required=False,
                        help='Service max threads for background task')
    parser.add_argument('--only-print', default=False, required=False, action='store_true',
                        help="Don't send message to telegram. Only log message in log file.")
    parser.add_argument('--log-level', default='INFO', required=False, help='Log level')
    parser.add_argument('--log-file', default='.', required=False,
                        help='Write logs to this file. use `.` for log in stdout')
    parser.add_argument('--config-file', required=False, help='Config file for read settings from it')

    args = parser.parse_args()

    if args.config_file:
        load_dotenv(args.config_file)

    server_url = os.getenv('SERVER_URL', args.server_url)
    server_port = os.getenv('SERVER_PORT', args.port)
    workers = os.getenv('WORKERS', args.workers)
    threads = os.getenv('THREADS', args.threads)
    if only_print := os.getenv('ONLY_PRINT') is not None:
        if only_print in ('True', 'true'):
            only_print = True
        elif only_print in ('False', 'false'):
            only_print = False
    else:
        only_print = args.only_print

    setup_logging(
        level=os.getenv('LOG_LEVEL', args.log_level),
        log_file=os.getenv('LOG_FILE', args.log_file),
    )

    return NotifierConfig(
        server_url=server_url,
        server_port=server_port,
        server_max_workers=int(workers),
        service_max_threads=int(threads),
        only_print=only_print,
    )
