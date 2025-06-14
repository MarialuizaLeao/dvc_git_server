#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for MongoDB connection configuration.
This script helps you set up and test your MongoDB connection.
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

def create_env_file():
    """Create a .env file with MongoDB configuration"""
    env_content = """# MongoDB Connection String
# Replace with your actual MongoDB Atlas connection string
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Alternative connection string format (if SSL issues persist)
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE

# Local MongoDB (for development)
# MONGODB_URL=mongodb://localhost:27017/dvc_server

# DVC Repository Root
REPO_ROOT=/path/to/your/dvc/repositories
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit the .env file with your actual MongoDB connection string")

async def test_mongodb_connection(connection_string):
    """Test MongoDB connection"""
    try:
        print(f"🔗 Testing connection to: {connection_string.split('@')[1] if '@' in connection_string else connection_string}")
        
        client = AsyncIOMotorClient(
            connection_string,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000
        )
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client.get_database("dvc_server")
        collections = await db.list_collection_names()
        print(f"✅ Database access successful! Collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def test_local_mongodb():
    """Test local MongoDB connection"""
    return await test_mongodb_connection("mongodb://localhost:27017")

def main():
    print("🚀 MongoDB Setup Script")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("📁 .env file not found. Creating one...")
        create_env_file()
        print("\n📋 Please edit the .env file with your MongoDB connection string and run this script again.")
        return
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    mongodb_url = os.getenv('MONGODB_URL')
    
    if not mongodb_url:
        print("❌ MONGODB_URL not found in .env file")
        print("📝 Please add your MongoDB connection string to the .env file")
        return
    
    print("🔧 Testing MongoDB connection...")
    
    # Test the configured connection
    success = asyncio.run(test_mongodb_connection(mongodb_url))
    
    if not success:
        print("\n🔄 Trying local MongoDB connection...")
        local_success = asyncio.run(test_local_mongodb())
        
        if local_success:
            print("\n💡 Local MongoDB is working. You can use it for development:")
            print("   MONGODB_URL=mongodb://localhost:27017/dvc_server")
        else:
            print("\n❌ Both connections failed. Please check:")
            print("   1. Your MongoDB Atlas connection string")
            print("   2. Network connectivity")
            print("   3. IP whitelist in MongoDB Atlas")
            print("   4. Username/password credentials")
            print("   5. Or install MongoDB locally for development")
    else:
        print("\n🎉 MongoDB connection is working correctly!")

if __name__ == "__main__":
    main() 