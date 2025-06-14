#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify parameter validation fix.
"""

import asyncio
import yaml
from datetime import datetime

# Test data - using the example provided
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

async def test_validation_fix():
    """Test that parameter validation works correctly."""
    print("🧪 Testing Parameter Validation Fix")
    print("=" * 40)
    
    # Import the necessary functions
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import parse_params_yaml, validate_parameters, validate_single_parameter
    
    try:
        # Test 1: Parse and validate the example YAML
        print("\n📋 Test 1: Parse and validate example YAML")
        print("-" * 40)
        
        parameter_set = parse_params_yaml(EXAMPLE_YAML)
        print(f"✅ YAML parsed successfully")
        print(f"   Groups: {len(parameter_set.get('groups', []))}")
        
        # Validate the parameter set
        validation_result = await validate_parameters("test_user", "test_project", parameter_set)
        print(f"✅ Validation completed")
        print(f"   Valid: {validation_result.get('valid')}")
        print(f"   Validated parameters: {validation_result.get('validated_parameters')}")
        print(f"   Errors: {len(validation_result.get('errors', []))}")
        print(f"   Warnings: {len(validation_result.get('warnings', []))}")
        
        if validation_result.get('errors'):
            print("   Error details:")
            for error in validation_result['errors']:
                print(f"     - {error}")
        
        # Test 2: Test with None parameter
        print("\n📋 Test 2: Test with None parameter")
        print("-" * 35)
        
        none_validation = validate_single_parameter(None)
        print(f"✅ None parameter validation: {none_validation}")
        
        # Test 3: Test with invalid parameter structure
        print("\n📋 Test 3: Test with invalid parameter structure")
        print("-" * 45)
        
        invalid_param = {"name": "test", "value": None}  # Missing type
        invalid_validation = validate_single_parameter(invalid_param)
        print(f"✅ Invalid parameter validation: {invalid_validation}")
        
        # Test 4: Test with None parameter set
        print("\n📋 Test 4: Test with None parameter set")
        print("-" * 40)
        
        none_set_validation = await validate_parameters("test_user", "test_project", None)
        print(f"✅ None parameter set validation: {none_set_validation}")
        
        # Test 5: Test with empty parameter set
        print("\n📋 Test 5: Test with empty parameter set")
        print("-" * 40)
        
        empty_set = {"name": "Empty", "groups": []}
        empty_validation = await validate_parameters("test_user", "test_project", empty_set)
        print(f"✅ Empty parameter set validation: {empty_validation}")
        
        # Test 6: Test with None groups
        print("\n📋 Test 6: Test with None groups")
        print("-" * 35)
        
        none_groups_set = {"name": "None Groups", "groups": None}
        none_groups_validation = await validate_parameters("test_user", "test_project", none_groups_set)
        print(f"✅ None groups validation: {none_groups_validation}")
        
        # Test 7: Test with None parameters in group
        print("\n📋 Test 7: Test with None parameters in group")
        print("-" * 45)
        
        none_params_group = {
            "name": "None Params",
            "groups": [
                {
                    "name": "test_group",
                    "parameters": None
                }
            ]
        }
        none_params_validation = await validate_parameters("test_user", "test_project", none_params_group)
        print(f"✅ None parameters validation: {none_params_validation}")
        
        # Test 8: Test with mixed valid/invalid parameters
        print("\n📋 Test 8: Test with mixed valid/invalid parameters")
        print("-" * 50)
        
        mixed_set = {
            "name": "Mixed",
            "groups": [
                {
                    "name": "valid_group",
                    "parameters": [
                        {
                            "name": "valid_param",
                            "value": 42,
                            "type": "number"
                        },
                        None,  # Invalid parameter
                        {
                            "name": "another_valid",
                            "value": "test",
                            "type": "string"
                        }
                    ]
                }
            ]
        }
        mixed_validation = await validate_parameters("test_user", "test_project", mixed_set)
        print(f"✅ Mixed parameters validation: {mixed_validation}")
        
        print("\n🎉 All validation tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_import_with_validation():
    """Test the complete import process with validation."""
    print("\n🧪 Testing Import with Validation")
    print("=" * 40)
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import import_parameters_from_upload
    
    try:
        # Test user and project IDs
        TEST_USER_ID = "6848b6c8408bff83c12646ec"
        TEST_PROJECT_ID = "684da4d5845118aeefc05140"
        
        print("\n📋 Test 1: Import with validation")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            EXAMPLE_YAML,
            "test_params.yaml",
            "yaml"
        )
        
        print(f"✅ Import completed")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Imported from: {result.get('imported_from')}")
        print(f"   Format: {result.get('import_format')}")
        
        # Check validation results
        validation = result.get('validation', {})
        print(f"   Validation valid: {validation.get('valid', False)}")
        print(f"   Validated parameters: {validation.get('validated_parameters', 0)}")
        print(f"   Validation errors: {len(validation.get('errors', []))}")
        
        if validation.get('errors'):
            print("   Validation error details:")
            for error in validation['errors']:
                print(f"     - {error}")
        
        print("\n🎉 Import with validation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Parameter Validation Fix Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    asyncio.run(test_validation_fix())
    asyncio.run(test_import_with_validation())
    
    print("\n✨ All tests completed!") 