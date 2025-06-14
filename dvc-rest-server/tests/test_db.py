from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

async def test_db_connection():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    MONGODB_URL = os.getenv("MONGODB_URL")
    if not MONGODB_URL:
        print("Error: MONGODB_URL environment variable is not set")
        return
        
    print("Connecting to MongoDB...")
    
    try:
        # Create client
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client["dvc_server"]  # Use the same database name as in init_db.py
        
        # Test connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # List all collections
        collections = await db.list_collection_names()
        print("Available collections:", collections)
        
        # Check users collection
        users_count = await db.users.count_documents({})
        print(f"Number of users: {users_count}")
        
        # Check projects collection
        projects_count = await db.projects.count_documents({})
        print(f"Number of projects: {projects_count}")
        
        # List all users
        print("\nUsers:")
        async for user in db.users.find():
            print(f"- {user['username']} (ID: {user['_id']})")
            
        # List all projects
        print("\nProjects:")
        async for project in db.projects.find():
            print(f"- {project['project_name']} (ID: {project['_id']})")
            
    except Exception as e:
        print("Error:", str(e))
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_db_connection()) 