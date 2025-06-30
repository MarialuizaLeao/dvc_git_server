#!/usr/bin/env python3
"""
Test script to check if the parsing function works with sample DVC output.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from routes import parse_execution_output_and_stats

async def test_parsing():
    """Test the parsing function with sample DVC output"""
    print("🔍 Testing Parsing Function")
    print("=" * 50)
    
    # Sample DVC output that should be parsed correctly
    sample_outputs = [
        # Case 1: Normal execution with stages running
        """Running stage 'data_preparation':
Executing command: python scripts/prepare_data.py
Running stage 'model_training':
Executing command: python scripts/train_model.py
Pipeline completed successfully.""",
        
        # Case 2: Some stages up to date
        """Stage 'data_preparation' is up to date
Running stage 'model_training':
Executing command: python scripts/train_model.py
Pipeline completed successfully.""",
        
        # Case 3: Pipeline up to date
        """Pipeline is up to date. Nothing to reproduce.""",
        
        # Case 4: Error case
        """Running stage 'data_preparation':
Executing command: python scripts/prepare_data.py
ERROR: Failed to execute stage 'model_training': Command failed""",
        
        # Case 5: Empty output
        "",
        
        # Case 6: Mixed case
        """Stage 'data_preparation' is up to date
Running stage 'model_training':
Executing command: python scripts/train_model.py
Running stage 'evaluation':
Executing command: python scripts/evaluate.py
Pipeline completed successfully."""
    ]
    
    for i, sample_output in enumerate(sample_outputs, 1):
        print(f"\n🧪 Test Case {i}:")
        print("-" * 30)
        print(f"Input: {repr(sample_output)}")
        
        try:
            # Mock the get_pipeline_stages function
            async def mock_get_pipeline_stages(user_id, project_id):
                return {
                    "stages": {
                        "data_preparation": {
                            "outs": ["data/processed"],
                            "cmd": "python scripts/prepare_data.py"
                        },
                        "model_training": {
                            "outs": ["models/model.pkl"],
                            "cmd": "python scripts/train_model.py"
                        },
                        "evaluation": {
                            "outs": ["metrics/accuracy.json"],
                            "cmd": "python scripts/evaluate.py"
                        }
                    }
                }
            
            # Replace the function temporarily
            import routes
            original_get_pipeline_stages = routes.get_pipeline_stages
            routes.get_pipeline_stages = mock_get_pipeline_stages
            
            try:
                result = await parse_execution_output_and_stats("test_user", "test_project", sample_output, {})
                
                print(f"✅ Parsing successful!")
                print(f"   Summary: {result['summary']}")
                print(f"   Pipeline stats: {result['pipeline_stats']}")
                print(f"   Structured logs count: {len(result['structured_logs'])}")
                
            finally:
                # Restore original function
                routes.get_pipeline_stages = original_get_pipeline_stages
                
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_parsing()) 