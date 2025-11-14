# request the city, call the rpc, show the result
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))
sys.path.append(os.path.join(BASE_DIR, "server", "generated"))

import grpc
import weather_pb2, weather_pb2_grpc

API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret")
GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost:50051")

def main():
    with grpc.insecure_channel(GRPC_ADDR) as channel:
        stub = weather_pb2_grpc.WeatherServiceStub(channel)
        city = input("Enter city name: ").strip()
        try:
            resp = stub.GetCurrentWeather(
                weather_pb2.GetCurrentWeatherRequest(city=city),
                metadata=[("x-api-key", API_KEY)]
            )
            s = resp.snapshot
            print(
                f"\nWeather in {s.city}:\n"
                f"Temperature: {s.temperature_c:.1f} celcius\n"
                f"Humidity: {s.humidity}%\n"
                f"Conditions: {s.description}\n"
                f"Wind Speed: {s.wind_speed} m/s\n"
            )
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code().name} - {e.details()}")
    

if __name__ == "__main__":
    main()

