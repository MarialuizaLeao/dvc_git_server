#!/bin/bash

echo "Running the script"

python3 -m venv dvc-rest-server/venv
source dvc-rest-server/venv/bin/activate
pip install -r dvc-rest-server/requirements.txt


python dvc-rest-server/main.py