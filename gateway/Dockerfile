FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# gateway are nevoie si de stubs ca sa importe weather_pb2*
COPY server /app/server
COPY gateway /app/gateway

ENV GRPC_ADDR="server:50051" \
    SERVICE_API_KEY="dev-secret"
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
