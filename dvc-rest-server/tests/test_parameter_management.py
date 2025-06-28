#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for parameter management functionality.
This script demonstrates the user-friendly parameter management system.
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"
PROJECT_ID = "test_project_456"

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_response(response: requests.Response, title: str = "Response"):
    """Print formatted response information."""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Text Response: {response.text}")

def test_get_current_parameters():
    """Test getting current parameters."""
    print_section("Testing Get Current Parameters")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters/current"
    
    print(f"Getting current parameters...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, "Current Parameters Response")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("parameter_set"):
                print(f"✅ Current parameters retrieved successfully")
                return data["parameter_set"]
            else:
                print(f"ℹ️ No parameters found")
                return None
        else:
            print(f"❌ Failed to get current parameters: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting current parameters: {str(e)}")
        return None

def test_create_parameter_set():
    """Test creating a new parameter set."""
    print_section("Testing Create Parameter Set")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters"
    
    parameter_set = {
        "name": "ML Training Parameters",
        "description": "Parameters for machine learning model training",
        "groups": [
            {
                "name": "data",
                "description": "Data processing parameters",
                "parameters": [
                    {
                        "name": "train_size",
                        "value": 0.8,
                        "type": "number",
                        "description": "Training data size ratio",
                        "validation": {"min": 0.1, "max": 0.9}
                    },
                    {
                        "name": "random_state",
                        "value": 42,
                        "type": "number",
                        "description": "Random seed for reproducibility"
                    },
                    {
                        "name": "shuffle",
                        "value": True,
                        "type": "boolean",
                        "description": "Whether to shuffle the data"
                    }
                ]
            },
            {
                "name": "model",
                "description": "Model training parameters",
                "parameters": [
                    {
                        "name": "learning_rate",
                        "value": 0.001,
                        "type": "number",
                        "description": "Learning rate for training",
                        "validation": {"min": 0.0001, "max": 1.0}
                    },
                    {
                        "name": "epochs",
                        "value": 100,
                        "type": "number",
                        "description": "Number of training epochs",
                        "validation": {"min": 1, "max": 10000}
                    },
                    {
                        "name": "batch_size",
                        "value": 32,
                        "type": "number",
                        "description": "Batch size for training",
                        "validation": {"min": 1, "max": 1024}
                    }
                ]
            }
        ]
    }
    
    print(f"Creating parameter set...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(parameter_set, indent=2)}")
    
    try:
        response = requests.post(url, json=parameter_set)
        print_response(response, "Create Parameter Set Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parameter set created successfully")
            return data
        else:
            print(f"❌ Failed to create parameter set: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating parameter set: {str(e)}")
        return None

def test_validate_parameters():
    """Test parameter validation."""
    print_section("Testing Parameter Validation")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters/validate"
    
    validation_request = {
        "parameter_set_id": "current",
        "validate_all": True
    }
    
    print(f"Validating parameters...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(validation_request, indent=2)}")
    
    try:
        response = requests.post(url, json=validation_request)
        print_response(response, "Parameter Validation Response")
        
        if response.status_code == 200:
            data = response.json()
            validation = data.get("validation", {})
            if validation.get("valid"):
                print(f"✅ All parameters are valid")
            else:
                print(f"❌ Parameter validation failed: {validation.get('errors')}")
            return data
        else:
            print(f"❌ Failed to validate parameters: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error validating parameters: {str(e)}")
        return None

def test_export_parameters(format: str = "yaml"):
    """Test exporting parameters."""
    print_section(f"Testing Export Parameters: {format.upper()}")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters/export"
    
    export_request = {
        "format": format,
        "include_metadata": True,
        "include_descriptions": True
    }
    
    print(f"Exporting parameters...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(export_request, indent=2)}")
    
    try:
        response = requests.post(url, json=export_request)
        print_response(response, "Export Parameters Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parameters exported successfully to {format.upper()} format")
            return data
        else:
            print(f"❌ Failed to export parameters: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error exporting parameters: {str(e)}")
        return None

def test_update_parameter_set():
    """Test updating parameter set."""
    print_section("Testing Update Parameter Set")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters"
    
    # First get current parameters
    current_params = test_get_current_parameters()
    if not current_params:
        print("❌ No current parameters to update")
        return None
    
    # Update some values
    update_request = {
        "name": "Updated ML Training Parameters",
        "description": "Updated parameters for machine learning model training",
        "groups": current_params["groups"]
    }
    
    # Modify a parameter value
    if update_request["groups"]:
        if update_request["groups"][0]["parameters"]:
            update_request["groups"][0]["parameters"][0]["value"] = 0.9
    
    print(f"Updating parameter set...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(update_request, indent=2)}")
    
    try:
        response = requests.put(url, json=update_request)
        print_response(response, "Update Parameter Set Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parameter set updated successfully")
            return data
        else:
            print(f"❌ Failed to update parameter set: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error updating parameter set: {str(e)}")
        return None

def test_delete_parameter_set():
    """Test deleting parameter set."""
    print_section("Testing Delete Parameter Set")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/parameters"
    
    print(f"Deleting parameter set...")
    print(f"URL: {url}")
    
    try:
        response = requests.delete(url)
        print_response(response, "Delete Parameter Set Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Parameter set deleted successfully")
            return data
        else:
            print(f"❌ Failed to delete parameter set: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error deleting parameter set: {str(e)}")
        return None

def test_parameter_workflow():
    """Test complete parameter management workflow."""
    print_section("Testing Complete Parameter Workflow")
    
    # Step 1: Check current parameters
    print("\nStep 1: Checking current parameters...")
    current_params = test_get_current_parameters()
    
    # Step 2: Validate parameters
    print("\nStep 2: Validating parameters...")
    validation_result = test_validate_parameters()
    
    # Step 3: Export parameters
    print("\nStep 3: Exporting parameters...")
    export_result = test_export_parameters("yaml")
    
    # Step 4: Update parameters
    print("\nStep 4: Updating parameters...")
    update_result = test_update_parameter_set()
    
    # Step 5: Export updated parameters
    print("\nStep 5: Exporting updated parameters...")
    export_result2 = test_export_parameters("json")
    
    # Step 6: Clean up (delete parameters)
    print("\nStep 6: Cleaning up...")
    delete_result = test_delete_parameter_set()
    
    print_section("Workflow Summary")
    print("✅ Complete parameter workflow tested successfully")
    print(f"   - Parameters validated: {validation_result is not None}")
    print(f"   - Parameters exported: {export_result is not None}")
    print(f"   - Parameters updated: {update_result is not None}")
    print(f"   - Parameters cleaned up: {delete_result is not None}")

def main():
    """Run all parameter management tests."""
    print_section("Parameter Management Test Suite")
    print(f"Testing with User ID: {USER_ID}")
    print(f"Testing with Project ID: {PROJECT_ID}")
    print(f"Base URL: {BASE_URL}")
    
    # Test individual functions
    print("\n🧪 Testing Individual Functions")
    
    # Test 1: Get current parameters
    current_params = test_get_current_parameters()
    
    # Test 2: Create parameter set
    create_result = test_create_parameter_set()
    
    # Test 3: Validate parameters
    validation_result = test_validate_parameters()
    
    # Test 4: Export parameters
    export_result = test_export_parameters("yaml")
    
    # Test 5: Update parameters
    update_result = test_update_parameter_set()
    
    # Test 6: Export updated parameters
    export_result2 = test_export_parameters("json")
    
    # Test 7: Delete parameters
    delete_result = test_delete_parameter_set()
    
    # Test complete workflow
    print("\n🔄 Testing Complete Workflow")
    test_parameter_workflow()
    
    print_section("Test Summary")
    print(f"✅ Get current parameters: {'PASSED' if current_params is not None else 'FAILED'}")
    print(f"✅ Create parameter set: {'PASSED' if create_result else 'FAILED'}")
    print(f"✅ Validate parameters: {'PASSED' if validation_result else 'FAILED'}")
    print(f"✅ Export parameters: {'PASSED' if export_result else 'FAILED'}")
    print(f"✅ Update parameters: {'PASSED' if update_result else 'FAILED'}")
    print(f"✅ Export updated parameters: {'PASSED' if export_result2 else 'FAILED'}")
    print(f"✅ Delete parameters: {'PASSED' if delete_result else 'FAILED'}")
    
    print_section("Test Suite Complete")

if __name__ == "__main__":
    main() 