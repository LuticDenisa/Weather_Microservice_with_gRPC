FROM python:3.11-slim

# set variabile de mediu pt python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# instaleaza dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy project files
COPY proto /app/proto
COPY server /app/server

# Port gRPC
ENV GRPC_PORT=50051
EXPOSE 50051

# variabile de mediu pt server
ENV OWM_API_KEY="" \
    SERVICE_API_KEY="dev-secret" \
    MONGO_URI="mongodb://mongo:27017"

CMD ["python", "-m", "server.weather_server"]
