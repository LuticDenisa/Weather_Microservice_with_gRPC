import os

from dotenv import load_dotenv
load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY", "")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "")
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
