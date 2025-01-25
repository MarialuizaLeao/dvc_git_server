# filepath: init_db.py

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_DB_URL = "mongodb+srv://marialuiza1598:aKDCxmiX87rh6bWZ@poc.bq6sk.mongodb.net/?retryWrites=true&w=majority&appName=poc"
DB_NAME = "project_management"

# Create a new client and connect to the server
client = AsyncIOMotorClient(MONGO_DB_URL)
db = client[DB_NAME]
users_collection = db["Users"]
projects_collection = db["Projects"]

# # Example initialization (optional)
# users_collection.insert_one({
#     "username": "john_doe",
#     "projects": []
# })

# projects_collection.insert_one({
#     "user_id": "user_id_here",
#     "project_name": "Sample Project",
#     "metadata": {"description": "A test project"}
# })