#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for code upload functionality.
This script tests the code upload and management endpoints.
"""

import requests
import json
import os
import tempfile
from datetime import datetime

# API base URL - adjust this to match your server configuration
BASE_URL = "http://localhost:8000/api"

def create_test_user():
    """Create a test user for testing"""
    user_data = {
        "username": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "user_directory": f"/test/user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Created test user: {user['username']}")
            return user['id']
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def create_test_project(user_id):
    """Create a test project for testing"""
    project_data = {
        "username": "test_user",
        "project_name": f"test_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "Test project for code upload",
        "project_type": "other",
        "framework": "scikit-learn",
        "python_version": "3.9",
        "dependencies": ["pandas", "numpy", "scikit-learn"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/{user_id}/project/create", json=project_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created test project: {project_data['project_name']}")
            return result['id']
        else:
            print(f"❌ Failed to create project: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def test_code_upload():
    """Test the code upload functionality"""
    
    print("🚀 Testing Code Upload Functionality")
    print("=" * 60)
    
    # Step 1: Create test user and project
    print("\nStep 1: Creating test user and project...")
    user_id = create_test_user()
    if not user_id:
        print("❌ Cannot proceed without a test user")
        return
    
    project_id = create_test_project(user_id)
    if not project_id:
        print("❌ Cannot proceed without a test project")
        return
    
    # Test 1: Create code file via API
    print("\nTest 1: Creating code file via API...")
    
    code_file_data = {
        "filename": "main.py",
        "file_path": "src/main.py",
        "file_type": "python",
        "description": "Main application file",
        "content": """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def load_data():
    \"\"\"Load and prepare the dataset\"\"\"
    # Load your data here
    data = pd.read_csv('data/dataset.csv')
    return data

def train_model(X, y):
    \"\"\"Train a machine learning model\"\"\"
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def main():
    \"\"\"Main function\"\"\"
    print("Starting ML pipeline...")
    
    # Load data
    data = load_data()
    print(f"Loaded {len(data)} samples")
    
    # Train model
    X = data.drop('target', axis=1)
    y = data['target']
    model = train_model(X, y)
    
    print("Model training completed!")
    return model

if __name__ == "__main__":
    main()
"""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/code/file",
            json=code_file_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created code file: {code_file_data['filename']}")
            print(f"  File ID: {result['file_id']}")
            print(f"  Git Commit Hash: {result.get('git_commit_hash', 'N/A')}")
            file_id = result['file_id']
        else:
            print(f"❌ Failed to create code file: {response.status_code}")
            print(f"Error: {response.text}")
            file_id = None
            
    except Exception as e:
        print(f"❌ Error creating code file: {e}")
        file_id = None
    
    # Test 2: Create configuration file
    print("\nTest 2: Creating configuration file...")
    
    config_file_data = {
        "filename": "config.yaml",
        "file_path": "config/config.yaml",
        "file_type": "config",
        "description": "Configuration file for the project",
        "content": """
# Project Configuration
project:
  name: "ML Pipeline Project"
  version: "1.0.0"
  description: "Machine learning pipeline with DVC"

# Data Configuration
data:
  input_path: "data/raw/"
  output_path: "data/processed/"
  train_split: 0.8
  random_state: 42

# Model Configuration
model:
  type: "RandomForest"
  parameters:
    n_estimators: 100
    max_depth: 10
    random_state: 42

# Training Configuration
training:
  test_size: 0.2
  validation_split: 0.1
  epochs: 100
  batch_size: 32

# Output Configuration
output:
  model_path: "models/"
  metrics_path: "metrics/"
  plots_path: "plots/"
"""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/code/file",
            json=config_file_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created config file: {config_file_data['filename']}")
            config_file_id = result['file_id']
        else:
            print(f"❌ Failed to create config file: {response.status_code}")
            print(f"Error: {response.text}")
            config_file_id = None
            
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        config_file_id = None
    
    # Test 3: Get code files
    print("\nTest 3: Getting code files...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/code/files")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result.get('code_files', []))} code files")
            for file in result.get('code_files', []):
                print(f"  - {file['filename']}: {file['file_path']} ({file['file_type']})")
        else:
            print(f"❌ Failed to get code files: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting code files: {e}")
    
    # Test 4: Get specific code file
    if file_id:
        print(f"\nTest 4: Getting specific code file ({file_id})...")
        
        try:
            response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/code/file/{file_id}")
            
            if response.status_code == 200:
                file_info = response.json()
                print(f"✅ Retrieved code file: {file_info['filename']}")
                print(f"  Type: {file_info['file_type']}")
                print(f"  Status: {file_info['status']}")
                print(f"  Size: {file_info['size']} bytes")
            else:
                print(f"❌ Failed to get code file: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting code file: {e}")
    
    # Test 5: Get file content
    if file_id:
        print(f"\nTest 5: Getting file content ({file_id})...")
        
        try:
            response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/code/file/{file_id}/content")
            
            if response.status_code == 200:
                content = response.json()
                print(f"✅ Retrieved file content: {content['filename']}")
                print(f"  Content length: {len(content['content'])} characters")
                print(f"  First 100 chars: {content['content'][:100]}...")
            else:
                print(f"❌ Failed to get file content: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting file content: {e}")
    
    # Test 6: Update code file
    if file_id:
        print(f"\nTest 6: Updating code file ({file_id})...")
        
        update_data = {
            "content": """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def load_data():
    \"\"\"Load and prepare the dataset\"\"\"
    # Load your data here
    data = pd.read_csv('data/dataset.csv')
    return data

