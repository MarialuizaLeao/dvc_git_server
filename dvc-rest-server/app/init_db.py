# filepath: init_db.py

from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

__all__ = ['init_db', 'close_db', 'get_database', 'get_users_collection', 'get_projects_collection']

# MongoDB connection string from environment variable
MONGODB_URL = os.getenv('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set. Please set it before running the application.")

# Global variables for database and collections
client = None
db = None
users_collection = None
projects_collection = None

async def init_if_needed():
    """Initialize database if not already initialized"""
    global client
    if client is None:
        await init_db()

async def get_database():
    """Get database instance"""
    await init_if_needed()
    return db

async def get_users_collection():
    """Get users collection"""
    await init_if_needed()
    return users_collection

async def get_projects_collection():
    """Get projects collection"""
    await init_if_needed()
    global projects_collection
    return projects_collection

async def init_db():
    """Initialize database connection"""
    global client, db, users_collection, projects_collection
    
    try:
        # Create a new client and connect to the server
        client = AsyncIOMotorClient(
            MONGODB_URL,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=20000,  # Increased timeout
            connectTimeoutMS=20000,          # Added connect timeout
            socketTimeoutMS=20000,           # Added socket timeout
            tls=True,
            retryWrites=True
        )
        
        # Send a ping to confirm a successful connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get database and collections
        db = client.get_database("dvc_server")
        users_collection = db.get_collection("users")
        projects_collection = db.get_collection("projects")
        print("Collections initialized successfully")
        
        # Initialize collections if they don't exist
        collections = await db.list_collection_names()
        if "users" not in collections:
            await db.create_collection("users")
        if "projects" not in collections:
            await db.create_collection("projects")
            
        print("Database and collections initialized successfully")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        client = None
        db = None
        users_collection = None
        projects_collection = None
        raise e

async def close_db():
    """Close database connection"""
    global client, db, users_collection, projects_collection
    if client:
        client.close()
    client = None
    db = None
    users_collection = None
    projects_collection = None