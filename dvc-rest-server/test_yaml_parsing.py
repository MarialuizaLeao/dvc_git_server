#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify YAML parsing with the correct structure.
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

async def test_yaml_parsing():
    """Test YAML parsing with the correct structure."""
    print("🧪 Testing YAML Parsing")
    print("=" * 40)
    
    # Import the necessary functions
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import parse_params_yaml, generate_params_yaml, convert_to_parameter_set
    
    try:
        # Test 1: Parse the example YAML
        print("\n📋 Test 1: Parse example YAML")
        print("-" * 30)
        
        parameter_set = parse_params_yaml(EXAMPLE_YAML)
        print(f"✅ YAML parsed successfully")
        print(f"   Name: {parameter_set.get('name')}")
        print(f"   Groups: {len(parameter_set.get('groups', []))}")
        
        # Display the parsed structure
        for group in parameter_set.get('groups', []):
            print(f"   Group: {group.get('name')} ({len(group.get('parameters', []))} parameters)")
            for param in group.get('parameters', []):
                print(f"     - {param.get('name')}: {param.get('value')} ({param.get('type')})")
        
        # Test 2: Generate YAML back from parsed structure
        print("\n📋 Test 2: Generate YAML from parsed structure")
        print("-" * 40)
        
        generated_yaml = generate_params_yaml(parameter_set)
        print(f"✅ YAML generated successfully")
        print(f"   Generated YAML:")
        print(generated_yaml)
        
        # Test 3: Parse the generated YAML to verify round-trip
        print("\n📋 Test 3: Round-trip verification")
        print("-" * 35)
        
        round_trip_set = parse_params_yaml(generated_yaml)
        print(f"✅ Round-trip parsing successful")
        print(f"   Groups: {len(round_trip_set.get('groups', []))}")
        
        # Test 4: Test with flat parameter structure
        print("\n📋 Test 4: Flat parameter structure")
        print("-" * 35)
        
        flat_yaml = """
learning_rate: 0.001
epochs: 100
batch_size: 32
dropout: 0.5
"""
        
        flat_set = parse_params_yaml(flat_yaml)
        print(f"✅ Flat YAML parsed successfully")
        print(f"   Groups: {len(flat_set.get('groups', []))}")
        
        if flat_set.get('groups'):
            default_group = flat_set['groups'][0]
            print(f"   Default group: {default_group.get('name')} ({len(default_group.get('parameters', []))} parameters)")
            for param in default_group.get('parameters', []):
                print(f"     - {param.get('name')}: {param.get('value')} ({param.get('type')})")
        
        # Test 5: Test convert_to_parameter_set function
        print("\n📋 Test 5: Convert to parameter set")
        print("-" * 35)
        
        # Parse YAML to dict first
        yaml_dict = yaml.safe_load(EXAMPLE_YAML)
        converted_set = convert_to_parameter_set(yaml_dict, "Converted Parameters")
        
        print(f"✅ Conversion successful")
        print(f"   Name: {converted_set.get('name')}")
        print(f"   Groups: {len(converted_set.get('groups', []))}")
        
        # Test 6: Verify parameter types
        print("\n📋 Test 6: Parameter type detection")
        print("-" * 35)
        
        from app.dvc_handler import get_value_type
        
        test_values = {
            "split": 0.3,
            "seed": 20170428,
            "max_features": 200,
            "ngrams": 2,
            "n_est": 50,
            "min_split": 0.01
        }
        
        for name, value in test_values.items():
            param_type = get_value_type(value)
            print(f"   {name}: {value} -> {param_type}")
        
        print("\n🎉 All YAML parsing tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_import_functionality():
    """Test the complete import functionality."""
    print("\n🧪 Testing Import Functionality")
    print("=" * 40)
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.dvc_handler import import_parameters_from_upload
    
    try:
        # Test user and project IDs
        TEST_USER_ID = "6848b6c8408bff83c12646ec"
        TEST_PROJECT_ID = "684da4d5845118aeefc05140"
        
        print("\n📋 Test 1: Import example YAML")
        print("-" * 30)
        
        result = await import_parameters_from_upload(
            TEST_USER_ID,
            TEST_PROJECT_ID,
            EXAMPLE_YAML,
            "example_params.yaml",
            "yaml"
        )
        
        print(f"✅ Import successful")
        print(f"   Imported from: {result.get('imported_from')}")
        print(f"   Format: {result.get('import_format')}")
        print(f"   DVC tracked: {result.get('dvc_tracked')}")
        print(f"   Params YAML path: {result.get('params_yaml_path')}")
        
        # Check if params.yaml was created correctly
        if result.get('params_yaml_path'):
            import os
            if os.path.exists(result['params_yaml_path']):
                with open(result['params_yaml_path'], 'r') as f:
                    content = f.read()
                print(f"   ✅ params.yaml created successfully")
                print(f"   Content preview:")
                print(content)
            else:
                print(f"   ❌ params.yaml not found at {result['params_yaml_path']}")
        
        print("\n🎉 Import functionality test completed successfully!")
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting YAML Parsing Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Run tests
    asyncio.run(test_yaml_parsing())
    asyncio.run(test_import_functionality())
    
    print("\n✨ All tests completed!") 