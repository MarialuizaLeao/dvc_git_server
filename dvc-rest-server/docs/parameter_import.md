# Parameter Import Functionality

This document describes the parameter import functionality implemented in the DVC REST server, which allows users to import parameters from various file formats into their projects.

## Overview

The parameter import system supports importing parameters from:
- **YAML files** (.yaml, .yml)
- **JSON files** (.json)
- **Environment files** (.env)

The system automatically detects the file format based on the file extension and content, validates the imported parameters, and stores them in the project's parameter set.

## Backend Implementation

### Core Functions

#### `import_parameters_from_upload()`
```python
async def import_parameters_from_upload(
    user_id: str, 
    project_id: str, 
    file_content: str, 
    filename: str, 
    format: str = None
) -> Dict[str, Any]
```

**Parameters:**
- `user_id`: The user ID
- `project_id`: The project ID
- `file_content`: The content of the uploaded file
- `filename`: The name of the uploaded file
- `format`: File format (yaml, json, env) - auto-detected if None

**Returns:**
- Dictionary containing import results, validation status, and file paths

#### `detect_file_format()`
```python
def detect_file_format(filename: str, content: str) -> str
```

Automatically detects the file format based on:
1. File extension (.yaml, .yml, .json, .env)
2. Content analysis (JSON structure, YAML syntax, ENV format)

### API Endpoints

#### POST `/{user_id}/{project_id}/parameters/upload`
Upload and import parameters from a file.

**Request:**
- `file`: Uploaded file (multipart/form-data)
- `format`: Optional format specification (yaml, json, env)

**Response:**
```json
{
  "message": "Parameters imported successfully from filename",
  "result": {
    "imported_from": "filename",
    "import_format": "yaml",
    "validation": {
      "valid": true,
      "errors": [],
      "warnings": []
    },
    "import_file_path": "/path/to/saved/file"
  }
}
```

### File Format Support

#### YAML Format
The system supports standard DVC parameter YAML format with sections:

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

#### JSON Format
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

#### Environment Format
```env
PREPARE_SPLIT=0.3
PREPARE_SEED=20170428
FEATURIZE_MAX_FEATURES=200
FEATURIZE_NGRAMS=2
TRAIN_SEED=20170428
TRAIN_N_EST=50
TRAIN_MIN_SPLIT=0.01
```

## Frontend Implementation

### ParameterManager Component

The frontend provides a user-friendly interface for parameter import:

#### Import Dialog
- File upload with drag-and-drop support
- Format validation and auto-detection
- Progress indication and error handling
- Success feedback and automatic refresh

#### Usage
1. Click the "Import" button in the Parameter Management section
2. Select a parameter file (YAML, JSON, or ENV format)
3. The system automatically detects the format and imports parameters
4. Validation results are displayed
5. The parameter set is updated and displayed

### API Integration

#### Constants
```typescript
UPLOAD_PARAMETERS: (userId: string, projectId: string) => 
  `${API_BASE_URL}/${userId}/${projectId}/parameters/upload`
```

#### File Upload Function
```typescript
const formData = new FormData();
formData.append('file', file);

const response = await fetch(API_ENDPOINTS.UPLOAD_PARAMETERS(userId, projectId), {
  method: 'POST',
  body: formData,
});
```

## DVC Integration

### Automatic DVC Tracking
When parameters are imported or updated, the system automatically:

1. **Saves `params.yaml`** in the project root directory
2. **Adds to DVC tracking** if DVC is initialized in the project
3. **Commits to Git** with descriptive commit messages
4. **Maintains version history** for parameter changes

### DVC Commands Used
```bash
# Add params.yaml to DVC tracking
dvc add params.yaml

# Commit DVC tracking file to Git
git add params.yaml.dvc
git commit -m "Add params.yaml to DVC tracking"

# Update DVC tracking when parameters change
dvc add params.yaml
git add params.yaml.dvc
git commit -m "Update params.yaml in DVC tracking"

# Remove from DVC tracking when deleted
dvc remove params.yaml.dvc
git add params.yaml.dvc
git commit -m "Remove params.yaml from DVC tracking"
```

### Parameter Usage in DVC Pipelines
The `params.yaml` file can be referenced in DVC pipeline stages:

```yaml
# dvc.yaml
stages:
  train:
    cmd: python train.py
    params:
      - params.yaml:data
      - params.yaml:model
    deps:
      - train.py
      - data/
    outs:
      - model.pkl
```

### Version Control Benefits
- **Parameter history**: Track changes to parameters over time
- **Experiment reproducibility**: Exact parameter values for each experiment
- **Collaboration**: Share parameter configurations across team members
- **Rollback capability**: Revert to previous parameter sets if needed

## Parsing Logic

