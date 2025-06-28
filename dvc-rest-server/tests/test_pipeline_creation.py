#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for DVC pipeline creation functionality.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from dvc_handler import (
    create_project,
    add_stage,
    get_pipeline_stages,
    validate_pipeline,
    add_code_file
)

async def test_pipeline_creation():
    """Test the pipeline creation functionality."""
    
    # Test parameters
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    print("🧪 Testing DVC Pipeline Creation")
    print("=" * 50)
    
    try:
        # Step 1: Create a test project
        print("1. Creating test project...")
        project_path = await create_project(user_id, project_id)
        print(f"   ✅ Project created at: {project_path}")
        
        # Step 2: Add a sample code file
        print("2. Adding sample code file...")
        await add_code_file(
            user_id=user_id,
            project_id=project_id,
            filename="train.py",
            file_path="src/train.py",
            content="""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load data
data = pd.read_csv('data/raw/data.csv')
X = data.drop('target', axis=1)
y = data['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'models/model.pkl')

# Save metrics
accuracy = model.score(X_test, y_test)
with open('metrics/accuracy.txt', 'w') as f:
    f.write(str(accuracy))
""",
            file_type="python",
            description="Training script for machine learning model"
        )
        print("   ✅ Code file added successfully")
        
        # Step 3: Add a sample data file
        print("3. Adding sample data file...")
        await add_code_file(
            user_id=user_id,
            project_id=project_id,
            filename="data.csv",
            file_path="data/raw/data.csv",
            content="""feature1,feature2,feature3,target
1.0,2.0,3.0,0
4.0,5.0,6.0,1
7.0,8.0,9.0,0
10.0,11.0,12.0,1
13.0,14.0,15.0,0
16.0,17.0,18.0,1
19.0,20.0,21.0,0
22.0,23.0,24.0,1
25.0,26.0,27.0,0
28.0,29.0,30.0,1""",
            file_type="data",
            description="Sample dataset for testing"
        )
        print("   ✅ Data file added successfully")
        
        # Step 4: Create a DVC stage
        print("4. Creating DVC stage...")
        stage_result = await add_stage(
            user_id=user_id,
            project_id=project_id,
            name="train",
            deps=["src/train.py", "data/raw/data.csv"],
            outs=["models/model.pkl", "metrics/accuracy.txt"],
            command="python src/train.py"
        )
        print(f"   ✅ Stage created: {stage_result}")
        
        # Step 5: Get pipeline stages
        print("5. Retrieving pipeline stages...")
        pipeline_stages = await get_pipeline_stages(user_id, project_id)
        print(f"   ✅ Pipeline stages: {pipeline_stages}")
        
        # Step 6: Validate pipeline
        print("6. Validating pipeline...")
        validation_result = await validate_pipeline(user_id, project_id)
        print(f"   ✅ Validation result: {validation_result}")
        
        print("\n🎉 All tests passed! Pipeline creation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_simple_stage():
    """Test creating a simple stage without dependencies."""
    
    user_id = "test_user_123"
    project_id = "test_project_456"
    
    print("\n🧪 Testing Simple Stage Creation")
    print("=" * 40)
    
    try:
        # Create a simple stage
        print("1. Creating simple stage...")
        stage_result = await add_stage(
            user_id=user_id,
            project_id=project_id,
            name="hello",
            command="echo 'Hello, DVC!' > hello.txt"
        )
        print(f"   ✅ Simple stage created: {stage_result}")
        
        # Get pipeline stages
        print("2. Retrieving updated pipeline...")
        pipeline_stages = await get_pipeline_stages(user_id, project_id)
        print(f"   ✅ Updated pipeline: {pipeline_stages}")
        
        print("\n🎉 Simple stage test passed!")
        
    except Exception as e:
        print(f"\n❌ Simple stage test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Main test function."""
    print("🚀 Starting DVC Pipeline Creation Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = await test_pipeline_creation()
    test2_passed = await test_simple_stage()
    
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