# Pipeline API Documentation

This document describes the new pipeline configuration and recovery API endpoints that have been added to the DVC REST server.

## Overview

The pipeline API allows users to:
- Create and manage pipeline configurations
- Execute pipelines with different parameters
- Recover pipelines from saved configurations
- Store pipeline stages and their dependencies

## API Endpoints

### 1. Create Pipeline Configuration

**POST** `/{user_id}/{project_id}/pipeline/config`

Creates a new pipeline configuration for a project.

**Request Body:**
```json
{
  "name": "My Pipeline",
  "description": "A data processing pipeline",
  "stages": [
    {
      "name": "data_preparation",
      "deps": ["data/raw"],
      "outs": ["data/processed"],
      "params": ["params.yaml"],
      "metrics": ["metrics/accuracy.json"],
      "command": "python scripts/prepare_data.py",
      "description": "Prepare and clean the data"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Pipeline configuration 'My Pipeline' created successfully",
  "id": "507f1f77bcf86cd799439013"
}
```

### 2. Get All Pipeline Configurations

**GET** `/{user_id}/{project_id}/pipeline/configs`

Retrieves all pipeline configurations for a project.

**Response:**
```json
{
  "pipeline_configs": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "user_id": "507f1f77bcf86cd799439011",
      "project_id": "507f1f77bcf86cd799439012",
      "name": "My Pipeline",
      "description": "A data processing pipeline",
      "stages": [...],
      "version": "1.0",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "is_active": true
    }
  ]
}
```

### 3. Get Specific Pipeline Configuration

**GET** `/{user_id}/{project_id}/pipeline/config/{config_id}`

Retrieves a specific pipeline configuration by ID.

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439013",
  "user_id": "507f1f77bcf86cd799439011",
  "project_id": "507f1f77bcf86cd799439012",
  "name": "My Pipeline",
  "description": "A data processing pipeline",
  "stages": [...],
  "version": "1.0",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "is_active": true
}
```

### 4. Update Pipeline Configuration

**PUT** `/{user_id}/{project_id}/pipeline/config/{config_id}`

Updates an existing pipeline configuration.

**Request Body:**
```json
{
  "name": "Updated Pipeline Name",
  "description": "Updated description",
  "is_active": true
}
```

**Response:**
```json
{
  "message": "Pipeline configuration updated successfully"
}
```

### 5. Delete Pipeline Configuration

**DELETE** `/{user_id}/{project_id}/pipeline/config/{config_id}`

Deletes a pipeline configuration.

**Response:**
```json
{
  "message": "Pipeline configuration deleted successfully"
}
```

### 6. Execute Pipeline

**POST** `/{user_id}/{project_id}/pipeline/execute`

Executes a pipeline with the specified configuration.

**Request Body:**
```json
{
  "pipeline_config_id": "507f1f77bcf86cd799439013",
  "force": false,
  "dry_run": false,
  "targets": ["data_preparation", "model_training"]
}
```

**Response:**
```json
{
  "execution_id": "exec_20240101_120000",
  "status": "completed",
  "start_time": "2024-01-01T12:00:00",
  "end_time": "2024-01-01T12:05:00",
  "output": "Pipeline execution completed successfully",
  "error": null
}
```

### 7. Recover Pipeline

**POST** `/{user_id}/{project_id}/pipeline/recover?config_id={config_id}`

Recovers a pipeline by applying a saved configuration to the current project.

**Response:**
```json
{
  "message": "Pipeline 'My Pipeline' recovered successfully",
  "config_name": "My Pipeline",
  "stages_applied": 3
}
```

## Data Models

### PipelineStage

```python
class PipelineStage(BaseModel):
    name: str
    deps: List[str] = []
    outs: List[str] = []
    params: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    plots: Optional[List[str]] = None
    command: str
    description: Optional[str] = None
```

### PipelineConfig

```python
class PipelineConfig(BaseModel):
    name: str
    description: Optional[str] = None
    stages: List[PipelineStage]
    version: str = "1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True
```

### PipelineExecutionRequest

```python
class PipelineExecutionRequest(BaseModel):
    pipeline_config_id: Optional[str] = None
    force: bool = False
    dry_run: bool = False
    targets: Optional[List[str]] = None
```

## Usage Examples

### Creating a Machine Learning Pipeline

```python
import requests

# Create a pipeline configuration
pipeline_config = {
    "name": "ML Training Pipeline",
    "description": "Complete ML pipeline from data prep to evaluation",
    "stages": [
        {
            "name": "data_preparation",
            "deps": ["data/raw"],
            "outs": ["data/processed"],
            "params": ["params.yaml"],
            "command": "python scripts/prepare_data.py",
            "description": "Clean and prepare the dataset"
        },
        {
            "name": "feature_engineering",
            "deps": ["data/processed"],
            "outs": ["data/features"],
            "params": ["params.yaml"],
            "command": "python scripts/engineer_features.py",
            "description": "Create features for training"
        },
        {
            "name": "model_training",
            "deps": ["data/features"],
            "outs": ["models/model.pkl"],
            "params": ["params.yaml"],
            "metrics": ["metrics/accuracy.json"],
            "command": "python scripts/train_model.py",
            "description": "Train the machine learning model"
        },
        {
            "name": "evaluation",
            "deps": ["models/model.pkl", "data/test"],
            "outs": ["results/evaluation.json"],
            "metrics": ["metrics/final_accuracy.json"],
            "command": "python scripts/evaluate_model.py",
            "description": "Evaluate model performance"
        }
    ]
}

response = requests.post(
    "http://localhost:8000/user123/project456/pipeline/config",
    json=pipeline_config
)
config_id = response.json()["id"]

# Execute the pipeline
execution_request = {
    "pipeline_config_id": config_id,
    "force": False,
    "dry_run": False
}

response = requests.post(
    "http://localhost:8000/user123/project456/pipeline/execute",
    json=execution_request
)
```

### Recovering a Pipeline

```python
# Recover a pipeline from a saved configuration
response = requests.post(
    "http://localhost:8000/user123/project456/pipeline/recover?config_id=config123"
)
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Project not found"
}
```

## Database Schema

Pipeline configurations are stored in the `pipeline_configs` collection with the following structure:

```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "project_id": String,
  "name": String,
  "description": String,
  "stages": Array,
  "version": String,
  "created_at": String,
  "updated_at": String,
  "is_active": Boolean
}
```

## Testing

Use the provided test script to verify the API functionality:

```bash
cd dvc-rest-server
python test_pipeline_api.py
```

Make sure the server is running on `http://localhost:8000` before running the tests. 