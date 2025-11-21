from fastapi.testclient import TestClient
from gateway.main import app
import grpc

# -- fake objects pt grpc -- 

class FakeSnapshot:
    def __init__(self, city="London", t=12.3, d="few clouds", h=60, w=3.1, ts=1710000000000):
        self.city = city
        self.temperature_c = t
        self.description = d
        self.humidity = h
        self.wind_speed = w
        self.timestamp_ms = ts

class FakeCurrentResp:
    def __init__(self, snapshot: FakeSnapshot):
        self.snapshot = snapshot

class FakeHistoryResp:
    def __init__(self, series):
        self.series = series

class DummyRpcError(grpc.RpcError):
    def __init__(self, code, details):
        self._code = code
        self._details = details
    def code(self):
        return self._code
    def details(self):
        return self._details

class FakeStub:
    def __init__(self, current_ok=True, history_ok=True):
        self.current_ok = current_ok
        self.history_ok = history_ok
    def GetCurrentWeather(self, req, metadata=None, timeout=None):
        if not self.current_ok:
            raise DummyRpcError(grpc.StatusCode.NOT_FOUND, "City not found")
        return FakeCurrentResp(FakeSnapshot(city=req.city))
    def GetWeatherHistory(self, req, metadata=None, timeout=None):
        if not self.history_ok:
            raise DummyRpcError(grpc.StatusCode.INTERNAL, "db error")
        return FakeHistoryResp([
            FakeSnapshot(city=req.city, t=10.0, ts=req.from_ms + 1000),
            FakeSnapshot(city=req.city, t=11.0, ts=req.to_ms - 1000),
        ])

# -- teste ---

def test_gateway_current_ok():
    with TestClient(app) as client:
        app.state.grpc_stub = FakeStub(current_ok=True)
        r = client.get("/api/weather/current", params={"city": "London"})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["city"] == "London"
        assert "temperature_c" in data
        assert "timestamp_ms" in data

def test_gateway_current_not_found_maps_to_404():
    with TestClient(app) as client:
        app.state.grpc_stub = FakeStub(current_ok=False)
        r = client.get("/api/weather/current", params={"city": "NoWhere"})
        assert r.status_code == 404
        assert "NOT_FOUND" in r.json()["detail"]
        

def test_gateway_history_defaults_last_24h_and_returns_points():
    with TestClient(app) as client:
        app.state.grpc_stub = FakeStub(history_ok=True)
        r = client.get("/api/weather/history", params={"city": "London"})
        assert r.status_code == 200, r.text
        series = r.json()
        assert isinstance(series, list)
        assert len(series) == 2
        assert all(p["city"] == "London" for p in series)

def test_gateway_history_invalid_range_400():
    with TestClient(app) as client:
        app.state.grpc_stub = FakeStub(history_ok=True)
        r = client.get("/api/weather/history", params={"city": "London", "from_ms": 1000, "to_ms": 999})
        assert r.status_code == 400

class FakeStubErr:
    def GetCurrentWeather(self, req, metadata=None, timeout=None):
        raise DummyRpcError(grpc.StatusCode.INTERNAL, "boom")
    def GetWeatherHistory(self, req, metadata=None, timeout=None):
        raise DummyRpcError(grpc.StatusCode.UNAVAILABLE, "downstream")
    
def test_gateway_current_internal_maps_to_502():
    with TestClient(app) as client:
        app.state.grpc_stub = FakeStubErr()
        r = client.get("/api/weather/current", params={"city": "X"})
        assert r.status_code == 502
        assert "INTERNAL" in r.json()["detail"]

