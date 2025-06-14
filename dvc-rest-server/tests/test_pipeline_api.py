#!/usr/bin/env python3
"""
Test script for the new pipeline API endpoints.
This script tests the pipeline configuration and recovery functionality.
"""

import asyncio
import json
import requests
from datetime import datetime

# API base URL - adjust this to match your server configuration
BASE_URL = "http://localhost:8000"

def test_pipeline_api():
    """Test the pipeline API endpoints"""
    
    # Test data
    user_id = "507f1f77bcf86cd799439011"  # Example user ID
    project_id = "507f1f77bcf86cd799439012"  # Example project ID
    
    # Test 1: Create a pipeline configuration
    print("Test 1: Creating pipeline configuration...")
    
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
    
    # Test 4: Execute pipeline
    print(f"\nTest 4: Executing pipeline...")
    
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
    
    # Test 5: Recover pipeline
    print(f"\nTest 5: Recovering pipeline...")
    
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
    
    # Test 6: Update pipeline configuration
    print(f"\nTest 6: Updating pipeline configuration...")
    
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
    print("🚀 Testing Pipeline API Endpoints")
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
    print("🏁 Pipeline API testing completed!") 