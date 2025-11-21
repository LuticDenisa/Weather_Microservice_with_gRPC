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
