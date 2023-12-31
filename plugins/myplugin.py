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

import process

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
        return
        # return if use the independent grpc server ,don't stop the server
        #
        event = self._server.stop(self._grace)  # type: threading.Event
        if not event.wait():
            self._server.stop(0)
        return grpc_controller_pb2.Empty()

class ModelServicer(model_pb2_grpc.ModelServicer):
    """Implementation of Model service."""

    def Exec(self, request, context):
        name = request.name
        argsStr = request.payload.decode()
        result = model_pb2.Response()
        response = {
            'code':0,
            'data':'',
            'message':''
        }
        args = []
        if args != "":
            args = json.loads(argsStr)

        if name == 'embed':
            if len(args) > 0:
               content = args[0]
               response['data'] = process.Embedding(content)
            else:
                response['message'] = 'missing the args'
        else:
           response['message'] = 'request not supported'


        json_data = json.dumps(response)
        json_bytes = json_data.encode()

        result.response = json_bytes
        # 支持的类型：map/interface/string/integer,int/float,double/array,slice
        result.type = 'map'
        sys.stdout.flush()
        return result
        
def serve():

    logging.basicConfig(
        filename="myplugin.log",
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
    server.start()
    log.info("Server started")

    # Output handshake information
    # tcp is the communication protocal
    # 1234 is the http port
    handshake = "1|1|tcp|127.0.0.1:1234|grpc"
    
    log.debug(f"Handshake: '{handshake}'")
    print(handshake, flush=True)

    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()