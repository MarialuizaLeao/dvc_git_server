#!/usr/bin/env python3
"""
Script to inspect execution records in the database.
"""

import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.init_db import get_pipeline_executions_collection

async def inspect_executions():
    """Inspect execution records in the database"""
    print("🔍 Inspecting execution records...")
    
    # Get the executions collection
    executions_collection = await get_pipeline_executions_collection()
    
    # Find all executions
    executions = await executions_collection.find({}).to_list(length=None)
    
    print(f"Found {len(executions)} total executions")
    
    for i, execution in enumerate(executions):
        print(f"\n--- Execution {i+1} ---")
        print(f"ID: {execution['_id']}")
        print(f"Execution ID: {execution['execution_id']}")
        print(f"Status: {execution['status']}")
        print(f"Has logs: {bool(execution.get('logs'))}")
        print(f"Logs count: {len(execution.get('logs', []))}")
        print(f"Has execution_output: {bool(execution.get('execution_output'))}")
        print(f"execution_output is None: {execution.get('execution_output') is None}")
        
        if execution.get('logs'):
            print(f"First log: {repr(execution['logs'][0][:100])}...")
        
        if execution.get('execution_output'):
            print(f"execution_output summary: {execution['execution_output'].get('summary', 'No summary')}")
        else:
            print("execution_output: None or missing")

if __name__ == "__main__":
    asyncio.run(inspect_executions()) 