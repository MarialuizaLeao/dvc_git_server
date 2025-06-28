#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for DVC pipeline integration functionality.
This script tests the complete pipeline workflow including DVC stage creation,
execution, and management.
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

# Test data
TEST_PIPELINE_CONFIG = {
    "name": "test_pipeline",
    "description": "A test pipeline for DVC integration",
    "stages": [
        {
            "name": "data_preparation",
            "deps": ["data/raw/*.csv"],
            "outs": ["data/processed/"],
            "params": ["config/params.yaml:preprocessing"],
            "metrics": ["metrics/preprocessing.json"],
            "plots": ["plots/preprocessing.html"],
            "command": "python scripts/prepare_data.py"
        },
        {
            "name": "model_training",
            "deps": ["data/processed/", "src/train.py"],
            "outs": ["models/"],
            "params": ["config/params.yaml:training"],
            "metrics": ["metrics/training.json"],
            "plots": ["plots/training.html"],
            "command": "python src/train.py"
        },
        {
            "name": "model_evaluation",
            "deps": ["models/", "data/processed/", "src/evaluate.py"],
            "outs": ["results/"],
            "params": ["config/params.yaml:evaluation"],
            "metrics": ["metrics/evaluation.json"],
            "plots": ["plots/evaluation.html"],
            "command": "python src/evaluate.py"
        }
    ]
}

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_response(response: requests.Response, title: str = "Response"):
    """Print formatted response information."""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Text Response: {response.text}")

def test_pipeline_creation():
    """Test pipeline configuration creation with DVC stages."""
    print_section("Testing Pipeline Configuration Creation")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config"
    
    print(f"Creating pipeline configuration...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(TEST_PIPELINE_CONFIG, indent=2)}")
    
    try:
        response = requests.post(url, json=TEST_PIPELINE_CONFIG)
        print_response(response, "Pipeline Creation Response")
        
        if response.status_code == 200:
            data = response.json()
            config_id = data.get("id")
            print(f"✅ Pipeline created successfully with ID: {config_id}")
            return config_id
        else:
            print(f"❌ Failed to create pipeline: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating pipeline: {str(e)}")
        return None