### YAML Structure Handling
The system correctly parses DVC parameter YAML files with the following structure:

#### Sectioned Parameters
Parameters organized in sections (like `prepare`, `featurize`, `train`):
```yaml
prepare:
  split: 0.3
  seed: 20170428
```

#### Flat Parameters
Parameters without sections (automatically grouped into "default"):
```yaml
learning_rate: 0.001
epochs: 100
batch_size: 32
```

### Internal Representation
The system converts YAML sections into parameter groups:

```python
# YAML input
prepare:
  split: 0.3
  seed: 20170428

# Internal structure
{
  "name": "Parsed Parameters",
  "groups": [
    {
      "name": "prepare",
      "description": "Parameters for prepare",
      "parameters": [
        {
          "name": "split",
          "value": 0.3,
          "type": "number",
          "description": "Parameter split in prepare"
        },
        {
          "name": "seed", 
          "value": 20170428,
          "type": "number",
          "description": "Parameter seed in prepare"
        }
      ]
    }
  ]
}
```

### Type Detection
The system automatically detects parameter types:
- **Numbers**: `0.3`, `20170428`, `50`
- **Booleans**: `true`, `false`
- **Strings**: `"text"`, `"path/to/file"`
- **Arrays**: `[1, 2, 3]`
- **Objects**: `{key: value}`

## Validation and Error Handling

### Parameter Validation
- Type checking (string, number, boolean, array, object)
- Required field validation
- Custom validation rules (min, max, pattern)
- Format-specific validation

### Error Handling
- File format validation
- Content parsing errors
- Parameter validation failures
- Database operation errors

### Error Responses
```json
{
  "detail": "Unsupported file type. Allowed types: .yaml, .yml, .json, .env"
}
```

## File Storage

### Project Structure
```
project_path/
├── params.yaml                    # Main parameter file (project root)
├── params.yaml.dvc               # DVC tracking file (if DVC initialized)
├── imports/                      # Import history directory
│   ├── imported_params_20241201_143022_params.yaml
│   ├── imported_params_20241201_143045_config.json
│   └── imported_params_20241201_143112_settings.env
└── .dvc/                         # DVC configuration
```

### File Locations
- **`params.yaml`**: Located in project root for DVC compatibility
- **`params.yaml.dvc`**: DVC tracking file (auto-generated when DVC is initialized)
- **Import files**: Stored in `imports/` directory with timestamps for reference

### DVC Integration
The system automatically:
1. Saves `params.yaml` in the project root directory
2. Adds the file to DVC tracking if DVC is initialized
3. Commits changes to Git with descriptive messages
4. Maintains version control for parameter changes

### File Naming Convention
- **Main file**: `params.yaml` (project root)
- **Import history**: `imported_params_YYYYMMDD_HHMMSS_filename`
- **DVC file**: `params.yaml.dvc` (auto-generated)

## Testing

### Test Script
Run the test script to verify functionality:
```bash
cd dvc-rest-server
python test_parameter_import.py
```

### Test Coverage
- YAML file import
- JSON file import
- ENV file import
- Format auto-detection
- File upload simulation
- Parameter validation
- Error handling

## Usage Examples

### Command Line Testing
```python
# Test YAML import
result = await import_parameters_from_upload(
    user_id="user123",
    project_id="project456",
    file_content="data:\n  train_size: 0.8",
    filename="params.yaml",
    format="yaml"
)
```

### Frontend Usage
```typescript
// Upload file through the web interface
const fileInput = document.getElementById('parameter-file');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);

const response = await fetch('/api/parameters/upload', {
  method: 'POST',
  body: formData
});
```

## Security Considerations

### File Validation
- File extension validation
- Content type checking
- File size limits
- Malicious content detection

### Access Control
- User authentication required
- Project ownership verification
- Parameter set isolation

### Data Sanitization
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Future Enhancements

### Planned Features
- Support for additional formats (XML, CSV)
- Bulk import from multiple files
- Import from remote URLs
- Parameter merging strategies
- Import history and rollback

### Integration Opportunities
- Git integration for version control
- DVC parameter tracking
- CI/CD pipeline integration
- Parameter template libraries

## Troubleshooting

### Common Issues

#### File Format Not Recognized
- Check file extension
- Verify file content format
- Use explicit format parameter

#### Import Validation Errors
- Review parameter types
- Check required fields
- Validate custom rules

#### Database Errors
- Verify user and project IDs
- Check database connectivity
- Review parameter set structure

### Debug Information
- Enable debug logging
- Check import file paths
- Review validation results
- Monitor database operations

## API Reference

### Complete Endpoint Documentation
See the main API documentation for complete endpoint specifications, request/response schemas, and error codes.

### Integration Examples
Refer to the test scripts and frontend components for practical integration examples. 