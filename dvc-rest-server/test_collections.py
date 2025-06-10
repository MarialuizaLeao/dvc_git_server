from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from pymongo.server_api import ServerApi

async def test_collections():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    MONGO_DB_URL = os.getenv("MONGO_DB_URL")
    if not MONGO_DB_URL:
        print("Error: MONGO_DB_URL environment variable is not set")
        return
        
    print("Connecting to MongoDB...")
    
    try:
        # Create client
        client = AsyncIOMotorClient(
            MONGO_DB_URL,
            server_api=ServerApi('1'),
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        db = client["project_management"]
        
        # Test connection
        await client.admin.command('ismaster')
        print("Successfully connected to MongoDB")
        
        # Get user
        user_id = "67950ca4970bd115977979a0"  # Your current user ID
        user = await db.Users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            print("User not found!")
            return
            
        print("Current user projects:", user["projects"])
        
        # Get all existing projects for this user
        existing_projects = []
        async for project in db.Projects.find({"username": "maria"}):
            existing_projects.append(str(project["_id"]))
            
        print("Existing projects:", existing_projects)
        
        # Update user's projects array
        result = await db.Users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"projects": existing_projects}}
        )
        
        print("Update result:", result.modified_count, "document(s) modified")
        
        # Verify the update
        updated_user = await db.Users.find_one({"_id": ObjectId(user_id)})
        print("Updated user projects:", updated_user["projects"])
            
    except Exception as e:
        print("Error:", str(e))
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_collections()) 