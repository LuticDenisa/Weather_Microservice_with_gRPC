# http client for OpenWeatherMap API + parsing response
import requests
from .config import OWM_API_KEY

class OpenWeatherMapClient:
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def get_current(self, city: str) -> dict:
        if not OWM_API_KEY:
            raise RuntimeError("OWM_API_KEY is not set in the environment variables.")
        params = {
            "q": city,
            "appid": OWM_API_KEY,
            "units": "metric"
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def parse(payload: dict) -> dict:
        return{
            "city": payload.get("name"),
            "temperature_c": float(payload["main"]["temp"]),
            "description": payload["weather"][0]["description"],
            "humidity": int(payload["main"]["humidity"]),
            "wind_speed": float(payload.get("wind", {}).get("speed", 0.0)),
        }
