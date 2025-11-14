# implement the service defined in weather.proto + starts the server
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "generated"))

import grpc
from concurrent import futures

import requests

from .auth import ApiKeyInterceptor
from .owm_client import OpenWeatherMapClient
from .config import GRPC_PORT

import weather_pb2_grpc, weather_pb2

class WeatherService(weather_pb2_grpc.WeatherServiceServicer):

    def __init__(self):
        self.owm = OpenWeatherMapClient()


    def GetCurrentWeather(self, request, context):
        city = (request.city or "").strip()
        if not city:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "City name is required.")
        
        try:
            raw = self.owm.get_current(city)
            data = self.owm.parse(raw)
            return weather_pb2.GetCurrentWeatherResponse(
                snapshot=weather_pb2.WeatherSnapshot(
                    city=data["city"],
                    temperature_c=data["temperature_c"],
                    description=data["description"],
                    humidity=data["humidity"],
                    wind_speed=data["wind_speed"],
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