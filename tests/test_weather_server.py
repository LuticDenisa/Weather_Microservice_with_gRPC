import grpc
from server.weather_server import WeatherService
from server.generated import weather_pb2

class FakeDAO:
    def __init__(self): self.saved = []
    def save_snapshot(self, snap):
        snap = {**snap, "timestamp_ms": snap.get("timestamp_ms", 1234567890000)}
        self.saved.append(snap)
        return snap
    def fetch_series(self, city, from_ms, to_ms):
        return [
            {"city": city, "temperature_c": 10.0, "description": "ok", "humidity": 50, "wind_speed": 3.1, "timestamp_ms": from_ms+1},
            {"city": city, "temperature_c": 11.0, "description": "ok", "humidity": 51, "wind_speed": 3.0, "timestamp_ms": to_ms-1},
        ]

class FakeOWM:
    def get_current(self, city):
        return {
            "name": city,
            "main": {"temp": 12.3, "humidity": 60},
            "weather": [{"description": "few clouds"}],
            "wind": {"speed": 4.2},
        }
    def parse(self, raw):
        return {
            "city": raw["name"],
            "temperature_c": raw["main"]["temp"],
            "description": raw["weather"][0]["description"],
            "humidity": raw["main"]["humidity"],
            "wind_speed": raw["wind"]["speed"],
        }

class _Ctx:
    def abort(self, code, details):
        raise grpc.RpcError()

def test_service_get_current_weather_builds_snapshot():
    srv = WeatherService()
    srv.dao = FakeDAO()
    srv.owm = FakeOWM()
    req = weather_pb2.GetCurrentWeatherRequest(city="London")
    resp = srv.GetCurrentWeather(req, _Ctx())
    s = resp.snapshot
    assert s.city == "London"
    assert s.temperature_c == 12.3
    assert s.humidity == 60
    assert s.timestamp_ms > 0

def test_service_get_history_maps_points():
    srv = WeatherService()
    srv.dao = FakeDAO()
    req = weather_pb2.GetWeatherHistoryRequest(city="Paris", from_ms=1_000, to_ms=2_000)
    resp = srv.GetWeatherHistory(req, _Ctx())
    assert len(resp.series) == 2
    assert all(pt.city == "Paris" for pt in resp.series)
