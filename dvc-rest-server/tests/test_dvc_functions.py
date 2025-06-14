#!/usr/bin/env python3
"""
Test script for DVC pipeline functions.
This script tests the DVC functions directly without requiring MongoDB or the full server.
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from dvc_handler import (
    add_stage,
    add_stages,
    create_pipeline_template,
    get_pipeline_stages,
    update_pipeline_stage,
    remove_pipeline_stage,
    validate_pipeline,
    repro
)

async def setup_test_environment():
    """Set up a test environment with a temporary project"""
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    user_id = "test_user"
    project_id = "test_project"
    
    # Set up the project structure
    project_path = os.path.join(temp_dir, user_id, project_id)
    os.makedirs(project_path, exist_ok=True)
    
    # Create some test files
    os.makedirs(os.path.join(project_path, "data"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "models"), exist_ok=True)
    
    # Create test data files
    with open(os.path.join(project_path, "data/raw"), 'w') as f:
        f.write("test data")
    
    with open(os.path.join(project_path, "scripts/prepare_data.py"), 'w') as f:
        f.write("print('Preparing data...')\n")
    
    with open(os.path.join(project_path, "scripts/train_model.py"), 'w') as f:
        f.write("print('Training model...')\n")
    
    # Set the REPO_ROOT environment variable
    os.environ['REPO_ROOT'] = temp_dir
    
    return temp_dir, user_id, project_id

async def test_dvc_functions():
    """Test the DVC pipeline functions"""
    print("🚀 Testing DVC Pipeline Functions")
    print("=" * 50)
    
    # Set up test environment
    temp_dir, user_id, project_id = await setup_test_environment()
    
    try:
        print(f"📁 Test environment created at: {temp_dir}")
        
        # Test 1: Create individual stages
        print("\nTest 1: Creating individual DVC stages...")
        try:
            result = await add_stage(
                user_id=user_id,
                project_id=project_id,
                name="data_preparation",
                deps=["data/raw"],
                outs=["data/processed"],
                params=["params.yaml"],
                metrics=["metrics/accuracy.json"],
                command="python scripts/prepare_data.py"
            )
            print(f"✅ Created stage: {result}")
        except Exception as e:
            print(f"❌ Failed to create stage: {e}")
        
        # Test 2: Create multiple stages
        print("\nTest 2: Creating multiple DVC stages...")
        try:
            stages = [
                "dvc stage add -n train_model -d data/processed -o models/model.pkl python scripts/train_model.py"
            ]
            result = await add_stages(user_id, project_id, stages)
            print(f"✅ Created stages: {result}")
        except Exception as e:
            print(f"❌ Failed to create stages: {e}")
        
        # Test 3: Create pipeline template
        print("\nTest 3: Creating pipeline template...")
        try:
            stages_config = [
                {
                    "name": "data_ingestion",
                    "deps": ["data/raw"],
                    "outs": ["data/ingested"],
                    "command": "python scripts/prepare_data.py"
                },
                {
                    "name": "model_training",
                    "deps": ["data/ingested"],
                    "outs": ["models/model.pkl"],
                    "command": "python scripts/train_model.py"
                }
            ]
            
            result = await create_pipeline_template(
                user_id=user_id,
                project_id=project_id,
                template_name="test_pipeline",
                stages=stages_config
            )
            print(f"✅ Created pipeline template: {result}")
        except Exception as e:
            print(f"❌ Failed to create pipeline template: {e}")
        
        # Test 4: Get pipeline stages
        print("\nTest 4: Getting pipeline stages...")
        try:
            stages = await get_pipeline_stages(user_id, project_id)
            print(f"✅ Retrieved pipeline stages: {stages}")
        except Exception as e:
            print(f"❌ Failed to get pipeline stages: {e}")
        
        # Test 5: Update pipeline stage
        print("\nTest 5: Updating pipeline stage...")
        try:
            updates = {
                "deps": ["data/raw", "config.yaml"],
                "metrics": ["metrics/accuracy.json", "metrics/precision.json"]
            }
            result = await update_pipeline_stage(user_id, project_id, "data_preparation", updates)
            print(f"✅ Updated stage: {result}")
        except Exception as e:
            print(f"❌ Failed to update stage: {e}")
        
        # Test 6: Validate pipeline
        print("\nTest 6: Validating pipeline...")
        try:
            result = await validate_pipeline(user_id, project_id)
            print(f"✅ Pipeline validation: {result}")
        except Exception as e:
            print(f"❌ Failed to validate pipeline: {e}")
        
        # Test 7: Remove pipeline stage
        print("\nTest 7: Removing pipeline stage...")
        try:
            result = await remove_pipeline_stage(user_id, project_id, "data_ingestion")
            print(f"✅ Removed stage: {result}")
        except Exception as e:
            print(f"❌ Failed to remove stage: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 DVC Pipeline Functions Testing Complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        # Clean up
        print(f"\n🧹 Cleaning up test environment...")
        try:
            shutil.rmtree(temp_dir)
            print("✅ Test environment cleaned up")
        except Exception as e:
            print(f"⚠️  Failed to clean up: {e}")

def main():
    """Main function"""
    print("🔧 DVC Pipeline Functions Test")
    print("This script tests the DVC functions directly without requiring the full server.")
    print("Note: This test requires DVC to be installed and configured.")
    print()
    
    # Check if DVC is available
    try:
        import subprocess
        result = subprocess.run(['dvc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ DVC is available: {result.stdout.strip()}")
        else:
            print("❌ DVC is not available. Please install DVC first.")
            return
    except FileNotFoundError:
        print("❌ DVC is not installed. Please install DVC first.")
        print("   Install with: pip install dvc")
        return
    
    # Run the tests
    asyncio.run(test_dvc_functions())

if __name__ == "__main__":
    main() 