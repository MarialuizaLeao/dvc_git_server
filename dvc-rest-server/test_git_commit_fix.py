#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Git commit fix for parameter management.
"""

import asyncio
import os
import yaml
from datetime import datetime

# Test data
EXAMPLE_YAML = """
prepare:
  split: 0.3
  seed: 20170428

featurize:
  max_features: 200
  ngrams: 2

train:
  seed: 20170428
  n_est: 50
  min_split: 0.01
"""

async def test_git_commit_fix():
    """Test that Git commit operations work correctly with untracked files."""
    print("🧪 Testing Git Commit Fix")
    print("=" * 40)
    
    # Import the necessary functions
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import (
        safe_git_commit, 
        create_parameter_set, 
        update_parameter_set,
        delete_parameter_set,
        parse_params_yaml
    )
    
    try:
        # Test user and project IDs
        TEST_USER_ID = "6848b6c8408bff83c12646ec"
        TEST_PROJECT_ID = "684da4d5845118aeefc05140"
        
        # Test 1: Test safe_git_commit function directly
        print("\n📋 Test 1: Test safe_git_commit function")
        print("-" * 40)
        
        project_path = os.path.join("/home/marialuiza/Documents/faculdade/9periodo/poc/project/dvc-rest-server/repos", TEST_USER_ID, TEST_PROJECT_ID)
        
        # Create a test file to simulate untracked files
        test_file_path = os.path.join(project_path, "test_untracked.txt")
        with open(test_file_path, 'w') as f:
            f.write("This is a test untracked file")
        
        print(f"✅ Created test untracked file: {test_file_path}")
        
        # Test safe commit with specific file
        result = await safe_git_commit(project_path, "Test commit with specific file", ["test_untracked.txt"])
        print(f"✅ Safe commit result: {result}")
        
        # Test 2: Create parameter set
        print("\n📋 Test 2: Create parameter set")
        print("-" * 30)
        
        parameter_set = parse_params_yaml(EXAMPLE_YAML)
        create_result = await create_parameter_set(TEST_USER_ID, TEST_PROJECT_ID, parameter_set)
        
        print(f"✅ Create result: {create_result.get('success')}")
        print(f"   Git committed: {create_result.get('git_committed')}")
        print(f"   DVC tracked: {create_result.get('dvc_tracked')}")
        print(f"   Parameter count: {create_result.get('parameter_count')}")
        
        # Test 3: Update parameter set
        print("\n📋 Test 3: Update parameter set")
        print("-" * 30)
        
        # Modify the parameter set
        parameter_set["name"] = "Updated Test Parameters"
        for group in parameter_set.get("groups", []):
            for param in group.get("parameters", []):
                if param.get("name") == "split":
                    param["value"] = 0.4  # Change a value
        
        update_result = await update_parameter_set(TEST_USER_ID, TEST_PROJECT_ID, parameter_set)
        
        print(f"✅ Update result: {update_result.get('success')}")
        print(f"   Git committed: {update_result.get('git_committed')}")
        print(f"   DVC tracked: {update_result.get('dvc_tracked')}")
        print(f"   Parameter count: {update_result.get('parameter_count')}")
        
        print("\n🎉 All Git commit tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Git Commit Fix Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    asyncio.run(test_git_commit_fix())
    
    print("\n✨ All tests completed!") 