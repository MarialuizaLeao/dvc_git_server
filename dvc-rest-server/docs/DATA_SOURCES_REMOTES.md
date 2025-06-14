# Data Sources and Remote Storage Documentation

This document describes the data sources and remote storage functionality that has been implemented in the DVC REST server. These features provide comprehensive data management capabilities for importing, tracking, and storing data in DVC projects.

## Overview

The data sources and remote storage functionality provides the following capabilities:

1. **Data Source Management** - Import data from URLs, local files, and remote sources
2. **Remote Storage Management** - Configure and manage DVC remote storage backends
3. **Data Operations** - Push, pull, and sync data with remote storage
4. **Status Tracking** - Monitor data source status and operations
5. **Integration** - Seamless integration with DVC tracking and version control

## Data Source Management

### Data Source Types

The system supports three types of data sources:

1. **URL Sources** - Download data from HTTP/HTTPS URLs
2. **Local Sources** - Copy data from local file system paths
3. **Remote Sources** - Import data from DVC remote repositories

### Core Data Source Functions

#### Function: `add_data_source`

Adds a data source to the project and tracks it with DVC.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `name` (str): Name of the data source
- `source_type` (str): Type of data source (url, local, remote)
- `source_path` (str): Path or URL to the data source
- `destination` (str): Where to store the data in the project
- `description` (str, optional): Description of the data source

**Example:**
```python
result = await add_data_source(
    user_id="user123",
    project_id="project456",
    name="iris_dataset",
    source_type="url",
    source_path="https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv",
    destination="data/iris.csv",
    description="Iris flower dataset"
)
```

#### Function: `remove_data_source`

Removes a data source from the project and DVC tracking.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `destination` (str): Path to the data source in the project

#### Function: `update_data_source`

Updates a data source with new data.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `destination` (str): Path to the data source in the project
- `new_source_path` (str): New path or URL to the data source
- `source_type` (str): Type of data source (url, local, remote)

## Remote Storage Management

### Remote Storage Types

The system supports various remote storage backends:

1. **S3** - Amazon S3 storage
2. **GCS** - Google Cloud Storage
3. **Azure** - Microsoft Azure Blob Storage
4. **SSH** - SSH/SFTP storage
5. **Local** - Local file system storage

### Core Remote Storage Functions

#### Function: `add_remote_storage`

Adds a remote storage to the project.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `name` (str): Name of the remote storage
- `url` (str): URL of the remote storage
- `remote_type` (str): Type of remote storage (default, cache, etc.)

**Example:**
```python
result = await add_remote_storage(
    user_id="user123",
    project_id="project456",
    name="s3_remote",
    url="s3://my-bucket/dvc-storage",
    remote_type="default"
)
```

#### Function: `remove_remote_storage`

Removes a remote storage from the project.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `name` (str): Name of the remote storage

#### Function: `list_remote_storages`

Lists all remote storages configured in DVC.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID

**Returns:**
- `dict`: Remote storage information

## Data Operations

### Push Operations

#### Function: `push_to_remote`

Pushes data to a remote storage.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `remote_name` (str, optional): Name of the remote storage
- `target` (str, optional): Specific target to push

### Pull Operations

#### Function: `pull_from_remote`

Pulls data from a remote storage.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `remote_name` (str, optional): Name of the remote storage
- `target` (str, optional): Specific target to pull

### Sync Operations

#### Function: `sync_with_remote`

Syncs data with a remote storage.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `remote_name` (str, optional): Name of the remote storage

## API Endpoints

### Data Sources Endpoints

#### 1. Get All Data Sources

**GET** `/{user_id}/{project_id}/data/sources`

Retrieves all data sources for a project.

**Response:**
```json
{
  "data_sources": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "user_id": "user123",
      "project_id": "project456",
      "name": "iris_dataset",
      "description": "Iris flower dataset",
      "type": "url",
      "source": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv",
      "destination": "data/iris.csv",
      "size": 4567,
      "format": "csv",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "status": "completed",
      "error": null
    }
  ]
}
```

#### 2. Get Specific Data Source

**GET** `/{user_id}/{project_id}/data/source/{source_id}`

Retrieves a specific data source by ID.

#### 3. Create Data Source

**POST** `/{user_id}/{project_id}/data/source`

Creates a new data source.

**Request Body:**
```json
{
  "name": "iris_dataset",
  "description": "Iris flower dataset",
  "type": "url",
  "source": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv",
  "destination": "data/iris.csv"
}
```

**Response:**
```json
{
  "message": "Data source created successfully",
  "id": "507f1f77bcf86cd799439013",
  "dvc_result": "Data source 'iris_dataset' added successfully to data/iris.csv"
}
```

#### 4. Update Data Source

**PUT** `/{user_id}/{project_id}/data/source/{source_id}`

Updates an existing data source.

**Request Body:**
```json
{
  "name": "updated_iris_dataset",
  "description": "Updated iris dataset description",
  "status": "completed"
}
```

#### 5. Delete Data Source

**DELETE** `/{user_id}/{project_id}/data/source/{source_id}`

Deletes a data source.

### Remote Storage Endpoints

#### 1. Get All Remote Storages

**GET** `/{user_id}/{project_id}/data/remotes`

Retrieves all remote storages for a project.

