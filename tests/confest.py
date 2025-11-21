import os
import pytest
from pymongo import MongoClient

TEST_DB_NAME = "weatherdb_test"

@pytest.fixture(scope="session", autouse=True)
def _override_test_env():
    test_uri = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017")
    os.environ["MONGO_URI"] = test_uri 
    os.environ["DB_NAME"] = TEST_DB_NAME

    yield

    client = MongoClient(test_uri)
    client.drop_database(TEST_DB_NAME)
    client.close()
