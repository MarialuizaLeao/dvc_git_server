# DVC REST Server

A FastAPI-based REST server for managing machine learning projects with DVC integration.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```env
MONGO_DB_URL=your_mongodb_connection_string
DB_NAME=project_management
```

4. Start the server:
```bash
uvicorn main:app --reload
```

## Project Creation

The server supports creating ML projects with the following configurations:

### Project Types
- Image Classification (default)
- Object Detection
- Segmentation
- Natural Language Processing
- Time Series
- Other

### Frameworks
- PyTorch (default)
- TensorFlow
- JAX
- Scikit-learn

### Python Versions
- 3.9 (default)
- 3.10
- 3.11

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for the complete API documentation. 