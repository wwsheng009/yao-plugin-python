# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0
#!python
import signal
import threading
from concurrent import futures
import sys
import time
import json
import grpc
import logging

log = logging.getLogger(__name__)

from model import model_pb2
from model import model_pb2_grpc

from plugin import grpc_controller_pb2
from plugin import grpc_controller_pb2_grpc


from grpc_health.v1.health import HealthServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc



class GRPCControllerServicer(grpc_controller_pb2_grpc.GRPCControllerServicer):
    """
    ServerController implements controller requests in the server,
    sent by the client.
    """
    def __init__(self, server, grace=2):
        """
        Args:
            server (Server): Server instance
            grace (float): Graceful shutdown time in seconds
        """
        self._server = server  # type: Server
        self._grace = float(grace)
    def Shutdown(self, request, context):
        """
        Shut down the server using the configured grace period
        """
        log.info("Shutdown")
        event = self._server.stop(self._grace)  # type: threading.Event
        if not event.wait():
            self._server.stop(0)
        return grpc_controller_pb2.Empty()
        # # Implement your shutdown logic here
        # # You can access the request parameters using `request.<parameter_name>`
        # # Return a `ShutdownResponse` message to send a response back to the client
        # print("Shutdown the server...")
        # sys.stdout.flush()
        # server.stop(0)
        # exit()
        # # Set any necessary response parameters
        # return grpc_controller_pb2.Empty()

class ModelServicer(model_pb2_grpc.ModelServicer):
    """Implementation of Model service."""

    def Exec(self, request, context):
        name = request.name
        payload = request.payload
        string = payload.decode()
        result = model_pb2.Response()
        data = {
            'request name': name,
            'your intput': string
        }   
        json_data = json.dumps(data)
        json_bytes = json_data.encode()

        result.response = json_bytes
        # 支持的类型：map/interface/string/integer,int/float,double/array,slice
        result.type = 'map'
        sys.stdout.flush()
        return result

# Define a signal handler function for the OS kill signal
# def handle_os_kill_signal(signum, frame):
#     print("Received OS kill signal. Stopping the server...")
#     server.stop(0)
#     exit()


def serve():

    logging.basicConfig(
        filename="test.log",
        level=logging.INFO,
        format="{asctime}.{msecs:03.0f}:{levelname}:{name}:{message}",
        style="{",
        datefmt="%Y%m%d-%H%M%S",
    )

    # We need to build a health service to work with go-plugin
    health = HealthServicer()
    health.set("plugin", health_pb2.HealthCheckResponse.ServingStatus.Value('SERVING'))

    # Start the server.
    global server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    health_pb2_grpc.add_HealthServicer_to_server(health, server)
    model_pb2_grpc.add_ModelServicer_to_server(ModelServicer(), server)
    grpc_controller_pb2_grpc.add_GRPCControllerServicer_to_server(GRPCControllerServicer(server), server)

    server.add_insecure_port('127.0.0.1:1234')

    # # Register the signal handler for the OS kill signal
    # signal.signal(signal.SIGINT, handle_os_kill_signal)
    # signal.signal(signal.SIGTERM, handle_os_kill_signal)
    server.start()
    log.info("Server started")

    # Output information
    # print("1|1|tcp|127.0.0.1:1234|grpc")
    handshake = "1|1|tcp|127.0.0.1:1234|grpc"
    # sys.stdout.flush()
    
    log.debug(f"Handshake: '{handshake}'")
    print(handshake, flush=True)

    server.wait_for_termination()
    # log.info("Exit main")


    # 不要用下面的处理方法，要不然退不出
    # try:
    #     while True:
    #         time.sleep(60 * 60 * 24)
    # except KeyboardInterrupt:
    #     # print("Keyboard interrupt detected. Stopping the server...")
    #     log.info("Exit main")
    #     server.stop(0)
    #     exit()
    
if __name__ == '__main__':
    serve()