from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime

async def test_project_creation():
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
        db = client["dvc_server"]
        
        # Test connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Get a user ID (using the first user from the previous test)
        user = await db.users.find_one({"username": "testuser"})
        if not user:
            print("No test user found!")
            return
            
        user_id = str(user["_id"])
        print(f"Using user ID: {user_id}")
        
        # Create a test project
        project_data = {
            "user_id": user_id,
            "username": "testuser",
            "project_name": "Test Project",
            "description": "A test project",
            "project_type": "test",
            "framework": "test",
            "python_version": "3.8",
            "dependencies": ["test"],
            "models_count": 0,
            "experiments_count": 0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Insert the project
        result = await db.projects.insert_one(project_data)
        project_id = str(result.inserted_id)
        print(f"Created project with ID: {project_id}")
        
        # Update user's projects array
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"projects": project_id}}
        )
        
        # Test get_user_projects
        print("\nTesting get_user_projects:")
        projects = await db.projects.find({"user_id": user_id}).to_list(None)
        print(f"Found {len(projects)} projects:")
        for project in projects:
            print(f"- {project['project_name']} (ID: {project['_id']})")
            
    except Exception as e:
        print("Error:", str(e))
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_project_creation()) 