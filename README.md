# 🌧️ Weather Microservice with gRPC

## Overview

A complete microservice-based system for retrieving and visualizing weather data using gRPC, FastAPI, MongoDB, and a React + Vite frontend.

The system allows users to request real-time weather information for a city, and visualize the temperature history over the last 24h via a web interface.

## Architecture
Browser (React UI)
| 
| (HTTP / REST)
|
Nginx <- proxy / api -> FastAPI Gateway
|
| (gRPC)
|
Python gRPC Server (WeatherService)
|
|
MongoDB

### Components

| Service| Technology | Description
|--------|------|---------|
|Server | Python, gRPC| Core microservice that fetches data from OpenWeatherMap, stores results in MongoDB and exposes a gRPC API |
| Gateway | FastAPI|  REST interface for the gRPC service. Handles HTTP requests and translates them into gRPC calls |
| MongoDB | Mongo| Stores weather snapshots (city, temperature, humidity, wind speed, timestamp) |
| UI | React (Vite) + Nginx| User interface for querying weather data and displaying history chart |
| Tests | Pytest| Comprehensive unit and integration tests for all the components |

## Features

- Fetch current weather via **OpenWeatherMap API**
- Store data in **MongoDB**
- Acces via - gRPC API (`WeatherService`) and REST API (`/api/weather/current`, `/api/weather/history`)
- View weather history and current conditions in the React UI
- Secured with an API key (`x-api-key` header)
- Fully containerized using **Docker Compose**

### Project Structure
Weather_Microservice_with_gRPC/
├── server/                 # gRPC service and business logic
│   ├── dao.py              # MongoDB persistence layer
│   ├── weather_server.py   # gRPC server implementation
│   ├── owm_client.py       # OpenWeatherMap client
│   ├── auth.py             # API key interceptor
│   └── generated/          # Auto-generated protobuf stubs
│
├── gateway/                # FastAPI REST-to-gRPC gateway
│   └── main.py
│
├── ui/                     # React + Vite frontend
│   ├── src/
│   └── nginx.conf          # Nginx config (proxy /api to gateway)
│
├── proto/                  # weather.proto definition
├── tests/                  # Unit & integration tests
├── docker-compose.yml      # Multi-service orchestration
├── .coveragerc             # Coverage configuration
└── README.md

### APIs

## gRPC (WeatherService)
| Method| Request | Response | Description
|--------|------|---------|---------|
| GetCurrentWeather | GetCurrentWeatherRequest(city) | GetCurrentWeatherResponse(snapshot) | Fetches current weather for a city. |
| GetWeatherHistory | GetWeatherHistoryRequest(city, from_ms, to_ms) | GetWeatherHistoryResponse(series) | Returns temperature history for the selected time range. |

## REST (via FastAPI Gateway)
| Endpoint| Method | Params | Description
|--------|------|---------|---------|
| /api/weather/current | GET | city | Returns current weather snapshot. |
| /api/weather/history | GET | city, from_ms, to_ms (optional) | Returns weather history for the last 24h by default. |
