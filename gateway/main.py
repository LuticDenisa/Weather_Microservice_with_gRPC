import os, sys, time
import grpc
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))
sys.path.append(os.path.join(BASE_DIR, "server", "generated"))
import weather_pb2, weather_pb2_grpc # type: ignore

from dotenv import load_dotenv
load_dotenv()

SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "dev-secret")
GRPC_ADDR = os.getenv("GRPC_ADDR", "localhost:50051")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create a single grpc channel and stub for this process
    channel = grpc.insecure_channel(GRPC_ADDR)
    stub = weather_pb2_grpc.WeatherServiceStub(channel)

    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except Exception:
        print("(gateway) grpc channel not ready yet, will retry on first request")

    app.state.grpc_channel = channel
    app.state.grpc_stub = stub
    print("(gateway) grpc channel opened")

    try: 
        yield
    finally:
        try:
            app.state.grpc_channel.close()
            print("(gateway) grpc channel closed")
        except Exception:
            pass


app = FastAPI(title="Weather Gateway", lifespan=lifespan)

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
def current(request: Request, city: str):
    try:
        stub = request.app.state.grpc_stub
        resp = stub.GetCurrentWeather(
            weather_pb2.GetCurrentWeatherRequest(city=city),
            metadata=(("x-api-key", SERVICE_API_KEY),),
            timeout=5.0
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
        code = e.code().name
        detail = e.details()
        status = 502
        if code == "NOT_FOUND":
            status = 404
        elif code == "INVALID_ARGUMENT":
            status = 400
        elif code == "UNAUTHENTICATED":
            status = 401
        elif code == "PERMISSION_DENIED":
            status = 403
        elif code == "UNAVAILABLE":
            status = 503
        elif code == "DEADLINE_EXCEEDED":
            status = 504
        raise HTTPException(status_code=status, detail=f"{code}: {detail}")


@app.get("/api/weather/history", response_model=list[WeatherHistoryPoint])
def history(
    request: Request,
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
        stub = request.app.state.grpc_stub
        resp = stub.GetWeatherHistory(
            weather_pb2.GetWeatherHistoryRequest(city=city, from_ms=from_ms, to_ms=to_ms),
            metadata=(("x-api-key", SERVICE_API_KEY),),
            timeout=5.0
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
        code = e.code().name
        detail = e.details()
        status = 502
        if code == "NOT_FOUND":
            status = 404
        elif code == "INVALID_ARGUMENT":
            status = 400
        elif code == "UNAUTHENTICATED":
            status = 401
        elif code == "PERMISSION_DENIED":
            status = 403
        elif code == "UNAVAILABLE":
            status = 503
        elif code == "DEADLINE_EXCEEDED":
            status = 504
        raise HTTPException(status_code=status, detail=f"{code}: {detail}")