# Parameter Management System

This document describes the comprehensive parameter management system that provides a user-friendly alternative to manually editing `params.yaml` files.

## Overview

The parameter management system offers:

- **Visual Parameter Editor**: Web-based interface for managing parameters
- **Validation**: Built-in validation for parameter types and values
- **Import/Export**: Support for multiple file formats (YAML, JSON, ENV)
- **Version Control**: Automatic Git integration for parameter changes
- **Type Safety**: Support for different parameter types (string, number, boolean, array)

## Key Features

### 1. User-Friendly Interface
- **Visual Editor**: No need to manually edit YAML files
- **Grouped Parameters**: Organize parameters into logical groups
- **Real-time Validation**: Immediate feedback on parameter values
- **Type-specific Inputs**: Appropriate input controls for each parameter type

### 2. Validation System
- **Type Validation**: Ensures parameters match their declared types
- **Range Validation**: Min/max values for numeric parameters
- **Required Parameters**: Mark parameters as required
- **Custom Validation**: Extensible validation rules

### 3. Import/Export Capabilities
- **Multiple Formats**: YAML, JSON, Environment Variables
- **Bulk Import**: Import parameters from existing files
- **Export Options**: Export with or without metadata
- **Format Conversion**: Convert between different formats

## API Endpoints

### Parameter Set Management

#### GET `/{user_id}/{project_id}/parameters`
Get all parameter sets for a project.

**Response:**
```json
{
  "parameter_sets": [...],
  "current_set": {...},
  "file_path": "config/params.yaml"
}
```

#### GET `/{user_id}/{project_id}/parameters/current`
Get the current parameter set.

**Response:**
```json
{
  "success": true,
  "message": "Parameter set retrieved successfully",
  "parameter_set": {
    "name": "ML Training Parameters",
    "description": "Parameters for machine learning training",
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
          }
        ]
      }
    ]
  }
}
```

#### POST `/{user_id}/{project_id}/parameters`
Create a new parameter set.

**Request Body:**
```json
{
  "name": "My Parameter Set",
  "description": "Custom parameter set",
  "groups": [
    {
      "name": "training",
      "description": "Training parameters",
      "parameters": [
        {
          "name": "learning_rate",
          "value": 0.001,
          "type": "number",
          "description": "Learning rate",
          "validation": {"min": 0.0001, "max": 1.0}
        }
      ]
    }
  ]
}
```

#### PUT `/{user_id}/{project_id}/parameters`
Update the current parameter set.

#### DELETE `/{user_id}/{project_id}/parameters`
Delete the current parameter set.

### Import/Export

#### POST `/{user_id}/{project_id}/parameters/import`
Import parameters from a file.

#### GET `/{user_id}/{project_id}/parameters/export`
Export parameters to a file.

#### POST `/{user_id}/{project_id}/parameters/upload`
Upload and import parameters from a file.

#### POST `/{user_id}/{project_id}/parameters/validate`
Validate the current parameter set.

## Frontend Interface

The parameter management system includes a comprehensive React-based frontend interface with:

- **Parameter Table**: Tabular view of parameters with inline editing
- **Group Accordion**: Collapsible parameter groups
- **Validation Feedback**: Real-time validation status
- **Action Buttons**: Save, delete, import, export operations

### Key Components
- **Parameter Table**: Tabular view of parameters with inline editing
- **Group Accordion**: Collapsible parameter groups
- **Validation Feedback**: Real-time validation status
- **Action Buttons**: Save, delete, import, export operations

## Usage Examples

### Creating a Parameter Set via API
```python
import requests

# Create a parameter set
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
                }
            ]
        }
    ]
}

response = requests.post(
    f"{API_BASE_URL}/{user_id}/{project_id}/parameters",
    json=parameter_set
)
```

### Importing Parameters from YAML
```python
# Import from YAML file
with open("params.yaml", "r") as f:
    yaml_content = f.read()

response = requests.post(
    f"{API_BASE_URL}/{user_id}/{project_id}/parameters/upload",
    files={"file": ("params.yaml", yaml_content, "text/yaml")}
)
```

### Validating Parameters
```python
# Validate current parameters
response = requests.post(
    f"{API_BASE_URL}/{user_id}/{project_id}/parameters/validate"
)

if response.json()["valid"]:
    print("All parameters are valid!")
else:
    print(f"Validation errors: {response.json()['errors']}")
```

## File Format Support

### YAML Format
```yaml
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
```

### JSON Format
```json
{
  "prepare": {
    "split": 0.3,
    "seed": 20170428
  },
  "featurize": {
    "max_features": 200,
    "ngrams": 2
  },
  "train": {
    "seed": 20170428,
    "n_est": 50,
    "min_split": 0.01
  }
}
```

### Environment Variables Format
```env
PREPARE_SPLIT=0.3
PREPARE_SEED=20170428
FEATURIZE_MAX_FEATURES=200
FEATURIZE_NGRAMS=2
TRAIN_SEED=20170428
TRAIN_N_EST=50
TRAIN_MIN_SPLIT=0.01
```

## Integration with DVC

The parameter management system integrates seamlessly with DVC:

- **Automatic Git Integration**: All parameter changes are automatically committed to Git
- **DVC Tracking**: Parameters can be tracked by DVC for version control
- **Pipeline Integration**: Parameters work with DVC pipelines
- **File Location**: Parameters are saved as `params.yaml` in the project root

## Error Handling

The system includes comprehensive error handling:

- **Validation Errors**: Clear feedback on parameter validation issues
- **File Format Errors**: Support for multiple file formats with proper error handling
- **Git Integration Errors**: Robust handling of Git operations
- **Network Errors**: Proper error handling for API calls

## Security Considerations

- **User Isolation**: Parameters are isolated per user and project
- **Input Validation**: All inputs are validated before processing
- **File Upload Security**: Secure file upload handling
- **Access Control**: Proper access control for parameter operations 