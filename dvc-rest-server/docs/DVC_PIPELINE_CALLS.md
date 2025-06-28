# Enhanced DVC Pipeline Calls Documentation

This document describes the enhanced DVC pipeline calls functionality that has been added to the DVC REST server. These features provide comprehensive pipeline management capabilities for creating, updating, and executing DVC pipelines.

## Overview

The enhanced DVC pipeline calls provide the following capabilities:

1. **Individual Stage Creation** - Create DVC stages with dependencies, outputs, parameters, metrics, and plots
2. **Pipeline Templates** - Create complete pipeline templates with multiple stages
3. **Stage Management** - Update and remove existing pipeline stages
4. **Pipeline Validation** - Validate pipeline configurations
5. **Pipeline Execution** - Run pipelines with various options
6. **Pipeline Recovery** - Recover pipelines from saved configurations

## Core DVC Functions

### 1. Individual Stage Creation

#### Function: `add_stage`

Creates a single DVC stage with specified dependencies, outputs, and command.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `name` (str): The name of the stage
- `deps` (list, optional): List of dependencies (files/directories)
- `outs` (list, optional): List of outputs (files/directories)
- `params` (list, optional): List of parameter files
- `metrics` (list, optional): List of metric files
- `plots` (list, optional): List of plot files
- `command` (str, optional): The command to execute

**Example:**
```python
result = await add_stage(
    user_id="user123",
    project_id="project456",
    name="data_preparation",
    deps=["data/raw"],
    outs=["data/processed"],
    params=["params.yaml"],
    metrics=["metrics/accuracy.json"],
    command="python scripts/prepare_data.py"
)
```

#### Function: `add_stages`

Creates multiple DVC stages from a list of stage commands.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `stages` (list): List of stage commands as strings

**Example:**
```python
stages = [
    "dvc stage add -n data_prep -d data/raw -o data/processed python scripts/prepare_data.py",
    "dvc stage add -n train -d data/processed -o models/model.pkl python scripts/train.py"
]
result = await add_stages(user_id="user123", project_id="project456", stages=stages)
```

### 2. Pipeline Template Creation

#### Function: `create_pipeline_template`

Creates a complete pipeline template with predefined stages.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `template_name` (str): Name of the template
- `stages` (list): List of stage configurations

**Example:**
```python
stages = [
    {
        "name": "data_ingestion",
        "deps": ["data/raw"],
        "outs": ["data/ingested"],
        "command": "python scripts/ingest_data.py"
    },
    {
        "name": "feature_engineering",
        "deps": ["data/ingested"],
        "outs": ["data/features"],
        "params": ["params.yaml"],
        "command": "python scripts/engineer_features.py"
    }
]

result = await create_pipeline_template(
    user_id="user123",
    project_id="project456",
    template_name="ml_pipeline",
    stages=stages
)
```

### 3. Pipeline Stage Management

#### Function: `get_pipeline_stages`

Retrieves the current pipeline stages from dvc.yaml.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID

**Returns:**
- `dict`: Pipeline stages configuration

#### Function: `update_pipeline_stage`

Updates an existing pipeline stage.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `stage_name` (str): Name of the stage to update
- `updates` (dict): Updates to apply to the stage

**Example:**
```python
updates = {
    "deps": ["data/raw", "config.yaml"],
    "metrics": ["metrics/accuracy.json", "metrics/precision.json"]
}

result = await update_pipeline_stage(
    user_id="user123",
    project_id="project456",
    stage_name="data_preparation",
    updates=updates
)
```

#### Function: `remove_pipeline_stage`

Removes a pipeline stage from dvc.yaml.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `stage_name` (str): Name of the stage to remove

### 4. Pipeline Validation

#### Function: `validate_pipeline`

Validates the current pipeline configuration.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID

**Returns:**
- `dict`: Validation results with `valid`, `message`, and `details` fields

### 5. Pipeline Execution

#### Function: `repro`

Runs the DVC pipeline with various options.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `target` (str, optional): Specify the target stage or file to reproduce
- `pipeline` (bool, optional): Reproduce the entire pipeline containing the target
- `force` (bool, optional): Force reproduction even if outputs are up-to-date
- `dry_run` (bool, optional): Show what will be done without actually executing
- `no_commit` (bool, optional): Do not commit changes to cache

## API Endpoints

### 1. Create Individual Stage

**POST** `/{user_id}/{project_id}/stage`

Creates a single DVC stage.

**Request Body:**
```json
{
  "name": "data_preparation",
  "deps": ["data/raw"],
  "outs": ["data/processed"],
  "params": ["params.yaml"],
  "metrics": ["metrics/accuracy.json"],
  "plots": ["plots/confusion_matrix.png"],
  "command": "python scripts/prepare_data.py"
}
```

### 2. Create Multiple Stages

**POST** `/{user_id}/{project_id}/stages`

Creates multiple DVC stages.

**Request Body:**
```json
{
  "stages": [
    "dvc stage add -n data_prep -d data/raw -o data/processed python scripts/prepare_data.py",
    "dvc stage add -n train -d data/processed -o models/model.pkl python scripts/train.py"
  ]
}
```

### 3. Create Pipeline Template

**POST** `/{user_id}/{project_id}/pipeline/template`

Creates a pipeline template with predefined stages.

**Request Body:**
```json
{
  "template_name": "ml_pipeline_template",
  "stages": [
    {
      "name": "data_ingestion",
      "deps": ["data/raw"],
      "outs": ["data/ingested"],
      "command": "python scripts/ingest_data.py"
    },
    {
      "name": "feature_engineering",
      "deps": ["data/ingested"],
      "outs": ["data/features"],
      "params": ["params.yaml"],
      "command": "python scripts/engineer_features.py"
    }
  ]
}
```

