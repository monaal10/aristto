from pymongo import MongoClient, InsertOne
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
ATLAS_URI = ("mongodb+srv://monaal:Abcd1234!@atlascluster.2fxmiy3.mongodb.net/?retryWrites=true&w=majority&appName"
             "=AtlasCluster")
client = MongoClient(ATLAS_URI, server_api=ServerApi('1'))
database = client['aristto']


def insert_data(data, database_name):
    collection = database[database_name]
    collection.create_index("id", unique=True)

    # Prepare bulk operations
    operations = [
        InsertOne(paper) for paper in data
    ]

    # Perform bulk write operation
    try:
        result = collection.bulk_write(operations, ordered=False)
        inserted_count = result.inserted_count
        logger.info(f"Successfully inserted {inserted_count} new papers.")
    except BulkWriteError as bwe:
        inserted_count = bwe.details['nInserted']
        logger.info(f"Inserted {inserted_count} new papers. Some papers were already in the database.")

    client.close()


def fetch_data(data, database_name):
    results = []
    try:
        collection = database[database_name]
        for result in collection.find(data):
            results.append(result)
        return results
    except Exception:
        raise Exception("Could not fetch data from MongoDB")
