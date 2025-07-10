from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()     # load the environment varibales 

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.github_events_db # My database name
events_collection = db.events # My collection name