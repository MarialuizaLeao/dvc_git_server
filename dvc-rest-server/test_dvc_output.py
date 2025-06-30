#!/usr/bin/env python3
"""
Test script to see what DVC repro output actually looks like.
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
    repro,
    get_pipeline_stages
)

async def test_dvc_output():
    """Test to see what DVC repro output looks like"""
    print("🔍 Testing DVC Output Format")
    print("=" * 50)
    
    # Create temporary directories
    temp_dir = tempfile.mkdtemp()
    user_id = "test_user"
    project_id = "test_project"
    
    # Set up the project structure
    project_path = os.path.join(temp_dir, user_id, project_id)
    os.makedirs(project_path, exist_ok=True)
    
    # Set the REPO_ROOT environment variable
    os.environ['REPO_ROOT'] = temp_dir
    
    try:
        print(f"📁 Test environment created at: {temp_dir}")
        
        # Create a simple stage
        print("\n1. Creating a simple stage...")
        result = await add_stage(
            user_id=user_id,
            project_id=project_id,
            name="test_stage",
            command="echo 'Hello, DVC!' > output.txt"
        )
        print(f"✅ Created stage: {result}")
        
        # Get pipeline stages
        print("\n2. Getting pipeline stages...")
        stages = await get_pipeline_stages(user_id, project_id)
        print(f"✅ Pipeline stages: {stages}")
        
        # Run the stage
        print("\n3. Running the stage...")
        try:
            output = await repro(user_id, project_id, target="test_stage")
            print(f"✅ DVC repro output:")
            print("=" * 30)
            print(repr(output))
            print("=" * 30)
            print("Raw output:")
            print(output)
            print("=" * 30)
        except Exception as e:
            print(f"❌ DVC repro failed: {e}")
        
        # Run again to see "up to date" message
        print("\n4. Running the stage again (should be up to date)...")
        try:
            output = await repro(user_id, project_id, target="test_stage")
            print(f"✅ DVC repro output (second run):")
            print("=" * 30)
            print(repr(output))
            print("=" * 30)
            print("Raw output:")
            print(output)
            print("=" * 30)
        except Exception as e:
            print(f"❌ DVC repro failed: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up test directory: {temp_dir}")

if __name__ == "__main__":
    asyncio.run(test_dvc_output()) 