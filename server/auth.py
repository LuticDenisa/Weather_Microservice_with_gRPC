# gRPC interceptor that checks x-api-key
import grpc
from .config import SERVICE_API_KEY

class ApiKeyInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata or [])
        if metadata.get('x-api-key') != SERVICE_API_KEY:
            def deny(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid x-api-key')
            return grpc.unary_unary_rpc_method_handler(deny)
        return continuation(handler_call_details)
    
    