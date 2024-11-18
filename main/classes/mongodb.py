from pymongo import MongoClient, InsertOne
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
import logging

from utils.constants import RESEARCH_PAPER_DATABASE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
ATLAS_URI = ("mongodb+srv://monaal:Abcd1234!@atlascluster.2fxmiy3.mongodb.net/?retryWrites=true&w=majority&appName"
             "=AtlasCluster")
client = MongoClient(ATLAS_URI, server_api=ServerApi('1'), uuidRepresentation="standard")
database = client['aristto']


def insert_data(data, database_name):
    collection = database[database_name]
    # Prepare bulk operations
    operations = [
        InsertOne(paper) for paper in data
    ] if database_name == RESEARCH_PAPER_DATABASE else [InsertOne(data)]

    # Perform bulk write operation
    try:
        result = collection.bulk_write(operations, ordered=False)
        inserted_count = result.inserted_count
        logger.info(f"Successfully inserted {inserted_count} new papers.")
    except BulkWriteError as bwe:
        inserted_count = bwe.details['nInserted']
        logger.info(f"Inserted {inserted_count} new papers. Some papers were already in the database.")
    except Exception as e:
        raise f"Could not insert data in mongodb, {e}"


def fetch_data(data, database_name):
    try:
        collection = database[database_name]
        results = list(collection.find(data))
        return results
    except Exception as e:
        raise Exception("Could not fetch data from MongoDB" + e)


def update_data(data, database_name, filter, operation):
    # Update multiple documents
    try:
        update_data = {
            operation: data
        }
        collection = database[database_name]
        collection.update_one(
            filter,
            update_data
        )
    except Exception as e:
        raise Exception("Could not update data in MongoDB :", e)
