#!/bin/bash

curl -X POST "http://127.0.0.1:8000/project/create" \
     -H "Content-Type: application/json" \
     -d '{"username": "user123", "project_name": "my-project"}'
