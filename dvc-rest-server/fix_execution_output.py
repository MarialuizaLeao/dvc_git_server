#!/usr/bin/env python3
"""
Script to fix existing execution records by parsing their logs and updating the execution_output field.
"""

import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from routes import parse_execution_output_and_stats
from app.init_db import get_pipeline_executions_collection

async def fix_execution_output():
    """Fix the execution_output field for existing execution records"""
    print("🔧 Fixing execution output for existing records...")
    
    # Get the executions collection
    executions_collection = await get_pipeline_executions_collection()
    
    # Find all executions that have logs but no execution_output
    executions = await executions_collection.find({
        "logs": {"$exists": True, "$ne": []},
        "$or": [
            {"execution_output": {"$exists": False}},
            {"execution_output": None}
        ]
    }).to_list(length=None)
    
    print(f"Found {len(executions)} executions to fix")
    
    for execution in executions:
        try:
            print(f"\nProcessing execution {execution['execution_id']}...")
            
            # Get the raw logs
            logs = execution.get('logs', [])
            if not logs:
                print("  No logs found, skipping")
                continue
            
            # Join the logs into a single string
            raw_output = '\n'.join(logs)
            print(f"  Raw output: {repr(raw_output[:200])}...")
            
            # Parse the output
            execution_output = await parse_execution_output_and_stats(
                execution['user_id'],
                execution['project_id'],
                raw_output,
                execution.get('parameters_used', {})
            )
            
            print(f"  Parsed summary: {execution_output['summary']}")
            
            # Update the execution record
            result = await executions_collection.update_one(
                {"_id": execution["_id"]},
                {
                    "$set": {
                        "execution_output": execution_output,
                        "output_files": execution_output["pipeline_stats"]["output_files"],
                        "models_produced": execution_output["pipeline_stats"]["models_produced"]
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Updated successfully")
            else:
                print(f"  ⚠️ No changes made")
                
        except Exception as e:
            print(f"  ❌ Error processing execution {execution['execution_id']}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Finished fixing {len(executions)} execution records")

if __name__ == "__main__":
    asyncio.run(fix_execution_output()) 