### 4. Get Pipeline Stages

**GET** `/{user_id}/{project_id}/pipeline/stages`

Retrieves the current pipeline stages from dvc.yaml.

**Response:**
```json
{
  "stages": {
    "data_preparation": {
      "deps": ["data/raw"],
      "outs": ["data/processed"],
      "cmd": "python scripts/prepare_data.py"
    },
    "model_training": {
      "deps": ["data/processed"],
      "outs": ["models/model.pkl"],
      "cmd": "python scripts/train_model.py"
    }
  }
}
```

### 5. Update Pipeline Stage

**PUT** `/{user_id}/{project_id}/pipeline/stage/{stage_name}`

Updates an existing pipeline stage.

**Request Body:**
```json
{
  "updates": {
    "deps": ["data/raw", "config.yaml"],
    "metrics": ["metrics/accuracy.json", "metrics/precision.json"]
  }
}
```

### 6. Remove Pipeline Stage

**DELETE** `/{user_id}/{project_id}/pipeline/stage/{stage_name}`

Removes a pipeline stage from dvc.yaml.

### 7. Validate Pipeline

**GET** `/{user_id}/{project_id}/pipeline/validate`

Validates the current pipeline configuration.

**Response:**
```json
{
  "valid": true,
  "message": "Pipeline validation successful",
  "details": "All stages are properly configured"
}
```

### 8. Run Pipeline

**POST** `/{user_id}/{project_id}/pipeline/run`

Runs the pipeline with optional parameters.

**Request Body:**
```json
{
  "target": "data_preparation",
  "pipeline": true,
  "force": false,
  "dry_run": true,
  "no_commit": false
}
```

**Response:**
```json
{
  "message": "Pipeline executed successfully",
  "output": "Pipeline execution output...",
  "parameters": {
    "target": "data_preparation",
    "pipeline": true,
    "force": false,
    "dry_run": true,
    "no_commit": false
  }
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

### PipelineTemplateRequest

```python
class PipelineTemplateRequest(BaseModel):
    template_name: str
    stages: List[PipelineStage]
```

### StageUpdateRequest

```python
class StageUpdateRequest(BaseModel):
    updates: dict
```

### PipelineRunRequest

```python
class PipelineRunRequest(BaseModel):
    target: Optional[str] = None
    pipeline: bool = False
    force: bool = False
    dry_run: bool = False
    no_commit: bool = False
```

### PipelineValidationResult

```python
class PipelineValidationResult(BaseModel):
    valid: bool
    message: str
    details: Optional[str] = None
```

## Usage Examples

### Creating a Machine Learning Pipeline

```python
import requests

# Create individual stages
stage_data = {
    "name": "data_preparation",
    "deps": ["data/raw"],
    "outs": ["data/processed"],
    "params": ["params.yaml"],
    "metrics": ["metrics/accuracy.json"],
    "command": "python scripts/prepare_data.py"
}

response = requests.post(
    "http://localhost:8000/user123/project456/stage",
    json=stage_data
)

# Create a complete pipeline template
template_data = {
    "template_name": "ml_pipeline",
    "stages": [
        {
            "name": "data_ingestion",
            "deps": ["data/raw"],
            "outs": ["data/ingested"],
            "command": "python scripts/ingest_data.py"
        },
        {
            "name": "model_training",
            "deps": ["data/ingested"],
            "outs": ["models/model.pkl"],
            "metrics": ["metrics/accuracy.json"],
            "command": "python scripts/train_model.py"
        }
    ]
}

response = requests.post(
    "http://localhost:8000/user123/project456/pipeline/template",
    json=template_data
)

# Run the pipeline
run_data = {
    "pipeline": True,
    "force": False,
    "dry_run": True
}

response = requests.post(
    "http://localhost:8000/user123/project456/pipeline/run",
    json=run_data
)
```

### Updating Pipeline Stages

```python
# Update a stage
update_data = {
    "updates": {
        "deps": ["data/raw", "config.yaml"],
        "metrics": ["metrics/accuracy.json", "metrics/precision.json"]
    }
}

response = requests.put(
    "http://localhost:8000/user123/project456/pipeline/stage/data_preparation",
    json=update_data
)

# Remove a stage
response = requests.delete(
    "http://localhost:8000/user123/project456/pipeline/stage/old_stage"
)
```

## Error Handling

All functions include comprehensive error handling:

1. **Project Validation** - Ensures the project exists and belongs to the user
2. **Path Validation** - Verifies project paths exist before operations
3. **Command Validation** - Validates DVC commands before execution
4. **Git Integration** - Handles Git operations for version control
5. **Detailed Error Messages** - Provides specific error information for debugging

## Best Practices

1. **Use Templates** - Create pipeline templates for common workflows
2. **Validate First** - Always validate pipelines before execution
3. **Use Dry Runs** - Test pipeline execution with dry runs first
4. **Version Control** - All changes are automatically committed to Git
5. **Error Handling** - Implement proper error handling in client applications

## Testing

Use the provided test script `test_pipeline_dvc_calls.py` to test all functionality:

```bash
python test_pipeline_dvc_calls.py
```

This script tests:
- Individual stage creation
- Pipeline template creation
- Stage management (get, update, remove)
- Pipeline validation
- Pipeline execution
- Error handling

## Dependencies

The enhanced DVC pipeline calls require:
- DVC installed and configured
- Git repository initialized
- PyYAML for YAML file handling
- Proper file system permissions

## Security Considerations

1. **User Isolation** - All operations are scoped to specific users and projects
2. **Path Validation** - Prevents directory traversal attacks
3. **Command Sanitization** - Validates and sanitizes DVC commands
4. **Error Information** - Limits exposure of sensitive information in error messages 