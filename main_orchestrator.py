"""
Main script to set up the environment and start the AI agent threads (-pt and -it).
"""
import os
import time
import json
import threading
import sys

# --- Add project root to path if needed ---
# Ensures modules can be found when run from root directory
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Import necessary components ---
try:
    from sim_env.grid_logic import GameEnvironment, ROWS, COLS # Import class and dimensions
    from ai_agent.learning import experience_history # Import the shared history dict
    from ai_agent.strategy_pt import planner_thread_func # Import PT logic runner
    from ai_agent.tactics_it import implementer_thread_func # Import IT logic runner
    from comms import write_json_file # Import comms utility
except ImportError as e:
     print(f"ERROR: Failed to import necessary modules: {e}")
     print("Ensure you are running this script from the 'autonomous_system' directory.")
     print(f"Current sys.path: {sys.path}")
     exit(1)


# --- Configuration ---
SHARED_DIRECTORY = "./shared_directory"
STATUS_FILE = os.path.join(SHARED_DIRECTORY, "status.json")
INSTRUCTION_FILE = os.path.join(SHARED_DIRECTORY, "instructions.json")
LOG_FILE = os.path.join(SHARED_DIRECTORY, "log.json")
PT_CYCLE_TIME_SECONDS = 10 # How often the planner analyzes/updates strategy
# IT_CYCLE_TIME_SECONDS is defined within tactics_it.py

# --- Global Shared State ---
# Create the single GameEnvironment instance that both threads will interact with
# NOTE: Direct sharing of complex objects like this between threads requires careful
# consideration of thread safety if methods modify shared state concurrently.
# Python's Global Interpreter Lock (GIL) might serialize access enough for this
# specific structure, but using Queues or Locks might be safer in complex scenarios.
game_env = GameEnvironment(rows=ROWS, cols=COLS) # Use configured dimensions

# experience_history is imported from learning.py and acts as shared memory (needs care)

# --- Main Execution ---
if __name__ == "__main__":
    print("="*50)
    print(" Starting Autonomous System Orchestrator (Optimisation Focus) ")
    print("="*50)

    # 1. Ensure shared directory exists
    try:
        os.makedirs(SHARED_DIRECTORY, exist_ok=True)
        print(f"Shared directory ensured: {os.path.abspath(SHARED_DIRECTORY)}")
    except Exception as e:
        print(f"ERROR: Could not create shared directory: {e}")
        exit(1)

    # 2. Initialize communication files (clear previous state)
    print("Initializing communication files...")
    try:
        # Initial status
        write_json_file(STATUS_FILE, {
            "timestamp": time.time(),
            "cycle": 0,
            "score": 0,
            "game_over": False,
            "dot_count": sum(row.count(6) for row in game_env.grid), # Use constant DOT=6
            "o_count": sum(row.count(7) for row in game_env.grid) # Use constant PLAYER_O=7
        })
        # Initial instructions
        write_json_file(INSTRUCTION_FILE, {
            "timestamp": time.time(),
            "goal": "Initial Survival & Exploit Language",
            "parameters": {"exploration_rate": 0.1, "use_heuristics": True},
            "guidance": "Begin operation. Apply heuristics and learn."
        })
        # Clear log file
        with open(LOG_FILE, 'w') as f:
             f.write("") # Create or clear the log file
        print(f"Communication files initialized/cleared.")
    except Exception as e:
        print(f"ERROR: Could not initialize communication files: {e}")
        exit(1)


    # 3. Create Stop Event for graceful shutdown
    stop_event = threading.Event()

    # 4. Create and Start Threads
    print("Starting AI agent threads (-pt: Planner, -it: Implementer)...")
    try:
        pt_thread = threading.Thread(target=planner_thread_func, args=(stop_event,), name="PlannerPT", daemon=True) # Make PT daemon so it exits if IT finishes
        it_thread = threading.Thread(target=implementer_thread_func, args=(stop_event,), name="ImplementerIT")

        it_thread.start() # Start implementer first (main game loop)
        time.sleep(1) # Give IT a moment to start up
        pt_thread.start() # Start planner

        # 5. Wait for Implementer Thread to Complete (runs until game over)
        print("Orchestrator running... Waiting for IT thread to finish (game over or error).")
        it_thread.join() # Wait for the game simulation loop to end

        print("\nIT thread finished. Signalling PT thread to stop...")
        stop_event.set() # Signal the planner thread to stop its loop
        pt_thread.join(timeout=PT_CYCLE_TIME_SECONDS + 2) # Wait briefly for PT to exit cleanly

        if pt_thread.is_alive():
             print("Warning: PT thread did not exit cleanly after stop signal.")

    except KeyboardInterrupt:
         print("\nKeyboardInterrupt received. Stopping threads...")
         stop_event.set() # Signal threads to stop
         it_thread.join(timeout=2)
         pt_thread.join(timeout=PT_CYCLE_TIME_SECONDS + 2)
         print("Threads stopped.")
    except Exception as e:
         print(f"\nOrchestrator encountered an error: {e}")
         stop_event.set() # Try to stop threads on error
         # Wait briefly
         if 'it_thread' in locals() and it_thread.is_alive(): it_thread.join(timeout=1)
         if 'pt_thread' in locals() and pt_thread.is_alive(): pt_thread.join(timeout=1)

    print("\nOrchestration finished.")
    final_status = comms.read_json_file(STATUS_FILE)
    print(f"Final Status: {final_status}")
