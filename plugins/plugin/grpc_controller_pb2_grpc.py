# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from plugin import grpc_controller_pb2 as grpc__controller__pb2


class GRPCControllerStub(object):
    """The GRPCController is responsible for telling the plugin server to shutdown.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Shutdown = channel.unary_unary(
                '/plugin.GRPCController/Shutdown',
                request_serializer=grpc__controller__pb2.Empty.SerializeToString,
                response_deserializer=grpc__controller__pb2.Empty.FromString,
                )


class GRPCControllerServicer(object):
    """The GRPCController is responsible for telling the plugin server to shutdown.
    """

    def Shutdown(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GRPCControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Shutdown': grpc.unary_unary_rpc_method_handler(
                    servicer.Shutdown,
                    request_deserializer=grpc__controller__pb2.Empty.FromString,
                    response_serializer=grpc__controller__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'plugin.GRPCController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class GRPCController(object):
    """The GRPCController is responsible for telling the plugin server to shutdown.
    """

    @staticmethod
    def Shutdown(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/plugin.GRPCController/Shutdown',
            grpc__controller__pb2.Empty.SerializeToString,
            grpc__controller__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)