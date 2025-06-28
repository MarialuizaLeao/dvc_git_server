from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
if not MONGO_DB_URL:
    print("Error: MONGO_DB_URL environment variable is not set")
    exit(1)

print("Attempting to connect with URL:", MONGO_DB_URL)

try:
    # Create a new client and connect to the server
    client = MongoClient(MONGO_DB_URL)
    
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # List databases
    print("Available databases:", client.list_database_names())
    
except Exception as e:
    print("Error:", e) 