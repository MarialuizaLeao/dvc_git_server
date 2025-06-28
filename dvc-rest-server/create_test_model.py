#!/usr/bin/env python3
"""
Script to create a test model file for debugging model evaluation.
"""
import pickle
import os
import sys

def create_test_model():
    """Create a simple test model"""
    # Create a simple mock model
    class MockModel:
        def __init__(self):
            self.name = "Test Model"
            self.version = "1.0"
        
        def predict(self, X):
            # Mock prediction
            return [0.5] * len(X)
    
    model = MockModel()
    
    # Create models directory if it doesn't exist
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"Created directory: {models_dir}")
    
    # Save model to different locations for testing
    model_paths = [
        "model.pkl",  # In current directory
        "models/model.pkl",  # In models subdirectory
        "models/test_model.pkl"  # Another test file
    ]
    
    for path in model_paths:
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        print(f"Created test model at: {path}")
    
    print("Test models created successfully!")
    print("You can now test model evaluation with these files.")

if __name__ == "__main__":
    create_test_model() 