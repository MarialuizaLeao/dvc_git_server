#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for data sources and remote storage functionality.
This script tests the data source and remote storage management endpoints.
"""

import requests
import json
import os
import tempfile
from datetime import datetime

# API base URL - adjust this to match your server configuration
BASE_URL = "http://localhost:8000"

def create_test_user():
    """Create a test user for testing"""
    user_data = {
        "username": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_directory": f"/test/user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Created test user: {user['username']}")
            return user['id']
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def create_test_project(user_id):
    """Create a test project for testing"""
    project_data = {
        "username": "test_user",
        "project_name": f"test_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "Test project for data sources and remote storage",
        "project_type": "other",
        "framework": "scikit-learn",
        "python_version": "3.9",
        "dependencies": ["pandas", "numpy", "scikit-learn"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/project/create", json=project_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created test project: {project_data['project_name']}")
            return result['id']
        else:
            print(f"❌ Failed to create project: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def test_data_sources_and_remotes():
    """Test the data sources and remote storage functionality"""
    
    print("🚀 Testing Data Sources and Remote Storage")
    print("=" * 60)
    
    # Step 1: Create test user and project
    print("\nStep 1: Creating test user and project...")
    user_id = create_test_user()
    if not user_id:
        print("❌ Cannot proceed without a test user")
        return
    
    project_id = create_test_project(user_id)
    if not project_id:
        print("❌ Cannot proceed without a test project")
        return
    
    # Test 1: Create remote storage
    print("\nTest 1: Creating remote storage...")
    
    remote_data = {
        "name": "test_remote",
        "url": "s3://test-bucket/dvc-storage",
        "type": "s3",
        "is_default": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/data/remote",
            json=remote_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created remote storage: {remote_data['name']}")
            print(f"  ID: {result['id']}")
            print(f"  DVC Result: {result.get('dvc_result', 'N/A')}")
            remote_id = result['id']
        else:
            print(f"❌ Failed to create remote storage: {response.status_code}")
            print(f"Error: {response.text}")
            remote_id = None
            
    except Exception as e:
        print(f"❌ Error creating remote storage: {e}")
        remote_id = None
    
    # Test 2: Get remote storages
    print("\nTest 2: Getting remote storages...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/data/remotes")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result.get('remote_storages', []))} remote storages")
            for remote in result.get('remote_storages', []):
                print(f"  - {remote['name']}: {remote['url']} ({remote['type']})")
        else:
            print(f"❌ Failed to get remote storages: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting remote storages: {e}")
    
    # Test 3: Create data source (URL)
    print("\nTest 3: Creating data source from URL...")
    
    data_source_url = {
        "name": "sample_dataset",
        "description": "Sample dataset from URL",
        "type": "url",
        "source": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv",
        "destination": "data/iris.csv"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/data/source",
            json=data_source_url,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created data source: {data_source_url['name']}")
            print(f"  ID: {result['id']}")
            print(f"  DVC Result: {result.get('dvc_result', 'N/A')}")
            source_id = result['id']
        else:
            print(f"❌ Failed to create data source: {response.status_code}")
            print(f"Error: {response.text}")
            source_id = None
            
    except Exception as e:
        print(f"❌ Error creating data source: {e}")
        source_id = None
    
    # Test 4: Create data source (local file)
    print("\nTest 4: Creating data source from local file...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("test data for local source\n")
        temp_file_path = f.name
    
    data_source_local = {
        "name": "local_test_data",
        "description": "Test data from local file",
        "type": "local",
        "source": temp_file_path,
        "destination": "data/local_test.txt"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/data/source",
            json=data_source_local,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created local data source: {data_source_local['name']}")
            print(f"  ID: {result['id']}")
            source_id_local = result['id']
        else:
            print(f"❌ Failed to create local data source: {response.status_code}")
            print(f"Error: {response.text}")
            source_id_local = None
            
    except Exception as e:
        print(f"❌ Error creating local data source: {e}")
        source_id_local = None
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass
    
    # Test 5: Get data sources
    print("\nTest 5: Getting data sources...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/data/sources")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result.get('data_sources', []))} data sources")
            for source in result.get('data_sources', []):
                print(f"  - {source['name']}: {source['type']} -> {source['destination']} ({source['status']})")
        else:
            print(f"❌ Failed to get data sources: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting data sources: {e}")
    
    # Test 6: Get specific data source
    if source_id:
        print(f"\nTest 6: Getting specific data source ({source_id})...")
        
        try:
            response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/data/source/{source_id}")
            
            if response.status_code == 200:
                source = response.json()
                print(f"✅ Retrieved data source: {source['name']}")
                print(f"  Type: {source['type']}")
                print(f"  Status: {source['status']}")
                print(f"  Destination: {source['destination']}")
            else:
                print(f"❌ Failed to get data source: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting data source: {e}")
    
    # Test 7: Update data source
    if source_id:
        print(f"\nTest 7: Updating data source ({source_id})...")
        
        update_data = {
            "name": "updated_sample_dataset",
            "description": "Updated description for the dataset"
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/{user_id}/{project_id}/data/source/{source_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Updated data source: {result['message']}")
            else:
                print(f"❌ Failed to update data source: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error updating data source: {e}")
    
    # Test 8: Push to remote (if remote exists)
    if remote_id:
        print(f"\nTest 8: Pushing to remote ({remote_id})...")
        
        push_data = {
            "target": "data/iris.csv"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/{user_id}/{project_id}/data/remote/{remote_id}/push",
                json=push_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Pushed to remote: {result['message']}")
            else:
                print(f"❌ Failed to push to remote: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error pushing to remote: {e}")
    
    # Test 9: List DVC remotes
    print("\nTest 9: Listing DVC remotes...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/data/remote/list")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved DVC remotes:")
            for name, remote_info in result.get('remotes', {}).items():
                print(f"  - {name}: {remote_info['url']} ({remote_info['type']})")
        else:
            print(f"❌ Failed to list DVC remotes: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing DVC remotes: {e}")
    
    # Test 10: Delete data source
    if source_id_local:
        print(f"\nTest 10: Deleting data source ({source_id_local})...")
        
        try:
            response = requests.delete(f"{BASE_URL}/{user_id}/{project_id}/data/source/{source_id_local}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Deleted data source: {result['message']}")
            else:
                print(f"❌ Failed to delete data source: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error deleting data source: {e}")
    
    # Test 11: Delete remote storage
    if remote_id:
        print(f"\nTest 11: Deleting remote storage ({remote_id})...")
        
        try:
            response = requests.delete(f"{BASE_URL}/{user_id}/{project_id}/data/remote/{remote_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Deleted remote storage: {result['message']}")
            else:
                print(f"❌ Failed to delete remote storage: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error deleting remote storage: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Data Sources and Remote Storage Testing Complete!")
    print(f"User ID: {user_id}")
    print(f"Project ID: {project_id}")

def main():
    """Main function"""
    print("🔧 Data Sources and Remote Storage Test")
    print("This script tests the data source and remote storage management functionality.")
    print("Note: This test requires the server to be running and DVC to be configured.")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/users/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running on http://localhost:8000")
        return
    
    # Run the tests
    test_data_sources_and_remotes()

if __name__ == "__main__":
    main() 