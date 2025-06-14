# Code Upload and Management Documentation

This document describes the code upload and management functionality that has been implemented in the DVC REST server. This feature provides comprehensive code file management capabilities for DVC projects, including both API and web interface uploads.

## Overview

The code upload functionality provides the following capabilities:

1. **Single File Upload** - Upload individual code files via API or web interface
2. **Multiple Files Upload** - Bulk upload multiple files at once
3. **File Management** - Create, read, update, and delete code files
4. **File Content Management** - View and edit file contents
5. **Git Integration** - Automatic Git commits for all file operations
6. **File Type Detection** - Automatic detection of file types based on extensions
7. **Project Scanning** - Scan project directories for existing code files

## Code File Types

The system supports various code file types:

1. **Python** - `.py` files
2. **Jupyter Notebooks** - `.ipynb` files
3. **Configuration** - `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg` files
4. **Documentation** - `.md`, `.txt`, `.rst` files
5. **Other** - Any other file types

## Core Functions

### Function: `add_code_file`

Adds a code file to the project and tracks it with Git.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `filename` (str): Name of the file
- `file_path` (str): Path within the project (e.g., "src/main.py")
- `content` (str): File content as string
- `file_type` (str): Type of file (python, jupyter, config, etc.)
- `description` (str, optional): Description of the file

**Example:**
```python
result = await add_code_file(
    user_id="user123",
    project_id="project456",
    filename="main.py",
    file_path="src/main.py",
    content="print('Hello, World!')",
    file_type="python",
    description="Main application file"
)
```

### Function: `update_code_file`

Updates an existing code file with new content.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `file_path` (str): Path to the file within the project
- `content` (str): New file content
- `description` (str, optional): Description of the update

### Function: `remove_code_file`

Removes a code file from the project and Git tracking.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `file_path` (str): Path to the file within the project

### Function: `get_code_file_content`

Gets the content of a code file.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `file_path` (str): Path to the file within the project

### Function: `list_code_files`

Lists code files in the project with optional filtering.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `file_type` (str, optional): Filter by file type
- `path_pattern` (str, optional): Filter by path pattern

### Function: `bulk_upload_code_files`

Uploads multiple code files at once.

**Parameters:**
- `user_id` (str): The user ID
- `project_id` (str): The project ID
- `files` (list): List of file dictionaries with filename, file_path, content, etc.

## API Endpoints

### 1. Get All Code Files

**GET** `/api/{user_id}/{project_id}/code/files`

Retrieves all code files for a project with optional filtering.

**Query Parameters:**
- `file_type` (optional): Filter by file type
- `path_pattern` (optional): Filter by path pattern

**Response:**
```json
{
  "code_files": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "user_id": "user123",
      "project_id": "project456",
      "filename": "main.py",
      "file_path": "src/main.py",
      "file_type": "python",
      "description": "Main application file",
      "size": 1024,
      "content_hash": "abc123...",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "status": "completed",
      "error": null,
      "git_commit_hash": "abc123def456..."
    }
  ],
  "total_count": 1
}
```

### 2. Get Specific Code File

**GET** `/api/{user_id}/{project_id}/code/file/{file_id}`

Retrieves a specific code file by ID.

### 3. Get File Content

**GET** `/api/{user_id}/{project_id}/code/file/{file_id}/content`

Retrieves the content of a specific code file.

**Response:**
```json
{
  "file_id": "507f1f77bcf86cd799439013",
  "file_path": "src/main.py",
  "filename": "main.py",
  "content": "print('Hello, World!')"
}
```

### 4. Create Code File

**POST** `/api/{user_id}/{project_id}/code/file`

Creates a new code file.

**Request Body:**
```json
{
  "filename": "main.py",
  "file_path": "src/main.py",
  "file_type": "python",
  "description": "Main application file",
  "content": "print('Hello, World!')"
}
```

