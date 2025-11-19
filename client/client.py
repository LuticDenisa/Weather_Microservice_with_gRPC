# request the city, call the rpc, show the result
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))
sys.path.append(os.path.join(BASE_DIR, "server", "generated"))

import grpc
import weather_pb2, weather_pb2_grpc # type: ignore

API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret")
GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost:50051")

def main():
    with grpc.insecure_channel(GRPC_ADDR) as channel:
        stub = weather_pb2_grpc.WeatherServiceStub(channel)
        mode = input("Choose mode: [1] current  [2] history : ").strip() or "1"
        if mode == "1":
            city = input("Enter city name: ").strip()
            try:
                resp = stub.GetCurrentWeather(
                    weather_pb2.GetCurrentWeatherRequest(city=city),
                    metadata=(("x-api-key", API_KEY),),
                )
                s = resp.snapshot
                print(
                    f"\nWeather for {s.city}:\n"
                    f"Temperature: {s.temperature_c:.1f} Celcius\n"
                    f"Humidity: {s.humidity}%\n"
                    f"Conditions: {s.description}\n"
                    f"Wind Speed: {s.wind_speed} m/s\n"
                    f"Timestamp: {s.timestamp_ms}\n"
                )
            except grpc.RpcError as e:
                print(f"Error: {e.code().name} — {e.details()}")
        else:
            city = input("City: ").strip()
            import time
            now = int(time.time() * 1000)
            from_ms = now - 24*60*60*1000
            to_ms = now
            try:
                resp = stub.GetWeatherHistory(
                    weather_pb2.GetWeatherHistoryRequest(city=city, from_ms=from_ms, to_ms=to_ms),
                    metadata=(("x-api-key", API_KEY),),
                )
                print(f"\n{len(resp.series)} point(s) in last 24h for {city}:")
                for snap in resp.series:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(snap.timestamp_ms/1000.0)
                    print(f"- {dt}: {snap.temperature_c:.1f} °C ({snap.description})")
            except grpc.RpcError as e:
                print(f"Error: {e.code().name} — {e.details()}")
    

if __name__ == "__main__":
    main()

