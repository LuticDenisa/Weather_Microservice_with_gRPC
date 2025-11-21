import requests
from server.owm_client import OpenWeatherMapClient

def test_parse_response(monkeypatch):
    fake_json = {
        "name": "London",
        "main": {"temp": 15, "humidity": 60},
        "weather": [{"description": "sunny"}],
        "wind": {"speed": 3.4},
    }
    def fake_get(url, params, timeout): return type("r", (), {"json": lambda self=fake_json: fake_json, "raise_for_status": lambda: None})()
    monkeypatch.setattr(requests, "get", fake_get)
    client = OpenWeatherMapClient()
    data = client.parse(fake_json)
    assert data["city"] == "London"
    assert data["temperature_c"] == 15
