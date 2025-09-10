import motor.motor_asyncio
from pymongo.uri_parser import parse_uri
from pymongo.errors import OperationFailure
from contextlib import asynccontextmanager


class HPLog:
    def __init__(self, mongo_uri: str):
        parsed = parse_uri(mongo_uri)
        db_name = parsed.get("database")
        if not db_name:
            raise ValueError("Mongo URI muss eine Datenbank enthalten (…/mydb).")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]

    @classmethod
    async def connect(cls, mongo_uri: str) -> "HPLog":
        self = cls(mongo_uri)
        await self._startup_script()
        return self

    @asynccontextmanager
    async def session(self):
        async with await self.client.start_session() as s:
            yield s

    async def get_collections(self, *, session=None):
        return await self.db.list_collection_names(session=session)

    async def create_collection(self, collection_name: str):
        """Idempotent & race-free: Code 48 (NamespaceExists) ignorieren."""
        try:
            await self.db.create_collection(collection_name)
        except OperationFailure as e:
            if e.code != 48:  # 48 = NamespaceExists
                raise

    async def _startup_script(self):
        # ping ohne Session ok
        await self.db.command("ping")
        # Sicherstellen, dass Basis-Collections existieren (idempotent)
        await self.create_collection("hplog_meta")
        await self.create_collection("hplog_data")
