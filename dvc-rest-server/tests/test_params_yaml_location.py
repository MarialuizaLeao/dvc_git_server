#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify params.yaml is created in project root.
"""

import asyncio
import os
import yaml
from datetime import datetime

# Test data
TEST_USER_ID = "6848b6c8408bff83c12646ec"
TEST_PROJECT_ID = "684da4d5845118aeefc05140"

# Sample parameter data
SAMPLE_PARAMETERS = {
    "data": {
        "train_size": 0.8,
        "random_state": 42,
        "shuffle": True
    },
    "model": {
        "learning_rate": 0.001,
        "epochs": 100,
        "batch_size": 32
    }
}

async def test_params_yaml_location():
    """Test that params.yaml is created in project root."""
    print("🧪 Testing params.yaml Location")
    print("=" * 40)
    
    # Import the necessary functions
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import create_parameter_set, get_parameter_set, delete_parameter_set
    
    try:
        # Test 1: Create parameter set
        print("\n📋 Test 1: Create parameter set")
        print("-" * 30)
        
        parameter_set = {
            "name": "Test Parameters",
            "description": "Test parameter set for location verification",
            "groups": [
                {
                    "name": "data",
                    "description": "Data processing parameters",
                    "parameters": [
                        {
                            "name": "train_size",
                            "value": 0.8,
                            "type": "number",
                            "description": "Training data size ratio"
                        },
                        {
                            "name": "random_state",
                            "value": 42,
                            "type": "number",
                            "description": "Random seed"
                        },
                        {
                            "name": "shuffle",
                            "value": True,
                            "type": "boolean",
                            "description": "Shuffle data"
                        }
                    ]
                },
                {
                    "name": "model",
                    "description": "Model parameters",
                    "parameters": [
                        {
                            "name": "learning_rate",
                            "value": 0.001,
                            "type": "number",
                            "description": "Learning rate"
                        },
                        {
                            "name": "epochs",
                            "value": 100,
                            "type": "number",
                            "description": "Number of epochs"
                        },
                        {
                            "name": "batch_size",
                            "value": 32,
                            "type": "number",
                            "description": "Batch size"
                        }
                    ]
                }
            ]
        }
        
        result = await create_parameter_set(TEST_USER_ID, TEST_PROJECT_ID, parameter_set)
        print(f"✅ Parameter set created successfully")
        print(f"   File path: {result.get('file_path')}")
        print(f"   DVC tracked: {result.get('dvc_tracked')}")
        
        # Test 2: Verify file location
        print("\n📋 Test 2: Verify file location")
        print("-" * 30)
        
        project_path = os.path.join("/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo", TEST_USER_ID, TEST_PROJECT_ID)
        params_yaml_path = os.path.join(project_path, "params.yaml")
        
        if os.path.exists(params_yaml_path):
            print(f"✅ params.yaml found in project root: {params_yaml_path}")
            
            # Read and verify content
            with open(params_yaml_path, 'r') as f:
                content = f.read()
            
            print(f"   File size: {len(content)} characters")
            
            # Parse YAML and verify structure
            yaml_data = yaml.safe_load(content)
            print(f"   YAML structure: {list(yaml_data.keys())}")
            
            # Verify specific values
            if 'data' in yaml_data and 'model' in yaml_data:
                print(f"   Data train_size: {yaml_data['data'].get('train_size')}")
                print(f"   Model learning_rate: {yaml_data['model'].get('learning_rate')}")
                print("✅ YAML content structure is correct")
            else:
                print("❌ YAML content structure is incorrect")
        else:
            print(f"❌ params.yaml not found in project root: {params_yaml_path}")
        
        # Test 3: Check DVC tracking
        print("\n📋 Test 3: Check DVC tracking")
        print("-" * 30)
        
        dvc_file_path = os.path.join(project_path, "params.yaml.dvc")
        if os.path.exists(dvc_file_path):
            print(f"✅ params.yaml.dvc found: {dvc_file_path}")
            with open(dvc_file_path, 'r') as f:
                dvc_content = f.read()
            print(f"   DVC file content: {dvc_content}")
        else:
            print(f"⚠️  params.yaml.dvc not found: {dvc_file_path}")
        
        # Test 4: Get parameter set
        print("\n📋 Test 4: Get parameter set")
        print("-" * 30)
        
        current_params = await get_parameter_set(TEST_USER_ID, TEST_PROJECT_ID)
        if current_params.get("parameter_set"):
            param_set = current_params["parameter_set"]
            print(f"✅ Parameter set retrieved successfully")
            print(f"   Name: {param_set.get('name')}")
            print(f"   Groups: {len(param_set.get('groups', []))}")
            print(f"   File path: {current_params.get('file_path')}")
        else:
            print("❌ Failed to retrieve parameter set")
        
        # Test 5: Clean up
        print("\n📋 Test 5: Clean up")
        print("-" * 30)
        
        delete_result = await delete_parameter_set(TEST_USER_ID, TEST_PROJECT_ID)
        print(f"✅ Parameter set deleted: {delete_result.get('message')}")
        
        # Verify file is removed
        if not os.path.exists(params_yaml_path):
            print(f"✅ params.yaml removed from project root")
        else:
            print(f"❌ params.yaml still exists in project root")
        
        print("\n🎉 All params.yaml location tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting params.yaml Location Tests")
    print(f"User ID: {TEST_USER_ID}")
    print(f"Project ID: {TEST_PROJECT_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    asyncio.run(test_params_yaml_location())
    
    print("\n✨ All tests completed!") 