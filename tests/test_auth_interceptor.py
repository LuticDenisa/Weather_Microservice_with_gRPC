import grpc
from server.auth import ApiKeyInterceptor

_called = False

def _continuation(details):
    global _called
    _called = True
    return grpc.unary_unary_rpc_method_handler(lambda req, ctx: None)

class _Details:
    def __init__(self, metadata=None):
        self.method = "/weather.WeatherService/GetCurrentWeather"
        self.invocation_metadata = metadata or []

def test_interceptor_missing_key_returns_unauthenticated():
    global _called; _called = False
    itc = ApiKeyInterceptor()
    handler = itc.intercept_service(_continuation, _Details(metadata=[]))
    assert _called is False

def test_interceptor_ok_allows_through(monkeypatch):
    global _called; _called = False
    monkeypatch.setenv("SERVICE_API_KEY", "dev-secret")

    itc = ApiKeyInterceptor()
    md = [("x-api-key", "dev-secret")]
    handler = itc.intercept_service(_continuation, _Details(metadata=md))
    assert _called is True
    assert hasattr(handler, "unary_unary")