def test_pipeline_listing():
    """Test listing pipeline configurations."""
    print_section("Testing Pipeline Configuration Listing")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/configs"
    
    print(f"Listing pipeline configurations...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, "Pipeline Listing Response")
        
        if response.status_code == 200:
            data = response.json()
            configs = data.get("pipeline_configs", [])
            print(f"✅ Found {len(configs)} pipeline configurations")
            return configs
        else:
            print(f"❌ Failed to list pipelines: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error listing pipelines: {str(e)}")
        return []

def test_pipeline_status(config_id: str):
    """Test getting pipeline configuration status."""
    print_section("Testing Pipeline Configuration Status")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config/{config_id}/status"
    
    print(f"Getting pipeline status...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, "Pipeline Status Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline status retrieved successfully")
            return data
        else:
            print(f"❌ Failed to get pipeline status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting pipeline status: {str(e)}")
        return None

def test_pipeline_dry_run(config_id: str):
    """Test pipeline dry run."""
    print_section("Testing Pipeline Dry Run")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config/{config_id}/dry-run"
    
    print(f"Performing pipeline dry run...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url)
        print_response(response, "Pipeline Dry Run Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline dry run completed successfully")
            return data
        else:
            print(f"❌ Failed to perform dry run: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error performing dry run: {str(e)}")
        return None

def test_pipeline_execution(config_id: str):
    """Test pipeline execution."""
    print_section("Testing Pipeline Execution")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config/{config_id}/execute"
    
    execution_request = {
        "force": False,
        "dry_run": False
    }
    
    print(f"Executing pipeline...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(execution_request, indent=2)}")
    
    try:
        response = requests.post(url, json=execution_request)
        print_response(response, "Pipeline Execution Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline executed successfully")
            return data
        else:
            print(f"❌ Failed to execute pipeline: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error executing pipeline: {str(e)}")
        return None

def test_pipeline_update(config_id: str):
    """Test updating pipeline configuration."""
    print_section("Testing Pipeline Configuration Update")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config/{config_id}"
    
    update_request = {
        "name": "updated_test_pipeline",
        "description": "Updated test pipeline description",
        "stages": [
            {
                "name": "updated_data_preparation",
                "deps": ["data/raw/*.csv"],
                "outs": ["data/processed/"],
                "params": ["config/params.yaml:preprocessing"],
                "metrics": ["metrics/preprocessing.json"],
                "plots": ["plots/preprocessing.html"],
                "command": "python scripts/prepare_data_updated.py"
            }
        ]
    }
    
    print(f"Updating pipeline configuration...")
    print(f"URL: {url}")
    print(f"Request: {json.dumps(update_request, indent=2)}")
    
    try:
        response = requests.put(url, json=update_request)
        print_response(response, "Pipeline Update Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline updated successfully")
            return data
        else:
            print(f"❌ Failed to update pipeline: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error updating pipeline: {str(e)}")
        return None

def test_pipeline_deletion(config_id: str):
    """Test deleting pipeline configuration."""
    print_section("Testing Pipeline Configuration Deletion")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/pipeline/config/{config_id}"
    
    print(f"Deleting pipeline configuration...")
    print(f"URL: {url}")
    
    try:
        response = requests.delete(url)
        print_response(response, "Pipeline Deletion Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pipeline deleted successfully")
            return data
        else:
            print(f"❌ Failed to delete pipeline: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error deleting pipeline: {str(e)}")
        return None

def test_dvc_status():
    """Test DVC status endpoint."""
    print_section("Testing DVC Status")
    
    url = f"{BASE_URL}/{USER_ID}/{PROJECT_ID}/dvc/status"
    
    print(f"Getting DVC status...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print_response(response, "DVC Status Response")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ DVC status retrieved successfully")
            return data
        else:
            print(f"❌ Failed to get DVC status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting DVC status: {str(e)}")
        return None

def main():
    """Run all pipeline integration tests."""
    print_section("DVC Pipeline Integration Test Suite")
    print(f"Testing with User ID: {USER_ID}")
    print(f"Testing with Project ID: {PROJECT_ID}")
    print(f"Base URL: {BASE_URL}")
    
    # Test DVC status first
    dvc_status = test_dvc_status()
    
    # Test pipeline creation
    config_id = test_pipeline_creation()
    
    if config_id:
        # Test pipeline listing
        configs = test_pipeline_listing()
        
        # Test pipeline status
        status = test_pipeline_status(config_id)
        
        # Test pipeline dry run
        dry_run = test_pipeline_dry_run(config_id)
        
        # Test pipeline execution (commented out to avoid actual execution)
        # execution = test_pipeline_execution(config_id)
        
        # Test pipeline update
        update = test_pipeline_update(config_id)
        
        # Test pipeline deletion
        deletion = test_pipeline_deletion(config_id)
        
        print_section("Test Summary")
        print(f"✅ Pipeline creation: {'PASSED' if config_id else 'FAILED'}")
        print(f"✅ Pipeline listing: {'PASSED' if configs else 'FAILED'}")
        print(f"✅ Pipeline status: {'PASSED' if status else 'FAILED'}")
        print(f"✅ Pipeline dry run: {'PASSED' if dry_run else 'FAILED'}")
        print(f"✅ Pipeline update: {'PASSED' if update else 'FAILED'}")
        print(f"✅ Pipeline deletion: {'PASSED' if deletion else 'FAILED'}")
        print(f"✅ DVC status: {'PASSED' if dvc_status else 'FAILED'}")
    else:
        print_section("Test Summary")
        print("❌ Pipeline creation failed - skipping other tests")
    
    print_section("Test Suite Complete")

if __name__ == "__main__":
    main() 