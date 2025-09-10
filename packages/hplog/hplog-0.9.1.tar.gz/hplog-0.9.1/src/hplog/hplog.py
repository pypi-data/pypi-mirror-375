from __future__ import annotations
import motor.motor_asyncio
from pymongo.uri_parser import parse_uri
from pymongo.errors import OperationFailure, CollectionInvalid
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import uuid4

META_COLL = "hplog_meta"
DATA_COLL = "hplog_data"
META_DOC_ID = "meta"


class HPLog:
    def __init__(self, mongo_uri: str):
        self._mongo_uri = mongo_uri
        parsed = parse_uri(mongo_uri)
        db_name = parsed.get("database")
        if not db_name:
            raise ValueError("Mongo URI muss eine Datenbank enthalten (…/mydb).")
        self._db_name = db_name
        self.client = None
        self.db = None

    @classmethod
    async def connect(cls, mongo_uri: str) -> "HPLog":
        self = cls(mongo_uri)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self._mongo_uri)
        self.db = self.client[self._db_name]
        await self._startup_script()
        return self

    @asynccontextmanager
    async def session(self):
        async with await self.client.start_session() as s:
            yield s

    async def get_collections(self):
        return await self.db.list_collection_names()

    async def create_collection(self, name: str):
        try:
            await self.db.create_collection(name)
        except CollectionInvalid:
            # exists already
            pass
        except OperationFailure as e:
            # 48 = NamespaceExists (Server-Variante)
            if e.code != 48:
                raise

    async def _startup_script(self):
        await self.db.command("ping")
        await self.create_collection(META_COLL)
        await self.create_collection(DATA_COLL)
        # statt direkter Index-Erstellung:
        await self._ensure_indexes()
        await self.db[META_COLL].update_one(
            {"_id": META_DOC_ID},
            {"$setOnInsert": {"models": []}},
            upsert=True,
        )

    async def close(self):
        if self.client:
            self.client.close()

    async def log(self, pydantic_model: BaseModel):
        async with self.session() as s:
            await self.db[DATA_COLL].insert_one(
                {
                    "id": str(uuid4()),
                    "model": pydantic_model.__class__.__name__,
                    "data": pydantic_model.model_dump(mode="json"),
                    "timestamp": datetime.now(timezone.utc),
                },
                session=s,
            )

    async def _migrate_id_field(self):
        coll = self.db["hplog_data"]
        # fehlende id -> backfill (batchweise, um Ram zu sparen)
        cursor = coll.find(
            {"$or": [{"id": {"$exists": False}}, {"id": None}]}, projection=["_id"]
        )
        async for doc in cursor:
            await coll.update_one({"_id": doc["_id"]}, {"$set": {"id": str(uuid4())}})

    async def _ensure_indexes(self):
        coll = self.db["hplog_data"]
        # erst Daten migrieren, dann Index
        await self._migrate_id_field()
        await coll.create_index("timestamp")
        await coll.create_index("model")
        await coll.create_index("id", name="id_1", unique=True)
