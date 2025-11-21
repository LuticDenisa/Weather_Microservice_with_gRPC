import time
import os
import sys
import importlib

os.environ["MONGO_URI"] = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017")
os.environ["DB_NAME"] = "weatherdb_test"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "server"))

import server.dao as dao_module
importlib.reload(dao_module)

from server.dao import WeatherDAO

def test_save_and_fetch_snapshot():
    dao = WeatherDAO()
    snap = {
        "city": "London",
        "temperature_c": 10.5,
        "description": "few clouds",
        "humidity": 60,
        "wind_speed": 3.2,
    }
    saved = dao.save_snapshot(snap)
    assert saved["city"] == "London"
    assert "timestamp_ms" in saved

    t = saved["timestamp_ms"]
    series = dao.fetch_series("London", t - 5_000, t + 5_000)
    assert len(series) >= 1
    assert any(p["timestamp_ms"] == t for p in series)
