"""
Utility functions for reading/writing JSON files for inter-process communication
and logging actions.
"""
import json
import os
import time
from typing import Dict, Any, Optional, List

def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Reads data from a JSON file."""
    try:
        # Ensure file exists before trying to open
        if not os.path.exists(file_path):
             # print(f"Debug: File not found {file_path}")
             return None # Return None if file doesn't exist yet
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        # print(f"Warning: File not found {file_path}") # Already checked above, but good practice
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}. File might be empty or corrupt.")
        # Optional: Handle empty file case gracefully
        if os.path.getsize(file_path) == 0:
             print(f"Debug: File {file_path} is empty.")
             return {} # Return empty dict for empty file? Or None? Depends on desired logic.
        return None # Return None on decode error
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json_file(file_path: str, data: Dict[str, Any]):
    """Writes data to a JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4) # Use indent for readability
    except Exception as e:
        print(f"Error writing JSON file {file_path}: {e}")

def log_action(action_data: Dict[str, Any], file_path: str):
    """Appends an action (dictionary) as a JSON line to a log file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Add timestamp if not present
        if "timestamp" not in action_data:
             action_data["timestamp"] = time.time()

        with open(file_path, 'a') as file:
            json.dump(action_data, file)
            file.write("\n") # Write each entry as a new line (JSON Lines format)
    except Exception as e:
        print(f"Error logging action to {file_path}: {e}")
