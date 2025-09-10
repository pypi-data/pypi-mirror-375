import pytest
import motor.motor_asyncio
from hplog.hplog import HPLog


username = "root"
password = "example"
mongo_uri = (
    f"mongodb://{username}:{password}@127.0.0.1:27017/example_db?authSource=admin"
)

hplog = HPLog(mongo_uri)
db = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
client = db["example_db"]


@pytest.mark.asyncio
async def test_connection():
    assert client is not None, "Client is None"
    assert isinstance(client, motor.motor_asyncio.AsyncIOMotorDatabase), "Connection to MongoDB failed"

    result = await client.command("ping")
    assert result.get("ok") == 1.0, "Ping to MongoDB failed"

@pytest.mark.asyncio
async def test_startup_script():
    collections = await hplog.get_collections()
    assert "hplog_meta" in collections, "'hplog_meta' collection does not exist after startup"
    assert "hplog_data" in collections, "'hplog_data' collection does not exist after startup"