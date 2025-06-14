from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
import os
from dotenv import load_dotenv
import certifi

async def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    MONGO_DB_URL = os.getenv("MONGO_DB_URL")
    if not MONGO_DB_URL:
        print("Error: MONGO_DB_URL environment variable is not set")
        return
        
    print("Attempting to connect with URL:", MONGO_DB_URL)
    
    try:
        # Create client with more detailed settings
        client = AsyncIOMotorClient(
            MONGO_DB_URL,
            server_api=ServerApi('1'),
            tls=True,
            tlsCAFile=certifi.where(),
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
        
        # Test connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Try to list databases
        databases = await client.list_database_names()
        print("Available databases:", databases)
        
    except Exception as e:
        print("Connection failed with error:", str(e))
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection()) 