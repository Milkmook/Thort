"""
Main loop/Logic for the Implementer/Tactician AI model (-it).
Runs the game simulation cycle-by-cycle, makes decisions, learns.
"""
import time
import json
import os
from sim_env.grid_logic import GameEnvironment # Assuming GameEnvironment is here
from ai_agent.state import get_grid_state_key
from ai_agent.learning import experience_history, update_history # Use shared history for now
from ai_agent.decision import get_ai_learned_move
from comms import read_json_file, write_json_file, log_action # Assuming comms.py is in root

SHARED_DIRECTORY = "./shared_directory" # Define centrally?
STATUS_FILE = os.path.join(SHARED_DIRECTORY, "status.json")
LOG_FILE = os.path.join(SHARED_DIRECTORY, "log.json")
INSTRUCTION_FILE = os.path.join(SHARED_DIRECTORY, "instructions.json")

# Global or passed-in experience history
# experience_history = {} # Defined in learning.py

def run_implementer_loop(game_env: GameEnvironment, history: Dict):
    """Runs the main tactical loop for the -it agent."""
    print("IT: Implementer loop starting...")
    while not game_env.game_over:
        game_env.cycle += 1
        # print(f"\n--- IT Cycle {game_env.cycle} ---") # Verbose print

        # 1. Read Instructions from PT
        instructions = {}
        try:
            instructions = read_json_file(INSTRUCTION_FILE)
            # print(f"IT: Received instructions: {instructions.get('guidance', 'None')}")
        except FileNotFoundError:
            # print("IT: Instructions file not found, using defaults.")
            pass # Use default behavior if no instructions
        except json.JSONDecodeError:
             print("IT: Error reading instructions file.")

        # Extract parameters from instructions (e.g., exploration rate)
        current_exploration_rate = instructions.get("parameters", {}).get("exploration_rate", 0.1)

        # 2. Get Current State
        current_state_key = get_grid_state_key(game_env.grid)

        # 3. Choose Action (using learned experience + PT guidance potentially)
        # TODO: Modify get_ai_learned_move to incorporate PT guidance if needed
        action_nibble = get_ai_learned_move(current_state_key, history, current_exploration_rate)
        # print(f"IT: Chose action {action_nibble}")

        # --- Store state *before* action for learning ---
        state_before_action = current_state_key

        # 4. Execute Step in Environment
        # The step function encapsulates placing Os, moving Os, moving dots, checking goal
        # We need to refactor GameEnvironment to have a proper step function
        # For now, call the individual methods as in the previous main loop example

        # 4a. Place Os based on chosen action
        game_env.place_os(action_nibble) # Assuming place_os is now method of game_env

        # 4b. Move Os
        score_delta_o = game_env.move_os() # Assuming move_os is method
        game_env.score += score_delta_o

        # 4c. Move Dots & Check Traps
        dot_trapped = game_env.move_dots() # Assuming move_dots is method
        if dot_trapped:
            game_env.score -= 1 # Apply penalty
            game_env.game_over = True # Set game over flag

        # 4d. Generate New Dot
        game_env.generate_dot_pattern() # Assuming generate_dot_pattern is method

        # 4e. Check & Place 1111 Goal
        if game_env.check_and_place_1111(): # Assuming check_and_place_1111 is method
            game_env.score += 5 # Apply reward

        # --- Learning Step ---
        # 5. Update Experience History
        success_this_cycle = not dot_trapped # Survival is success
        update_history(history, state_before_action, action_nibble, success_this_cycle)

        # --- Reporting ---
        # 6. Log Cycle Data
        log_entry = {
             "cycle": game_env.cycle,
             "state_key_hash": hash(state_before_action) % 10000, # Log hash for brevity
             "action": action_nibble,
             "reward": score_delta_o + (5 if 'Placed 1111' in str(game_env.grid) else 0) - (1 if dot_trapped else 0), # Approximate reward
             "success": success_this_cycle,
             "score": game_env.score,
             "game_over": game_env.game_over
             # Add more detailed state info if needed
        }
        log_action(log_entry, LOG_FILE) # Use comms function

        # 7. Update Status File
        status_data = {
            "cycle": game_env.cycle,
            "score": game_env.score,
            "game_over": game_env.game_over,
            "dot_count": sum(row.count(DOT) for row in game_env.grid),
            "o_count": sum(row.count(PLAYER_O) for row in game_env.grid)
        }
        write_json_file(STATUS_FILE, status_data) # Use comms function

        # --- Visualization & Timing ---
        if game_env.cycle % 5 == 0 or game_env.game_over: # Print less often
            print(f"\n--- IT Cycle {game_env.cycle} ---")
            print(f"Score: {game_env.score}")
            game_env.print_grid()
            print(f"IT Action: {action_nibble}")

        if not game_env.game_over:
             time.sleep(0.1) # Faster simulation speed
        else:
             print("IT: Game Over detected.")
             break

    print("IT: Implementer loop finished.")


# --- Refactoring Needed ---
# The GameEnvironment class needs methods like step(), place_os(), move_os(), etc.
# The main orchestrator needs to create the GameEnvironment instance and pass it.
# The experience_history needs proper handling (global vs passed).
