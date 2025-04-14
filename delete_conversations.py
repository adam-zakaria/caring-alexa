import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variables
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Connect to MongoDB
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["alexa_az"]

# Delete the conversations collection
db.conversations.drop()

print("Conversations collection has been deleted successfully")