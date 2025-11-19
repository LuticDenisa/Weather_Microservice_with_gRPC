# implement the service defined in weather.proto + starts the server
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "generated"))

import grpc
from concurrent import futures

import requests

from .auth import ApiKeyInterceptor
from .owm_client import OpenWeatherMapClient
from .config import GRPC_PORT
from .dao import WeatherDAO

import weather_pb2_grpc, weather_pb2 # type: ignore

class WeatherService(weather_pb2_grpc.WeatherServiceServicer):

    def __init__(self):
        self.owm = OpenWeatherMapClient()
        self.dao = WeatherDAO()


    def GetCurrentWeather(self, request, context):
        city = (request.city or "").strip()
        if not city:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "City name is required.")
        
        try:
            raw = self.owm.get_current(city)
            data = self.owm.parse(raw)
            saved = self.dao.save_snapshot(data)
            return weather_pb2.GetCurrentWeatherResponse(
                snapshot=weather_pb2.WeatherSnapshot(
                    city=saved["city"],
                    temperature_c=saved["temperature_c"],
                    description=saved["description"],
                    humidity=saved["humidity"],
                    wind_speed=saved["wind_speed"],
                    timestamp_ms=saved["timestamp_ms"],
                )
            )
        except requests.HTTPError as http_err:
            code = http_err.response.status_code
            if code == 404:
                context.abort(grpc.StatusCode.NOT_FOUND, "City not found")
            elif code == 401:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Bad/empty OWM_API_KEY")
            else:
                context.abort(grpc.StatusCode.UNAVAILABLE, f"Upstream error {code}")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    
    def GetWeatherHistory(self, request, context):
        city = (request.city or "").strip()
        if not city:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "City name is required.")
        if request.from_ms <= 0 or request.to_ms <= 0 or request.from_ms >= request.to_ms:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid time range!")
        series = self.dao.fetch_series(city, request.from_ms, request.to_ms)
        return weather_pb2.GetWeatherHistoryResponse(
            series = [
                weather_pb2.WeatherSnapshot(
                    city=doc["city"],
                    temperature_c=doc["temperature_c"],
                    description=doc["description"],
                    humidity=doc["humidity"],
                    wind_speed=doc["wind_speed"],
                    timestamp_ms=doc["timestamp_ms"],
                )
                for doc in series
            ]
        )

    
def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ApiKeyInterceptor()]
    )
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    print(f"[gRPC] WeatherService listening on port {GRPC_PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()