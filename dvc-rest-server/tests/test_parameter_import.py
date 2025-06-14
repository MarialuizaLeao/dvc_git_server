#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for parameter import functionality.
"""

import asyncio
import json
import yaml
import tempfile
import os
from datetime import datetime

# Test data
TEST_USER_ID = "6848b6c8408bff83c12646ec"
TEST_PROJECT_ID = "684da4d5845118aeefc05140"

# Sample parameter files
SAMPLE_YAML = """
data:
  train_size: 0.8
  random_state: 42
  shuffle: true

model:
  learning_rate: 0.001
  epochs: 100
  batch_size: 32
"""

SAMPLE_JSON = """
{
  "data": {
    "train_size": 0.8,
    "random_state": 42,
    "shuffle": true
  },
  "model": {
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32
  }
}
"""

SAMPLE_ENV = """
TRAIN_SIZE=0.8
RANDOM_STATE=42
SHUFFLE=true
LEARNING_RATE=0.001
EPOCHS=100
BATCH_SIZE=32
"""

async def test_parameter_import():
    """Test parameter import functionality."""
    print("🧪 Testing Parameter Import Functionality")
    print("=" * 50)
    
    # Import the necessary functions
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import import_parameters_from_upload, get_parameter_set
    
    try:
        # Test 1: Import YAML parameters
        print("\n📋 Test 1: Import YAML parameters")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            SAMPLE_YAML,
            "test_params.yaml",
            "yaml"
        )
        
        print(f"✅ YAML import successful")
        print(f"   Imported from: {result.get('imported_from')}")
        print(f"   Format: {result.get('import_format')}")
        print(f"   Validation: {result.get('validation', {}).get('valid', 'Unknown')}")
        
        # Test 2: Import JSON parameters
        print("\n📋 Test 2: Import JSON parameters")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            SAMPLE_JSON,
            "test_params.json",
            "json"
        )
        
        print(f"✅ JSON import successful")
        print(f"   Imported from: {result.get('imported_from')}")
        print(f"   Format: {result.get('import_format')}")
        print(f"   Validation: {result.get('validation', {}).get('valid', 'Unknown')}")
        
        # Test 3: Import ENV parameters
        print("\n📋 Test 3: Import ENV parameters")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            SAMPLE_ENV,
            "test_params.env",
            "env"
        )
        
        print(f"✅ ENV import successful")
        print(f"   Imported from: {result.get('imported_from')}")
        print(f"   Format: {result.get('import_format')}")
        print(f"   Validation: {result.get('validation', {}).get('valid', 'Unknown')}")
        
        # Test 4: Auto-detect format
        print("\n📋 Test 4: Auto-detect format")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            SAMPLE_YAML,
            "auto_detect.yml",
            None  # Auto-detect
        )
        
        print(f"✅ Auto-detect successful")
        print(f"   Detected format: {result.get('import_format')}")
        
        # Test 5: Get current parameters
        print("\n📋 Test 5: Get current parameters")
        print("-" * 30)
        
        current_params = await get_parameter_set(TEST_USER_ID, TEST_PROJECT_ID)
        
        if current_params.get("parameter_set"):
            param_set = current_params["parameter_set"]
            print(f"✅ Current parameter set: {param_set.get('name')}")
            print(f"   Groups: {len(param_set.get('groups', []))}")
            total_params = sum(len(group.get('parameters', [])) for group in param_set.get('groups', []))
            print(f"   Total parameters: {total_params}")
            print(f"   File path: {current_params.get('file_path')}")
        else:
            print("❌ No parameter set found")
        
        # Test 6: Verify params.yaml in project root
        print("\n📋 Test 6: Verify params.yaml in project root")
        print("-" * 40)
        
        project_path = os.path.join("/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo", TEST_USER_ID, TEST_PROJECT_ID)
        params_yaml_path = os.path.join(project_path, "params.yaml")
        
        if os.path.exists(params_yaml_path):
            print(f"✅ params.yaml found in project root: {params_yaml_path}")
            with open(params_yaml_path, 'r') as f:
                content = f.read()
            print(f"   File size: {len(content)} characters")
            print(f"   Content preview: {content[:100]}...")
        else:
            print(f"❌ params.yaml not found in project root: {params_yaml_path}")
        
        # Test 7: Check DVC tracking
        print("\n📋 Test 7: Check DVC tracking")
        print("-" * 30)
        
        from app.dvc_handler import is_dvc_initialized
        if await is_dvc_initialized(project_path):
            dvc_file_path = os.path.join(project_path, "params.yaml.dvc")
            if os.path.exists(dvc_file_path):
                print(f"✅ params.yaml is tracked by DVC: {dvc_file_path}")
                with open(dvc_file_path, 'r') as f:
                    dvc_content = f.read()
                print(f"   DVC file content: {dvc_content}")
            else:
                print("⚠️  DVC initialized but params.yaml.dvc not found")
        else:
            print("⚠️  DVC not initialized in project")
        
        print("\n🎉 All parameter import tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_file_upload_simulation():
    """Simulate file upload functionality."""
    print("\n🧪 Testing File Upload Simulation")
    print("=" * 50)
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import import_parameters_from_upload
    
    try:
        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(SAMPLE_YAML)
            yaml_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(SAMPLE_JSON)
            json_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(SAMPLE_ENV)
            env_file = f.name
        
        # Test file upload simulation
        print("\n📋 Test 1: YAML file upload simulation")
        print("-" * 40)
        
        with open(yaml_file, 'r') as f:
            content = f.read()
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            content,
            os.path.basename(yaml_file),
            "yaml"
        )
        
        print(f"✅ YAML file upload successful")
        print(f"   File: {result.get('imported_from')}")
        print(f"   Import file path: {result.get('import_file_path')}")
        
        # Clean up temporary files
        os.unlink(yaml_file)
        os.unlink(json_file)
        os.unlink(env_file)
        
        print("\n🎉 File upload simulation completed successfully!")
        
    except Exception as e:
        print(f"❌ File upload test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Parameter Import Tests")
    print(f"User ID: {TEST_USER_ID}")
    print(f"Project ID: {TEST_PROJECT_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    asyncio.run(test_parameter_import())
    asyncio.run(test_file_upload_simulation())
    
    print("\n✨ All tests completed!") 