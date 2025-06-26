# filepath: init_db.py

from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

__all__ = ['init_db', 'close_db', 'get_database', 'get_users_collection', 'get_projects_collection', 'get_pipeline_configs_collection', 'get_data_sources_collection', 'get_remote_storages_collection', 'get_code_files_collection', 'get_models_collection', 'get_pipeline_executions_collection']

# MongoDB connection string from environment variable
MONGODB_URL = os.getenv('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set. Please set it before running the application.")

# Global variables for database and collections
client = None
db = None
users_collection = None
projects_collection = None
pipeline_configs_collection = None
data_sources_collection = None
remote_storages_collection = None
code_files_collection = None
models_collection = None
pipeline_executions_collection = None

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

async def get_pipeline_configs_collection():
    """Get pipeline configurations collection"""
    await init_if_needed()
    global pipeline_configs_collection
    return pipeline_configs_collection

async def get_data_sources_collection():
    """Get data sources collection"""
    await init_if_needed()
    global data_sources_collection
    return data_sources_collection

async def get_remote_storages_collection():
    """Get remote storages collection"""
    await init_if_needed()
    global remote_storages_collection
    return remote_storages_collection

async def get_code_files_collection():
    """Get code files collection"""
    await init_if_needed()
    global code_files_collection
    return code_files_collection

async def get_models_collection():
    """Get models collection"""
    await init_if_needed()
    global models_collection
    return models_collection

async def get_pipeline_executions_collection():
    """Get pipeline executions collection"""
    await init_if_needed()
    global pipeline_executions_collection
    return pipeline_executions_collection

async def init_db():
    """Initialize database connection"""
    global client, db, users_collection, projects_collection, pipeline_configs_collection, data_sources_collection, remote_storages_collection, code_files_collection, models_collection, pipeline_executions_collection
    
    try:
        # Create a new client and connect to the server
        # Updated connection options to handle SSL/TLS issues
        client = AsyncIOMotorClient(
            MONGODB_URL,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000,  # Increased timeout
            connectTimeoutMS=30000,          # Increased connect timeout
            socketTimeoutMS=30000,           # Increased socket timeout
            tls=True,
            retryWrites=True,
            retryReads=True,
            # Additional SSL options to handle TLS issues
            tlsAllowInvalidCertificates=False,
            tlsAllowInvalidHostnames=False,
            # Connection pool settings
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000
        )
        
        # Send a ping to confirm a successful connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get database and collections
        db = client.get_database("dvc_server")
        users_collection = db.get_collection("users")
        projects_collection = db.get_collection("projects")
        pipeline_configs_collection = db.get_collection("pipeline_configs")
        data_sources_collection = db.get_collection("data_sources")
        remote_storages_collection = db.get_collection("remote_storages")
        code_files_collection = db.get_collection("code_files")
        models_collection = db.get_collection("models")
        pipeline_executions_collection = db.get_collection("pipeline_executions")
        print("Collections initialized successfully")
        
        # Initialize collections if they don't exist
        collections = await db.list_collection_names()
        if "users" not in collections:
            await db.create_collection("users")
        if "projects" not in collections:
            await db.create_collection("projects")
        if "pipeline_configs" not in collections:
            await db.create_collection("pipeline_configs")
        if "data_sources" not in collections:
            await db.create_collection("data_sources")
        if "remote_storages" not in collections:
            await db.create_collection("remote_storages")
        if "code_files" not in collections:
            await db.create_collection("code_files")
        if "models" not in collections:
            await db.create_collection("models")
        if "pipeline_executions" not in collections:
            await db.create_collection("pipeline_executions")
            
        print("Database and collections initialized successfully")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please check your MONGODB_URL environment variable and network connection.")
        print("For MongoDB Atlas, ensure your IP is whitelisted and credentials are correct.")
        
        # Try alternative connection method for development
        try:
            print("Attempting to connect to local MongoDB for development...")
            client = AsyncIOMotorClient(
                "mongodb://localhost:27017",
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            await client.admin.command('ping')
            print("Successfully connected to local MongoDB")
            
            # Get database and collections
            db = client.get_database("dvc_server")
            users_collection = db.get_collection("users")
            projects_collection = db.get_collection("projects")
            pipeline_configs_collection = db.get_collection("pipeline_configs")
            data_sources_collection = db.get_collection("data_sources")
            remote_storages_collection = db.get_collection("remote_storages")
            code_files_collection = db.get_collection("code_files")
            models_collection = db.get_collection("models")
            pipeline_executions_collection = db.get_collection("pipeline_executions")
            print("Local database and collections initialized successfully")
            
        except Exception as local_e:
            print(f"Failed to connect to local MongoDB as well: {local_e}")
            print("Please ensure MongoDB is running locally or fix your Atlas connection.")
            client = None
            db = None
            users_collection = None
            projects_collection = None
            pipeline_configs_collection = None
            data_sources_collection = None
            remote_storages_collection = None
            code_files_collection = None
            models_collection = None
            pipeline_executions_collection = None
            raise e

async def close_db():
    """Close database connection"""
    global client, db, users_collection, projects_collection, pipeline_configs_collection, data_sources_collection, remote_storages_collection, code_files_collection, models_collection, pipeline_executions_collection
    if client:
        client.close()
    client = None
    db = None
    users_collection = None
    projects_collection = None
    pipeline_configs_collection = None
    data_sources_collection = None
    remote_storages_collection = None
    code_files_collection = None
    models_collection = None
    pipeline_executions_collection = None