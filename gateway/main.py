import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import grpc
import sys
import time
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))
sys.path.append(os.path.join(BASE_DIR, "server", "generated"))
import weather_pb2, weather_pb2_grpc # type: ignore

from dotenv import load_dotenv
load_dotenv()

SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret")
GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost:50051")

app = FastAPI(title="Weather Gateway")

# cors pt vite dev server 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherCurrentResponse(BaseModel):
    city: str
    temperature_c: float
    description: str
    humidity: int
    wind_speed: float
    timestamp_ms: int

class WeatherHistoryPoint(BaseModel):
    city: str
    temperature_c: float
    description: str
    humidity: int
    wind_speed: float
    timestamp_ms: int

@app.get("/api/weather/current", response_model=WeatherCurrentResponse)
def current(city: str):
    try:
        with grpc.insecure_channel(GRPC_ADDR) as channel:
            stub = weather_pb2_grpc.WeatherServiceStub(channel)
            resp = stub.GetCurrentWeather(
                weather_pb2.GetCurrentWeatherRequest(city=city),
                metadata=(("x-api-key", SERVICE_API_KEY),),
            )
            s = resp.snapshot
            return {
                "city": s.city,
                "temperature_c": s.temperature_c,
                "description": s.description,
                "humidity": s.humidity,
                "wind_speed": s.wind_speed,
                "timestamp_ms": s.timestamp_ms,
            }
    except grpc.RpcError as e:
        raise HTTPException(status_code=502, detail=f"{e.code().name}: {e.details()}")

@app.get("/api/weather/history", response_model=list[WeatherHistoryPoint])
def history(
    city: str,
    from_ms: Optional[int] = Query(None, description="Start timestamp (ms). Defaults to now-24h"),
    to_ms: Optional[int]   = Query(None, description="End timestamp (ms). Defaults to now"),
):
    # calcuez ultimele 24h daca params lipsesc
    now = int(time.time() * 1000)
    if to_ms is None:
        to_ms = now
    if from_ms is None:
        from_ms = to_ms - 24 * 60 * 60 * 1000 

    if from_ms <= 0 or to_ms <= 0 or from_ms >= to_ms:
        raise HTTPException(status_code=400, detail="Invalid time range")

    try:
        with grpc.insecure_channel(GRPC_ADDR) as channel:
            stub = weather_pb2_grpc.WeatherServiceStub(channel)
            resp = stub.GetWeatherHistory(
                weather_pb2.GetWeatherHistoryRequest(city=city, from_ms=from_ms, to_ms=to_ms),
                metadata=(("x-api-key", SERVICE_API_KEY),),
            )
            return [
                {
                    "city": s.city,
                    "temperature_c": s.temperature_c,
                    "description": s.description,
                    "humidity": s.humidity,
                    "wind_speed": s.wind_speed,
                    "timestamp_ms": s.timestamp_ms,
                }
                for s in resp.series
            ]
    except grpc.RpcError as e:
        raise HTTPException(status_code=502, detail=f"{e.code().name}: {e.details()}")