#!/usr/bin/env python3
"""
Test script for the enhanced DVC pipeline calls functionality.
This script tests the new pipeline management endpoints and DVC operations.
"""

import requests
import json
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
        "description": "Test project for DVC pipeline calls",
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

def test_dvc_pipeline_calls():
    """Test the enhanced DVC pipeline calls functionality"""
    
    print("🚀 Testing Enhanced DVC Pipeline Calls")
    print("=" * 50)
    
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
    
    # Test 1: Create individual DVC stages
    print("\nTest 1: Creating individual DVC stages...")
    
    stages_to_create = [
        {
            "name": "data_preparation",
            "deps": ["data/raw"],
            "outs": ["data/processed"],
            "params": ["params.yaml"],
            "metrics": ["metrics/accuracy.json"],
            "command": "python scripts/prepare_data.py"
        },
        {
            "name": "model_training",
            "deps": ["data/processed", "src/model.py"],
            "outs": ["models/model.pkl"],
            "params": ["params.yaml"],
            "metrics": ["metrics/accuracy.json"],
            "command": "python scripts/train_model.py"
        }
    ]
    
    for stage in stages_to_create:
        try:
            response = requests.post(
                f"{BASE_URL}/{user_id}/{project_id}/stage",
                json=stage,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created stage: {stage['name']}")
                print(f"  Message: {result['message']}")
            else:
                print(f"❌ Failed to create stage {stage['name']}: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating stage {stage['name']}: {e}")
    
    # Test 2: Create pipeline template
    print("\nTest 2: Creating pipeline template...")
    
    template_request = {
        "template_name": "ml_pipeline_template",
        "stages": [
            {
                "name": "data_ingestion",
                "deps": ["data/raw"],
                "outs": ["data/ingested"],
                "command": "python scripts/ingest_data.py"
            },
            {
                "name": "feature_engineering",
                "deps": ["data/ingested"],
                "outs": ["data/features"],
                "params": ["params.yaml"],
                "command": "python scripts/engineer_features.py"
            },
            {
                "name": "model_evaluation",
                "deps": ["models/model.pkl", "data/test"],
                "outs": ["results/evaluation.json"],
                "metrics": ["metrics/final_accuracy.json"],
                "command": "python scripts/evaluate_model.py"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/template",
            json=template_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created pipeline template: {template_request['template_name']}")
            print(f"  Message: {result['message']}")
        else:
            print(f"❌ Failed to create pipeline template: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating pipeline template: {e}")
    
    # Test 3: Get pipeline stages
    print("\nTest 3: Getting pipeline stages...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/pipeline/stages")
        
        if response.status_code == 200:
            stages = response.json()
            print(f"✅ Retrieved pipeline stages")
            print(f"  Number of stages: {len(stages.get('stages', {}))}")
            for stage_name, stage_info in stages.get('stages', {}).items():
                print(f"    - {stage_name}: {stage_info.get('cmd', 'No command')}")
        else:
            print(f"❌ Failed to get pipeline stages: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting pipeline stages: {e}")
    
    # Test 4: Update a pipeline stage
    print("\nTest 4: Updating pipeline stage...")
    
    stage_update = {
        "updates": {
            "deps": ["data/raw", "config.yaml"],
            "metrics": ["metrics/accuracy.json", "metrics/precision.json"]
        }
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/stage/data_preparation",
            json=stage_update,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Updated stage: data_preparation")
            print(f"  Message: {result['message']}")
        else:
            print(f"❌ Failed to update stage: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error updating stage: {e}")
    
    # Test 5: Validate pipeline
    print("\nTest 5: Validating pipeline...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/pipeline/validate")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline validation result:")
            print(f"  Valid: {result['valid']}")
            print(f"  Message: {result['message']}")
            if result.get('details'):
                print(f"  Details: {result['details']}")
        else:
            print(f"❌ Failed to validate pipeline: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error validating pipeline: {e}")
    
    # Test 6: Run pipeline (dry run)
    print("\nTest 6: Running pipeline (dry run)...")
    
    run_request = {
        "pipeline": True,
        "force": False,
        "dry_run": True,
        "no_commit": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/pipeline/run",
            json=run_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pipeline run completed")
            print(f"  Message: {result['message']}")
            print(f"  Parameters: {result['parameters']}")
            if result.get('output'):
                print(f"  Output: {result['output'][:200]}...")
        else:
            print(f"❌ Failed to run pipeline: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
    
    # Test 7: Remove a pipeline stage
    print("\nTest 7: Removing pipeline stage...")
    
    try:
        response = requests.delete(f"{BASE_URL}/{user_id}/{project_id}/pipeline/stage/data_ingestion")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Removed stage: data_ingestion")
            print(f"  Message: {result['message']}")
        else:
            print(f"❌ Failed to remove stage: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error removing stage: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced DVC Pipeline Calls Testing Complete!")
    print(f"User ID: {user_id}")
    print(f"Project ID: {project_id}")

if __name__ == "__main__":
    test_dvc_pipeline_calls() 