**Response:**
```json
{
  "message": "Code file created successfully",
  "file_id": "507f1f77bcf86cd799439013",
  "file_path": "src/main.py",
  "git_commit_hash": "abc123def456..."
}
```

### 5. Update Code File

**PUT** `/api/{user_id}/{project_id}/code/file/{file_id}`

Updates an existing code file.

**Request Body:**
```json
{
  "filename": "updated_main.py",
  "file_path": "src/main.py",
  "description": "Updated main file",
  "content": "print('Updated Hello, World!')"
}
```

### 6. Delete Code File

**DELETE** `/api/{user_id}/{project_id}/code/file/{file_id}`

Deletes a code file.

### 7. Bulk Upload

**POST** `/api/{user_id}/{project_id}/code/files/bulk`

Uploads multiple code files at once.

**Request Body:**
```json
{
  "files": [
    {
      "filename": "utils.py",
      "file_path": "src/utils.py",
      "file_type": "python",
      "description": "Utility functions",
      "content": "def helper(): pass"
    },
    {
      "filename": "config.yaml",
      "file_path": "config/config.yaml",
      "file_type": "config",
      "description": "Configuration file",
      "content": "project:\n  name: test"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Bulk upload completed: 2 successful, 0 failed",
  "results": [
    {
      "filename": "utils.py",
      "status": "success",
      "result": {
        "file_path": "src/utils.py",
        "size": 1024,
        "content_hash": "abc123...",
        "git_commit_hash": "abc123def456..."
      }
    }
  ],
  "successful_uploads": 2,
  "failed_uploads": 0
}
```

### 8. Scan Code Files

**GET** `/api/{user_id}/{project_id}/code/files/scan`

Scans the project directory for code files.

**Query Parameters:**
- `file_type` (optional): Filter by file type
- `path_pattern` (optional): Filter by path pattern

### 9. Web Upload (Single File)

**POST** `/api/{user_id}/{project_id}/code/upload`

Uploads a code file via web interface (multipart form data).

**Form Data:**
- `file`: The file to upload
- `file_path`: Path within the project
- `file_type`: Type of file (default: "python")
- `description`: Description (optional)

### 10. Web Upload (Multiple Files)

**POST** `/api/{user_id}/{project_id}/code/upload/multiple`

Uploads multiple code files via web interface.

**Form Data:**
- `files`: Multiple files to upload
- `base_path`: Base path for files (default: "src")

## Frontend Integration

### React Component

The frontend includes a comprehensive React component (`CodeUpload.tsx`) that provides:

1. **Tabbed Interface** - Single file, multiple files, API upload, and file viewing
2. **Form Validation** - Client-side validation for all inputs
3. **File Type Detection** - Automatic detection based on file extensions
4. **Progress Feedback** - Loading states and success/error messages
5. **File Management** - View, edit, and delete existing files

### Usage in React

```tsx
import CodeUpload from './components/CodeUpload';

function App() {
  return (
    <div className="App">
      <CodeUpload />
    </div>
  );
}
```

## Data Models

### CodeFile

```typescript
interface CodeFile {
  id: string;
  user_id: string;
  project_id: string;
  filename: string;
  file_path: string;
  file_type: CodeFileType;
  description?: string;
  size?: number;
  content_hash?: string;
  created_at: string;
  updated_at: string;
  status: CodeFileStatus;
  error?: string;
  git_commit_hash?: string;
}
```

### CodeFileType

```typescript
enum CodeFileType {
  PYTHON = "python",
  JUPYTER = "jupyter",
  CONFIG = "config",
  DOCUMENTATION = "documentation",
  OTHER = "other"
}
```

### CodeFileStatus

```typescript
enum CodeFileStatus {
  PENDING = "pending",
  UPLOADING = "uploading",
  COMPLETED = "completed",
  FAILED = "failed"
}
```

## Usage Examples

### Creating a Code File via API

