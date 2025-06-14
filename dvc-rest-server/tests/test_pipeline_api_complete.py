#!/usr/bin/env python3
"""
Complete test script for the pipeline API endpoints.
This script creates a user and project first, then tests the pipeline functionality.
"""

import requests
import json
from datetime import datetime

# API base URL - adjust this to match your server configuration
BASE_URL = "http://localhost:8000"

def create_test_user():
    """Create a test user"""
    user_data = {
        "username": "test_user_pipeline",
        "user_directory": "/tmp/test_user_pipeline"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Test user created successfully. ID: {user['_id']}")
            return user['_id']
        else:
            print(f"❌ Failed to create test user: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def create_test_project(user_id):
    """Create a test project"""
    project_data = {
        "username": "test_user_pipeline",
        "project_name": "test_pipeline_project",
        "description": "Test project for pipeline API",
        "project_type": "other",
        "framework": "scikit-learn",
        "python_version": "3.9",
        "dependencies": ["pandas", "scikit-learn", "numpy"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/project/create",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get("id")
            print(f"✅ Test project created successfully. ID: {project_id}")
            return project_id
        else:
            print(f"❌ Failed to create test project: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test project: {e}")
        return None

def test_pipeline_api():
    """Test the pipeline API endpoints"""
    
    print("Step 1: Creating test user...")
    user_id = create_test_user()
    if not user_id:
        print("❌ Cannot proceed without a test user")
        return
    
    print("\nStep 2: Creating test project...")
    project_id = create_test_project(user_id)
    if not project_id:
        print("❌ Cannot proceed without a test project")
        return
    
    # Test 1: Create a pipeline configuration
    print("\nTest 1: Creating pipeline configuration...")
    
    pipeline_config = {
        "name": "Test Pipeline",
        "description": "A test pipeline for data processing",
        "stages": [
            {
                "name": "data_preparation",
                "deps": ["data/raw"],
                "outs": ["data/processed"],
                "params": ["params.yaml"],
                "metrics": ["metrics/accuracy.json"],
                "command": "python scripts/prepare_data.py",
                "description": "Prepare and clean the data"
            },
            {
                "name": "model_training",
                "deps": ["data/processed", "src/model.py"],
                "outs": ["models/model.pkl"],
                "params": ["params.yaml"],
                "metrics": ["metrics/accuracy.json"],
                "command": "python scripts/train_model.py",
                "description": "Train the machine learning model"
            },
            {
                "name": "evaluation",
                "deps": ["models/model.pkl", "data/test"],
                "outs": ["results/evaluation.json"],
                "metrics": ["metrics/final_accuracy.json"],
                "command": "python scripts/evaluate_model.py",
                "description": "Evaluate the trained model"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/config",
            json=pipeline_config,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            config_id = result.get("id")
            print(f"✅ Pipeline configuration created successfully. ID: {config_id}")
        else:
            print(f"❌ Failed to create pipeline configuration: {response.status_code}")
            print(f"Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating pipeline configuration: {e}")
        return
    
    # Test 2: Get all pipeline configurations
    print("\nTest 2: Getting all pipeline configurations...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/pipeline/configs")
        
        if response.status_code == 200:
            result = response.json()
            configs = result.get("pipeline_configs", [])
            print(f"✅ Found {len(configs)} pipeline configurations")
            for config in configs:
                print(f"  - {config['name']}: {config['description']}")
        else:
            print(f"❌ Failed to get pipeline configurations: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting pipeline configurations: {e}")
    
    # Test 3: Get specific pipeline configuration
    print(f"\nTest 3: Getting specific pipeline configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/pipeline/config/{config_id}")
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Retrieved pipeline configuration: {config['name']}")
            print(f"  Description: {config['description']}")
            print(f"  Stages: {len(config['stages'])}")
            for stage in config['stages']:
                print(f"    - {stage['name']}: {stage['description']}")
        else:
            print(f"❌ Failed to get pipeline configuration: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting pipeline configuration: {e}")
    
    # Test 4: Execute pipeline (dry run)
    print(f"\nTest 4: Executing pipeline (dry run)...")
    
    execution_request = {
        "pipeline_config_id": config_id,
        "force": False,
        "dry_run": True,  # Use dry run for testing
        "targets": None
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/execute",
            json=execution_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline execution started")
            print(f"  Execution ID: {result['execution_id']}")
            print(f"  Status: {result['status']}")
        else:
            print(f"❌ Failed to execute pipeline: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error executing pipeline: {e}")
    
    # Test 5: Update pipeline configuration
    print(f"\nTest 5: Updating pipeline configuration...")
    
    update_request = {
        "name": "Updated Test Pipeline",
        "description": "An updated test pipeline for data processing",
        "is_active": True
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/config/{config_id}",
            json=update_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline configuration updated successfully")
        else:
            print(f"❌ Failed to update pipeline configuration: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error updating pipeline configuration: {e}")
    
    # Test 6: Recover pipeline
    print(f"\nTest 6: Recovering pipeline...")
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/{project_id}/pipeline/recover?config_id={config_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline recovered successfully")
            print(f"  Config name: {result['config_name']}")
            print(f"  Stages applied: {result['stages_applied']}")
        else:
            print(f"❌ Failed to recover pipeline: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error recovering pipeline: {e}")
    
    # Test 7: Delete pipeline configuration
    print(f"\nTest 7: Deleting pipeline configuration...")
    
    try:
        response = requests.delete(f"{BASE_URL}/{user_id}/{project_id}/pipeline/config/{config_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline configuration deleted successfully")
        else:
            print(f"❌ Failed to delete pipeline configuration: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error deleting pipeline configuration: {e}")

if __name__ == "__main__":
    print("🚀 Complete Pipeline API Testing")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running on http://localhost:8000")
        exit(1)
    
    # Run tests
    test_pipeline_api()
    
    print("\n" + "=" * 50)
    print("🏁 Complete Pipeline API testing completed!")
    print("\nNote: Test user and project were created for testing purposes.")
    print("You may want to clean them up manually if needed.") 