# tests/test_startup.py
import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from hplog.hplog import HPLog

MONGO_URI = "mongodb://root:example@127.0.0.1:27017/example_db?authSource=admin"


@pytest.fixture
async def mongo_client():
    client = AsyncIOMotorClient(MONGO_URI)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def mongo_db(mongo_client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    return mongo_client["example_db"]


@pytest.fixture
async def hplog_instance():
    hp = await HPLog.connect(MONGO_URI)  # erstellt Client im aktuellen Loop
    try:
        yield hp
    finally:
        await hp.close()  # implementiere close(): self.client.close()


import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase


@pytest.mark.asyncio
async def test_connection(mongo_db: AsyncIOMotorDatabase):
    res = await mongo_db.command("ping")
    assert res.get("ok") == 1.0


@pytest.mark.asyncio
async def test_startup_script(hplog_instance: HPLog):
    cols = await hplog_instance.get_collections()
    assert "hplog_meta" in cols and "hplog_data" in cols


@pytest.mark.asyncio
async def test_log_pydantic(hplog_instance: HPLog, mongo_db: AsyncIOMotorDatabase):
    from pydantic import BaseModel

    class M(BaseModel):
        name: str
        value: int

    await hplog_instance.log(M(name="Test", value=42))
    doc = await mongo_db["hplog_data"].find_one({"data.name": "Test"})
    assert doc and doc["data"]["value"] == 42
