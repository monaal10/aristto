import pymongo
from pymongo import MongoClient, InsertOne, UpdateOne
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo.server_api import ServerApi
import logging

from main.utils.constants import RESEARCH_PAPER_DATABASE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
ATLAS_URI = ("mongodb+srv://monaal:Abcd1234!@atlascluster.2fxmiy3.mongodb.net/?retryWrites=true&w=majority&appName"
             "=AtlasCluster")
client = MongoClient(ATLAS_URI, server_api=ServerApi('1'), uuidRepresentation="standard")
database = client['aristto']

def encode_unicode(obj):
    try:
        if isinstance(obj, dict):
            return {k: encode_unicode(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [encode_unicode(item) for item in obj]
        elif isinstance(obj, str):
            return obj.encode('utf-8', errors='ignore').decode('utf-8')
        return obj
    except Exception as e:
        raise e


def insert_data(data, database_name):
    collection = database[database_name]
    try:
        if database_name != RESEARCH_PAPER_DATABASE:
            encoded_data = encode_unicode(data)
            collection.insert_one(encoded_data)
            return
        [collection.update_one({"id": doc["open_alex_id"]}, {"$set": doc}, upsert=True) for doc in data]
        logger.info(f"Successfully inserted {len(data)} new documents.")
    except DuplicateKeyError:
        logger.info(f"This entry was already in database")
    except Exception as e:
        raise e


def fetch_data(data, database_name):
    try:
        collection = database[database_name]
        results = list(collection.find(data))
        return results
    except Exception as e:
        raise Exception("Could not fetch data from MongoDB" + e)


def update_data(data, database_name, filter, operation):
    try:
        update_data = {
            operation: data
        }
        collection = database[database_name]
        collection.update_one(
            filter,
            update_data,
            upsert=True
        )
    except Exception as e:
        raise Exception("Could not update data in MongoDB :", e)