```python
import requests

# Create a code file
code_file_data = {
    "filename": "main.py",
    "file_path": "src/main.py",
    "file_type": "python",
    "description": "Main application file",
    "content": "print('Hello, World!')"
}

response = requests.post(
    "http://localhost:8000/api/user123/project456/code/file",
    json=code_file_data
)

if response.status_code == 200:
    result = response.json()
    print(f"File created: {result['file_id']}")
```

### Uploading Files via Web Interface

```javascript
// Single file upload
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('file_path', 'src/main.py');
formData.append('file_type', 'python');
formData.append('description', 'Main application file');

fetch('/api/user123/project456/code/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => console.log('Upload successful:', result));

// Multiple files upload
const formData = new FormData();
for (const file of fileInput.files) {
    formData.append('files', file);
}
formData.append('base_path', 'src');

fetch('/api/user123/project456/code/upload/multiple', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => console.log('Bulk upload result:', result));
```

### Managing Existing Files

```python
# Get all code files
response = requests.get("http://localhost:8000/api/user123/project456/code/files")
files = response.json()['code_files']

# Get specific file content
response = requests.get("http://localhost:8000/api/user123/project456/code/file/file_id/content")
content = response.json()['content']

# Update file
update_data = {
    "content": "print('Updated content')",
    "description": "Updated description"
}

response = requests.put(
    "http://localhost:8000/api/user123/project456/code/file/file_id",
    json=update_data
)

# Delete file
response = requests.delete("http://localhost:8000/api/user123/project456/code/file/file_id")
```

## Error Handling

All functions include comprehensive error handling:

1. **Project Validation** - Ensures the project exists and belongs to the user
2. **Path Validation** - Verifies project paths exist before operations
3. **File Validation** - Validates file types and content
4. **Git Integration** - Handles Git command failures gracefully
5. **Status Tracking** - Tracks operation status and provides detailed error messages
6. **Content Validation** - Validates file content encoding and size

## Best Practices

1. **Use Descriptive Names** - Give meaningful names to files and paths
2. **Organize File Structure** - Use consistent directory structures (src/, config/, etc.)
3. **Include Descriptions** - Add descriptions to help with file management
4. **Monitor Status** - Check file status after upload operations
5. **Use Appropriate File Types** - Select the correct file type for better organization
6. **Regular Backups** - All changes are automatically committed to Git
7. **Content Validation** - Validate file content before upload

## Testing

Use the provided test script `test_code_upload.py` to test all functionality:

```bash
python test_code_upload.py
```

This script tests:
- Code file creation (API and web interface)
- File content management
- Bulk upload operations
- File scanning and listing
- Error handling and validation

## Dependencies

The code upload functionality requires:
- DVC installed and configured
- Git repository initialized
- Proper file system permissions
- FastAPI with CORS support
- Frontend framework (React/Vue) for web interface

## Security Considerations

1. **User Isolation** - All operations are scoped to specific users and projects
2. **Path Validation** - Prevents directory traversal attacks
3. **File Type Validation** - Validates file types and extensions
4. **Content Validation** - Validates file content and size limits
5. **Error Information** - Limits exposure of sensitive information in error messages
6. **CORS Configuration** - Properly configured for frontend integration

## Integration with DVC

The code upload functionality integrates seamlessly with DVC:

1. **Git Tracking** - All file operations are automatically committed to Git
2. **DVC Pipeline Integration** - Uploaded files can be referenced in DVC pipelines
3. **Version Control** - Full version history is maintained through Git
4. **Collaboration** - Multiple users can work on the same project
5. **Backup** - All changes are automatically backed up through Git

## Performance Considerations

1. **File Size Limits** - Consider implementing file size limits for large files
2. **Bulk Operations** - Use bulk upload for multiple files to reduce API calls
3. **Caching** - Consider caching file content for frequently accessed files
4. **Async Operations** - All operations are asynchronous for better performance
5. **Error Recovery** - Implement retry mechanisms for failed operations 