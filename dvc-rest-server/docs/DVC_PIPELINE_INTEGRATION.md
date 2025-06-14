# DVC Pipeline Integration

This document describes the DVC pipeline integration functionality that has been added to the FastAPI backend.

## Overview

The pipeline integration provides a complete workflow for creating, managing, and executing DVC pipelines through the REST API. It includes:

- Pipeline configuration management (CRUD operations)
- DVC stage creation and management
- Pipeline validation and execution
- Dry run capabilities
- Status monitoring

## Enhanced Endpoints

### 1. Pipeline Configuration Creation
**Endpoint:** `POST /{user_id}/{project_id}/pipeline/config`

**Enhanced Features:**
- Creates pipeline template file
- Creates individual DVC stages for each stage in the configuration
- Validates the pipeline after creation
- Provides detailed feedback on stage creation success/failure

**Request Body:**
```json
{
  "name": "pipeline_name",
  "description": "Pipeline description",
  "stages": [
    {
      "name": "stage_name",
      "deps": ["dependency1", "dependency2"],
      "outs": ["output1", "output2"],
      "params": ["param1", "param2"],
      "metrics": ["metric1", "metric2"],
      "plots": ["plot1", "plot2"],
      "command": "python script.py"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Pipeline configuration created successfully",
  "id": "config_id",
  "template_result": "template_creation_result",
  "stages_created": 3,
  "stages_failed": 0,
  "created_stages": [...],
  "failed_stages": [],
  "validation": {...}
}
```

### 2. Pipeline Configuration Execution
**Endpoint:** `POST /{user_id}/{project_id}/pipeline/config/{config_id}/execute`

**Features:**
- Validates pipeline before execution
- Executes the pipeline using DVC repro
- Updates execution metadata in database
- Supports force and dry-run options

**Request Body:**
```json
{
  "force": false,
  "dry_run": false
}
```

### 3. Pipeline Dry Run
**Endpoint:** `POST /{user_id}/{project_id}/pipeline/config/{config_id}/dry-run`

**Features:**
- Performs validation without actual execution
- Shows what would be executed
- Safe for testing pipeline configurations

### 4. Pipeline Status
**Endpoint:** `GET /{user_id}/{project_id}/pipeline/config/{config_id}/status`

**Features:**
- Returns comprehensive pipeline status
- Includes DVC status, validation results, and pipeline stages
- Shows execution history and metadata

### 5. Enhanced Pipeline Update
**Endpoint:** `PUT /{user_id}/{project_id}/pipeline/config/{config_id}`

**Enhanced Features:**
- Updates pipeline configuration in database
- Removes existing DVC stages
- Creates new DVC stages based on updated configuration
- Validates the updated pipeline
- Provides detailed feedback on stage updates

### 6. Enhanced Pipeline Deletion
**Endpoint:** `DELETE /{user_id}/{project_id}/pipeline/config/{config_id}`

**Enhanced Features:**
- Removes all associated DVC stages
- Deletes pipeline configuration from database
- Provides feedback on stage removal success/failure

## DVC Integration Details

### Stage Creation Process
1. **Template Creation:** Creates a pipeline template file using `create_pipeline_template()`
2. **Individual Stage Creation:** Creates each stage using `add_stage()` function
3. **Validation:** Validates the complete pipeline using `validate_pipeline()`
4. **Database Storage:** Stores configuration metadata in MongoDB

### Stage Update Process
1. **Existing Stage Removal:** Removes all existing DVC stages
2. **New Stage Creation:** Creates new stages based on updated configuration
3. **Validation:** Validates the updated pipeline
4. **Database Update:** Updates configuration metadata

### Stage Cleanup Process
1. **Stage Removal:** Removes all DVC stages associated with the pipeline
2. **Database Cleanup:** Removes configuration metadata
3. **Error Handling:** Provides feedback on cleanup success/failure

## Error Handling

The integration includes comprehensive error handling:

- **Individual Stage Errors:** Failed stage creation doesn't prevent other stages from being created
- **Validation Errors:** Pipeline execution is blocked if validation fails
- **DVC Command Errors:** Proper error reporting for DVC command failures
- **Database Errors:** Graceful handling of database operation failures

## Testing

A comprehensive test script `test_pipeline_dvc_integration.py` is provided to verify:

- Pipeline configuration creation
- DVC stage creation and management
- Pipeline validation
- Dry run functionality
- Pipeline execution
- Configuration updates
- Pipeline deletion
- Status monitoring

## Usage Examples

### Creating a Pipeline
```bash
curl -X POST "http://localhost:8000/user123/project456/pipeline/config" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ml_pipeline",
    "description": "Machine learning pipeline",
    "stages": [
      {
        "name": "prepare_data",
        "deps": ["data/raw/*.csv"],
        "outs": ["data/processed/"],
        "command": "python scripts/prepare_data.py"
      },
      {
        "name": "train_model",
        "deps": ["data/processed/", "src/train.py"],
        "outs": ["models/"],
        "command": "python src/train.py"
      }
    ]
  }'
```

### Executing a Pipeline
```bash
curl -X POST "http://localhost:8000/user123/project456/pipeline/config/config_id/execute" \
  -H "Content-Type: application/json" \
  -d '{"force": false, "dry_run": false}'
```

### Getting Pipeline Status
```bash
curl -X GET "http://localhost:8000/user123/project456/pipeline/config/config_id/status"
```

## Benefits

1. **Complete Integration:** Full DVC pipeline management through REST API
2. **Error Resilience:** Graceful handling of partial failures
3. **Validation:** Built-in pipeline validation before execution
4. **Monitoring:** Comprehensive status and execution tracking
5. **Flexibility:** Support for dry runs and force execution
6. **Feedback:** Detailed responses with success/failure information

## Next Steps

1. **Frontend Integration:** Add pipeline management UI to the frontend
2. **Advanced Features:** Add support for pipeline branching and versioning
3. **Monitoring:** Add real-time pipeline execution monitoring
4. **Notifications:** Add webhook support for pipeline events
5. **Scheduling:** Add support for scheduled pipeline execution 