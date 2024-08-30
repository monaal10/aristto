from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.binary import Binary
from PIL import Image
import io

ATLAS_URI = ("mongodb+srv://monaal:Abcd1234!@atlascluster.2fxmiy3.mongodb.net/?retryWrites=true&w=majority&appName"
             "=AtlasCluster")


class MongoDB:

    def __init__(self):
        self.client = self.get_mongodb_client()
        self.database = self.client['aristto']
        self.collection = self.database['researchPapers']

    @staticmethod
    def get_mongodb_client():
        # Create a new client and connect to the server
        client = MongoClient(ATLAS_URI, server_api=ServerApi('1'))

        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            return client
        except Exception as e:
            print(e)
            raise Exception("Could not connect to mongoDB")


def insert_data(client, data):
    # Insert the data in mongoDB
    try:
        result = client.collection.insert_many(data)
        print(result.acknowledged)
    except Exception:
        raise Exception("Could not insert data in MongoDB")


def fetch_data(client, data):
    results = []
    try:
        for result in client.collection.find(data):
            results.append(result)
        return results
    except Exception:
        raise Exception("Could not fetch data from MongoDB")


def store_image(client, image_path, research_paper_id):
    # Open the image
    with Image.open(image_path) as img:
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_byte_arr = img_byte_arr.getvalue()

    # Create a document with the image data
    image_doc = {
        "research_paper_id": research_paper_id,
        "data": Binary(img_byte_arr)  # Convert to BSON Binary
    }

    # Insert the document into MongoDB
    result = client.collection.insert_one(image_doc)
    print(f"Image stored with ID: {result.inserted_id}")


def retrieve_image(client, research_paper_id):
    # Find the document in MongoDB
    image_doc = client.collection.find_one({"research_paper_id": research_paper_id})

    if image_doc:
        # Get the binary data
        image_data = image_doc["data"]

        # Convert binary data back to image
        image = Image.open(io.BytesIO(image_data))

        # Save or display the image
        image.save(f"retrieved_{research_paper_id}")
        print(f"Image retrieved and saved as 'retrieved_{research_paper_id}'")
    else:
        print("Image not found")