def train_model(X, y):
    \"\"\"Train a machine learning model\"\"\"
    model = RandomForestClassifier(n_estimators=200, random_state=42)  # Updated
    model.fit(X, y)
    return model

def evaluate_model(model, X_test, y_test):
    \"\"\"Evaluate the model performance\"\"\"
    score = model.score(X_test, y_test)
    print(f"Model accuracy: {score:.4f}")
    return score

def main():
    \"\"\"Main function\"\"\"
    print("Starting ML pipeline...")
    
    # Load data
    data = load_data()
    print(f"Loaded {len(data)} samples")
    
    # Split data
    X = data.drop('target', axis=1)
    y = data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    evaluate_model(model, X_test, y_test)
    
    print("Model training and evaluation completed!")
    return model

if __name__ == "__main__":
    main()
""",
            "description": "Updated main.py with evaluation function"
        }
        
        try:
            response = requests.put(
                f"{BASE_URL}/{user_id}/{project_id}/code/file/{file_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Updated code file: {result['message']}")
            else:
                print(f"❌ Failed to update code file: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error updating code file: {e}")
    
    # Test 7: Bulk upload
    print("\nTest 7: Bulk upload of multiple files...")
    
    bulk_files_data = {
        "files": [
            {
                "filename": "utils.py",
                "file_path": "src/utils.py",
                "file_type": "python",
                "description": "Utility functions",
                "content": """
import os
import json
import yaml
from pathlib import Path

def load_config(config_path: str) -> dict:
    \"\"\"Load configuration from YAML file\"\"\"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_metrics(metrics: dict, output_path: str):
    \"\"\"Save metrics to JSON file\"\"\"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)

def ensure_dir(path: str):
    \"\"\"Ensure directory exists\"\"\"
    Path(path).mkdir(parents=True, exist_ok=True)
"""
            },
            {
                "filename": "README.md",
                "file_path": "README.md",
                "file_type": "documentation",
                "description": "Project documentation",
                "content": """
# ML Pipeline Project

This project implements a machine learning pipeline using DVC for version control.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize DVC:
   ```bash
   dvc init
   ```

3. Run the pipeline:
   ```bash
   python src/main.py
   ```

## Project Structure

- `src/` - Source code
- `data/` - Data files
- `models/` - Trained models
- `config/` - Configuration files
- `metrics/` - Performance metrics

## Usage

See the main.py file for usage examples.
"""
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/{user_id}/{project_id}/code/files/bulk",
            json=bulk_files_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bulk upload completed: {result['successful_uploads']} successful, {result['failed_uploads']} failed")
        else:
            print(f"❌ Failed to perform bulk upload: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error performing bulk upload: {e}")
    
    # Test 8: Scan code files
    print("\nTest 8: Scanning code files...")
    
    try:
        response = requests.get(f"{BASE_URL}/{user_id}/{project_id}/code/files/scan")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Scanned {len(result.get('files', []))} files in project")
            for file in result.get('files', []):
                print(f"  - {file['filename']}: {file['file_path']} ({file['file_type']})")
        else:
            print(f"❌ Failed to scan code files: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error scanning code files: {e}")
    
    # Test 9: Delete code file
    if config_file_id:
        print(f"\nTest 9: Deleting code file ({config_file_id})...")
        
        try:
            response = requests.delete(f"{BASE_URL}/{user_id}/{project_id}/code/file/{config_file_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Deleted code file: {result['message']}")
            else:
                print(f"❌ Failed to delete code file: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error deleting code file: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Code Upload Testing Complete!")
    print(f"User ID: {user_id}")
    print(f"Project ID: {project_id}")

def main():
    """Main function"""
    print("🔧 Code Upload Test")
    print("This script tests the code upload and management functionality.")
    print("Note: This test requires the server to be running.")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please make sure the server is running on http://localhost:8000")
        return
    
    # Run the tests
    test_code_upload()

if __name__ == "__main__":
    main() 