import pytest
import grpc
import requests

from server.weather_server import WeatherService
from server.generated import weather_pb2

# -- helpers / fakess --

class AbortExc(Exception):
    def __init__(self, code, details):
        self.code = code
        self.details = details
        super().__init__(f"{code.name}: {details}")

class Ctx:
    def abort(self, code, details):
        raise AbortExc(code, details)

class FakeDAO:
    def save_snapshot(self, snap): 
        return {**snap, "timestamp_ms": snap.get("timestamp_ms", 1234567890000)}
    def fetch_series(self, city, from_ms, to_ms):
        return []

def _http_error(status_code: int) -> requests.HTTPError:
    resp = requests.Response()
    resp.status_code = status_code
    err = requests.HTTPError()
    err.response = resp
    return err

# --- teste pentru GetCurrentWeather ---

def test_current_empty_city_invalid_argument():
    srv = WeatherService()
    srv.dao = FakeDAO()

    with pytest.raises(AbortExc) as exc:
        srv.GetCurrentWeather(weather_pb2.GetCurrentWeatherRequest(city="  "), Ctx())
    assert exc.value.code == grpc.StatusCode.INVALID_ARGUMENT
    assert "City name is required" in exc.value.details

def test_current_http_404_maps_to_not_found(monkeypatch):
    srv = WeatherService(); srv.dao = FakeDAO()

    class FakeOWM:
        def get_current(self, city): raise _http_error(404)
        def parse(self, raw): raise AssertionError("should not be called")
    srv.owm = FakeOWM()

    with pytest.raises(AbortExc) as exc:
        srv.GetCurrentWeather(weather_pb2.GetCurrentWeatherRequest(city="X"), Ctx())
    assert exc.value.code == grpc.StatusCode.NOT_FOUND
    assert "City not found" in exc.value.details

def test_current_http_401_maps_to_failed_precondition():
    srv = WeatherService(); srv.dao = FakeDAO()
    class FakeOWM:
        def get_current(self, city): raise _http_error(401)
        def parse(self, raw): raise AssertionError("should not be called")
    srv.owm = FakeOWM()

    with pytest.raises(AbortExc) as exc:
        srv.GetCurrentWeather(weather_pb2.GetCurrentWeatherRequest(city="X"), Ctx())
    assert exc.value.code == grpc.StatusCode.FAILED_PRECONDITION
    assert "OWM_API_KEY" in exc.value.details

def test_current_http_500_maps_to_unavailable():
    srv = WeatherService(); srv.dao = FakeDAO()
    class FakeOWM:
        def get_current(self, city): raise _http_error(500)
        def parse(self, raw): raise AssertionError("should not be called")
    srv.owm = FakeOWM()

    with pytest.raises(AbortExc) as exc:
        srv.GetCurrentWeather(weather_pb2.GetCurrentWeatherRequest(city="X"), Ctx())
    assert exc.value.code == grpc.StatusCode.UNAVAILABLE
    assert "Upstream error 500" in exc.value.details

def test_current_generic_exception_maps_to_internal():
    srv = WeatherService(); srv.dao = FakeDAO()
    class FakeOWM:
        def get_current(self, city): raise RuntimeError("boom")
        def parse(self, raw): raise AssertionError("should not be called")
    srv.owm = FakeOWM()

    with pytest.raises(AbortExc) as exc:
        srv.GetCurrentWeather(weather_pb2.GetCurrentWeatherRequest(city="X"), Ctx())
    assert exc.value.code == grpc.StatusCode.INTERNAL
    assert "boom" in exc.value.details

# --- teste pentru GetWeatherHistory ---

def test_history_invalid_range_invalid_argument_from_ge_to():
    srv = WeatherService(); srv.dao = FakeDAO()
    with pytest.raises(AbortExc) as exc:
        srv.GetWeatherHistory(
            weather_pb2.GetWeatherHistoryRequest(city="X", from_ms=2000, to_ms=1000),
            Ctx()
        )
    assert exc.value.code == grpc.StatusCode.INVALID_ARGUMENT
    assert "Invalid time range" in exc.value.details

def test_history_empty_city_invalid_argument():
    srv = WeatherService(); srv.dao = FakeDAO()
    with pytest.raises(AbortExc) as exc:
        srv.GetWeatherHistory(
            weather_pb2.GetWeatherHistoryRequest(city="  ", from_ms=1, to_ms=2),
            Ctx()
        )
    assert exc.value.code == grpc.StatusCode.INVALID_ARGUMENT
    assert "City name is required" in exc.value.details
