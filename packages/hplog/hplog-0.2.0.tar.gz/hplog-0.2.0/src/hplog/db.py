from pymongo import MongoClient
from pydantic import BaseModel

class Collection:

    def __init__(self, model: BaseModel):
        self.model = model
        self.collection_name = model.__class__.__name__.lower() + "s"
        self.data = model.model_dump()
        
    def get_schema(self):
        return self.model.model_json_schema()

class MongoConnector:
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client.get_database()
        self.models = []
    def _init_db(self):
        self.db.create_collection("hplog_meta", check_exists=True)
        self.db.create_collection("hplog_data", check_exists=True)
        if self.db["hplog_meta"].count_documents({}) == 0:
            self.db["hplog_meta"].insert_one({"hplog_models": []}, )

    def add_model(self, model: BaseModel):
        self.models = self.db["hplog_meta"].find_one({})["hplog_models"]
        self.db["hplog_meta"].update_one({}, {"$addToSet": {"hplog_models": model.model_json_schema()}})
        self.db["hplog_data"].insert_one(model.model_dump())
        return model.model_dump()


