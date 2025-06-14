#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test script to debug pipeline config creation issues.
"""

import asyncio
import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from classes import PipelineConfigCreate, PipelineStage
from dvc_handler import create_project, create_pipeline_template
from init_db import get_projects_collection, get_pipeline_configs_collection

async def test_project_creation():
    """Test if project creation works."""
    
    print("🧪 Testing Project Creation")
    print("=" * 40)
    
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    try:
        # Check if project exists in database
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": project_id,
            "user_id": user_id
        })
        
        if not project:
            print("Project doesn't exist in database, creating...")
            project_path = await create_project(user_id, project_id)
            print(f"✅ Project created at: {project_path}")
        else:
            print("✅ Project already exists in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Project creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_template_creation():
    """Test pipeline template creation directly."""
    
    print("\n🧪 Testing Pipeline Template Creation")
    print("=" * 50)
    
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    try:
        # Create test stages
        stages_dict = [
            {
                "name": "data_prep",
                "deps": ["data/raw/data.csv"],
                "outs": ["data/processed/clean_data.csv"],
                "command": "python src/prepare_data.py"
            },
            {
                "name": "train",
                "deps": ["data/processed/clean_data.csv", "src/train.py"],
                "outs": ["models/model.pkl", "metrics/accuracy.txt"],
                "command": "python src/train.py"
            }
        ]
        
        print(f"Creating template with stages: {stages_dict}")
        
        # Create pipeline template
        result = await create_pipeline_template(user_id, project_id, "test_template", stages_dict)
        print(f"✅ Template creation result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_operations():
    """Test database operations for pipeline configs."""
    
    print("\n🧪 Testing Database Operations")
    print("=" * 40)
    
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    try:
        # Test pipeline configs collection
        pipeline_configs_collection = await get_pipeline_configs_collection()
        print("✅ Pipeline configs collection accessed successfully")
        
        # Test inserting a test config
        test_config = {
            "user_id": user_id,
            "project_id": project_id,
            "name": "test_config",
            "description": "Test config for debugging",
            "stages": [],
            "version": "1.0",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "is_active": True
        }
        
        result = await pipeline_configs_collection.insert_one(test_config)
        print(f"✅ Test config inserted with ID: {result.inserted_id}")
        
        # Clean up
        await pipeline_configs_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test config cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_pipeline_config_creation():
    """Test the full pipeline config creation process."""
    
    print("\n🧪 Testing Full Pipeline Config Creation")
    print("=" * 55)
    
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    try:
        # Create pipeline config object
        stages = [
            PipelineStage(
                name="data_prep",
                deps=["data/raw/data.csv"],
                outs=["data/processed/clean_data.csv"],
                command="python src/prepare_data.py"
            ),
            PipelineStage(
                name="train",
                deps=["data/processed/clean_data.csv", "src/train.py"],
                outs=["models/model.pkl", "metrics/accuracy.txt"],
                command="python src/train.py"
            )
        ]
        
        pipeline_config = PipelineConfigCreate(
            name="test_pipeline",
            description="Test pipeline for debugging",
            stages=stages
        )
        
        print("✅ Pipeline config object created")
        
        # Convert to dict format
        stages_dict = []
        for stage in pipeline_config.stages:
            stage_dict = {
                "name": stage.name,
                "deps": stage.deps,
                "outs": stage.outs,
                "params": stage.params,
                "metrics": stage.metrics,
                "plots": stage.plots,
                "command": stage.command
            }
            stages_dict.append(stage_dict)
        
        print(f"✅ Stages converted to dict: {stages_dict}")
        
        # Create template
        template_result = await create_pipeline_template(user_id, project_id, pipeline_config.name, stages_dict)
        print(f"✅ Template created: {template_result}")
        
        # Save to database
        pipeline_configs_collection = await get_pipeline_configs_collection()
        
        pipeline_config_data = {
            "user_id": user_id,
            "project_id": project_id,
            "name": pipeline_config.name,
            "description": pipeline_config.description,
            "stages": [stage.dict() for stage in pipeline_config.stages],
            "version": "1.0",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "is_active": True
        }
        
        db_result = await pipeline_configs_collection.insert_one(pipeline_config_data)
        print(f"✅ Config saved to database with ID: {db_result.inserted_id}")
        
        # Clean up
        await pipeline_configs_collection.delete_one({"_id": db_result.inserted_id})
        print("✅ Test config cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline config creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Comprehensive Pipeline Config Debug Tests")
    print("=" * 70)
    
    # Run tests in order
    tests = [
        ("Project Creation", test_project_creation),
        ("Database Operations", test_database_operations),
        ("Pipeline Template Creation", test_pipeline_template_creation),
        ("Full Pipeline Config Creation", test_full_pipeline_config_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = await test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Pipeline config creation should work.")
        return 0
    else:
        print("\n❌ Some tests failed! Check the errors above.")
        return 1

if __name__ == "__main__":
    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 