**Response:**
```json
{
  "remote_storages": [
    {
      "_id": "507f1f77bcf86cd799439014",
      "user_id": "user123",
      "project_id": "project456",
      "name": "s3_remote",
      "url": "s3://my-bucket/dvc-storage",
      "type": "s3",
      "is_default": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

#### 2. Get Specific Remote Storage

**GET** `/{user_id}/{project_id}/data/remote/{remote_id}`

Retrieves a specific remote storage by ID.

#### 3. Create Remote Storage

**POST** `/{user_id}/{project_id}/data/remote`

Creates a new remote storage.

**Request Body:**
```json
{
  "name": "s3_remote",
  "url": "s3://my-bucket/dvc-storage",
  "type": "s3",
  "is_default": true
}
```

**Response:**
```json
{
  "message": "Remote storage created successfully",
  "id": "507f1f77bcf86cd799439014",
  "dvc_result": "Remote storage 's3_remote' added successfully"
}
```

#### 4. Update Remote Storage

**PUT** `/{user_id}/{project_id}/data/remote/{remote_id}`

Updates an existing remote storage.

**Request Body:**
```json
{
  "name": "updated_s3_remote",
  "url": "s3://updated-bucket/dvc-storage",
  "is_default": false
}
```

#### 5. Delete Remote Storage

**DELETE** `/{user_id}/{project_id}/data/remote/{remote_id}`

Deletes a remote storage.

### Remote Operations Endpoints

#### 1. Push to Remote

**POST** `/{user_id}/{project_id}/data/remote/{remote_id}/push`

Pushes data to a specific remote storage.

**Request Body:**
```json
{
  "target": "data/iris.csv"
}
```

#### 2. Pull from Remote

**POST** `/{user_id}/{project_id}/data/remote/{remote_id}/pull`

Pulls data from a specific remote storage.

**Request Body:**
```json
{
  "target": "data/iris.csv"
}
```

#### 3. Sync with Remote

**POST** `/{user_id}/{project_id}/data/remote/{remote_id}/sync`

Syncs data with a specific remote storage.

#### 4. List DVC Remotes

**GET** `/{user_id}/{project_id}/data/remote/list`

Lists all remote storages configured in DVC.

**Response:**
```json
{
  "remotes": {
    "s3_remote": {
      "name": "s3_remote",
      "url": "s3://my-bucket/dvc-storage",
      "type": "default"
    }
  }
}
```

## Data Models

### DataSource

```python
class DataSource(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    project_id: str
    name: str
    description: Optional[str] = None
    type: DataSourceType
    source: str  # URL, file path, or remote path
    destination: str  # Where to store in the project
    size: Optional[int] = None
    format: Optional[str] = None
    created_at: str
    updated_at: str
    status: DataSourceStatus
    error: Optional[str] = None
```

### DataSourceType

```python
class DataSourceType(str, Enum):
    URL = "url"
    LOCAL = "local"
    REMOTE = "remote"
```

### DataSourceStatus

```python
class DataSourceStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
```

### RemoteStorage

```python
class RemoteStorage(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    project_id: str
    name: str
    url: str
    type: RemoteStorageType
    is_default: bool
    created_at: str
    updated_at: str
```

### RemoteStorageType

```python
class RemoteStorageType(str, Enum):
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    SSH = "ssh"
    LOCAL = "local"
```

## Usage Examples

### Creating a Data Source from URL

```python
import requests

# Create a data source from URL
data_source_data = {
    "name": "iris_dataset",
    "description": "Iris flower dataset from GitHub",
    "type": "url",
    "source": "https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv",
    "destination": "data/iris.csv"
}

response = requests.post(
    "http://localhost:8000/user123/project456/data/source",
    json=data_source_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Data source created: {result['id']}")
```

### Setting up S3 Remote Storage

```python
# Create S3 remote storage
remote_data = {
    "name": "s3_remote",
    "url": "s3://my-bucket/dvc-storage",
    "type": "s3",
    "is_default": True
}

response = requests.post(
    "http://localhost:8000/user123/project456/data/remote",
    json=remote_data
)

if response.status_code == 200:
    result = response.json()
    remote_id = result['id']
    
    # Push data to remote
    push_data = {"target": "data/iris.csv"}
    response = requests.post(
        f"http://localhost:8000/user123/project456/data/remote/{remote_id}/push",
        json=push_data
    )
```

### Managing Local Data Sources

```python
# Create a local data source
local_source_data = {
    "name": "local_dataset",
    "description": "Dataset from local file",
    "type": "local",
    "source": "/path/to/local/file.csv",
    "destination": "data/local_file.csv"
}

response = requests.post(
    "http://localhost:8000/user123/project456/data/source",
    json=local_source_data
)
```

## Error Handling

All functions include comprehensive error handling:

1. **Project Validation** - Ensures the project exists and belongs to the user
2. **Path Validation** - Verifies project paths exist before operations
3. **Source Validation** - Validates data source URLs and file paths
4. **DVC Integration** - Handles DVC command failures gracefully
5. **Status Tracking** - Tracks operation status and provides detailed error messages

## Best Practices

1. **Use Descriptive Names** - Give meaningful names to data sources and remotes
2. **Validate Sources** - Ensure data source URLs and paths are accessible
3. **Monitor Status** - Check data source status after creation
4. **Use Default Remotes** - Set up default remote storage for convenience
5. **Regular Sync** - Sync data regularly with remote storage
6. **Error Handling** - Implement proper error handling in client applications

## Testing

Use the provided test script `test_data_sources_remotes.py` to test all functionality:

```bash
python test_data_sources_remotes.py
```

This script tests:
- Data source creation (URL, local, remote)
- Remote storage management
- Data operations (push, pull, sync)
- Error handling and validation

## Dependencies

The data sources and remote storage functionality requires:
- DVC installed and configured
- Git repository initialized
- Proper file system permissions
- Network access for URL sources
- Appropriate credentials for remote storage

## Security Considerations

1. **User Isolation** - All operations are scoped to specific users and projects
2. **Path Validation** - Prevents directory traversal attacks
3. **URL Validation** - Validates data source URLs
4. **Credential Management** - Secure handling of remote storage credentials
5. **Error Information** - Limits exposure of sensitive information in error messages 