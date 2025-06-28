#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to debug pipeline config creation issues.
"""

import asyncio
import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from classes import PipelineConfigCreate, PipelineStage

async def test_pipeline_config_creation():
    """Test creating a pipeline config to identify the issue."""
    
    print("🧪 Testing Pipeline Config Creation")
    print("=" * 50)
    
    try:
        # Create a test pipeline config
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
        
        print("✅ Pipeline config object created successfully")
        print(f"   Name: {pipeline_config.name}")
        print(f"   Description: {pipeline_config.description}")
        print(f"   Stages count: {len(pipeline_config.stages)}")
        
        # Test serialization
        config_dict = pipeline_config.dict()
        print("✅ Pipeline config serialized successfully")
        print(f"   Config dict keys: {list(config_dict.keys())}")
        
        # Test stage serialization
        for i, stage in enumerate(pipeline_config.stages):
            stage_dict = stage.dict()
            print(f"   Stage {i+1}: {stage_dict}")
        
        # Test JSON serialization
        config_json = pipeline_config.json()
        print("✅ Pipeline config JSON serialized successfully")
        print(f"   JSON length: {len(config_json)}")
        
        print("\n🎉 All pipeline config tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_stage_creation():
    """Test creating individual stages."""
    
    print("\n🧪 Testing Stage Creation")
    print("=" * 30)
    
    try:
        # Test creating a stage with all fields
        stage = PipelineStage(
            name="test_stage",
            deps=["input1.txt", "input2.txt"],
            outs=["output1.txt", "output2.txt"],
            params=["params.yaml"],
            metrics=["metrics.json"],
            plots=["plots.html"],
            command="python script.py",
            description="Test stage"
        )
        
        print("✅ Stage created successfully")
        stage_dict = stage.dict()
        print(f"   Stage dict: {stage_dict}")
        
        # Test creating a minimal stage
        minimal_stage = PipelineStage(
            name="minimal_stage",
            command="echo 'hello'"
        )
        
        print("✅ Minimal stage created successfully")
        minimal_dict = minimal_stage.dict()
        print(f"   Minimal stage dict: {minimal_dict}")
        
        print("\n🎉 All stage tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Stage test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Pipeline Config Debug Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = await test_stage_creation()
    test2_passed = await test_pipeline_config_creation()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 