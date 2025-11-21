import os
import sys
import time
import grpc

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))
sys.path.append(os.path.join(BASE_DIR, "server", "generated"))

from server.generated import weather_pb2, weather_pb2_grpc # type: ignore

GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost:50051")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret")

def _stub():
    channel = grpc.insecure_channel(GRPC_ADDR)
    return weather_pb2_grpc.WeatherServiceStub(channel)

# verifica apelul complet catre serverul grpc
def test_get_current_weather_ok():
    stub = _stub()
    resp = stub.GetCurrentWeather(
        weather_pb2.GetCurrentWeatherRequest(city="London"),
        metadata=(("x-api-key", SERVICE_API_KEY),),
        timeout=10.0
    )
    s = resp.snapshot
    assert s.city
    assert s.temperature_c or s.temperature_c == 0.0

# verifica intreg lantul grpc - mongo
def test_history_after_current_has_points():
    stub = _stub()
    now_resp = stub.GetCurrentWeather(
        weather_pb2.GetCurrentWeatherRequest(city="London"),
        metadata=(("x-api-key", SERVICE_API_KEY),),
        timeout=10.0
    )
    t = now_resp.snapshot.timestamp_ms
    resp = stub.GetWeatherHistory(
        weather_pb2.GetWeatherHistoryRequest(
            city="London",
            from_ms=t - 60_000,
            to_ms=t + 60_000,
        ),
        metadata=(("x-api-key", SERVICE_API_KEY),),
        timeout=10.0
    )
    assert len(resp.series) >= 1

