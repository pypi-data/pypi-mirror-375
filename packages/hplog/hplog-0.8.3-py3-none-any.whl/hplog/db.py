# hplog/db.py
from __future__ import annotations
from typing import Any, Mapping, Type
from datetime import datetime

from pymongo import MongoClient, ASCENDING
from pydantic import BaseModel
import pandas as pd
import dask.dataframe as dd
META_COLL = "hplog_meta"
DATA_COLL = "hplog_data"
META_DOC_ID = "meta"  # single meta-doc anchor


class Collection:
    """Wraps a Pydantic instance and exposes schema via its class."""

    def __init__(self, model_instance: BaseModel):
        self.model = model_instance
        self.model_cls: Type[BaseModel] = model_instance.__class__
        self.collection_name = f"{self.model_cls.__name__.lower()}s"
        self.data = model_instance.model_dump()

    def get_schema(self) -> dict:
        # Clearer to derive schema from the class
        return self.model_cls.model_json_schema()


class MongoConnector:
    def __init__(self, uri: str, db_name: str | None = None):
        self.client = MongoClient(uri)
        # If db_name is None, this uses the DB from the URI (e.g., .../example_db)
        self.db = self.client.get_database(db_name)
        self.models = []
        self._init_db()

    def _init_db(self):
        # Safely create collections if missing (create_collection raises if exists)
        existing = set(self.db.list_collection_names())
        if META_COLL not in existing:
            self.db.create_collection(META_COLL)
        if DATA_COLL not in existing:
            self.db.create_collection(DATA_COLL)
            # Optional: index for time-ordered reads
            self.db[DATA_COLL].create_index([("created_at", ASCENDING)])

        # Ensure a single meta doc exists
        self.db[META_COLL].update_one(
            {"_id": META_DOC_ID},
            {"$setOnInsert": {"hplog_models": []}},
            upsert=True,
        )

    def add_model(self, model: BaseModel):
        model_cls = model.__class__
        model_name = model_cls.__name__
        schema = model.model_json_schema()

        # Stelle sicher, dass das Meta-Dokument existiert (bereits in _init_db)
        # 1) Entferne vorhandenen Eintrag gleichen Namens
        self.db[META_COLL].update_one(
            {"_id": META_DOC_ID}, {"$pull": {"hplog_models": {"name": model_name}}}
        )
        # 2) Füge (de-duplicated) neu hinzu
        self.db[META_COLL].update_one(
            {"_id": META_DOC_ID},
            {"$addToSet": {"hplog_models": {"name": model_name, "schema": schema}}},
            upsert=True,
        )

        # Daten speichern (optional mit Metafeldern), Rückgabe bleibt plain dump:
        doc = {
            "_model": model_name,
            "created_at": datetime.now(),
            **model.model_dump(),
        }
        self.db[DATA_COLL].insert_one(doc)
        return model.model_dump()

    def log(self, entry: Any) -> dict:
        if hasattr(entry, "model_dump"):
            payload = entry.model_dump()
        elif hasattr(entry, "dict"):
            payload = entry.dict()
        elif isinstance(entry, Mapping):
            payload = dict(entry)
        else:
            raise TypeError("log(entry): entry must be a Pydantic model or a mapping")

        payload.setdefault("created_at", datetime.now())
        self.db["logs"].insert_one(payload)
        return payload
    

    def get_logs(self, filter: dict = None, to_pandas: bool = False, to_dask: bool = False):
        if to_dask and to_pandas:
            raise ValueError("to_dask and to_pandas cannot both be True")
        filter = filter or {}
        cursor = self.db["logs"].find(filter).sort("created_at", ASCENDING)
        logs = list(cursor)
        if to_pandas:
            df = pd.DataFrame(logs)
            return df
        if to_dask:
            return dd.from_pandas(pd.DataFrame(logs))
        return logs
    
