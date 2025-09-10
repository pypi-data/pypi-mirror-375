import argparse
import os
import sys

from dotenv import load_dotenv

from .clients.health_client import HealthClient


def tg_notifier_healthcheck():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', default='[::]', required=False, help='gRPC server url')
    parser.add_argument('--port', default=50051, type=int, required=False, help='gRPC server port')
    parser.add_argument('--config-file', required=False, help='Config file for read settings from it')

    args = parser.parse_args()

    if args.config_file:
        load_dotenv(args.config_file)

    server_url = os.getenv('SERVER_URL', args.server_url)
    port = os.getenv('PORT', args.port)

    resp = HealthClient(server_url=server_url, server_port=port).healthcheck()
    if resp:
        sys.exit(0)
    sys.exit(1)
