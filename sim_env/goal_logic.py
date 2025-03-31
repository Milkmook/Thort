"""
Contains logic related to the game's goals, like placing 1111 blocks.
Assumes access to constants and grid structure from grid_logic.
"""
from .grid_logic import EMPTY, WALL, LANE1, LANE2, LANE3, LANE4, DOT, PLAYER_O, BLOCK_1111, LANE_VALUES

def check_and_place_1111(grid, rows, cols):
    """
    Checks conditions for placing a 1111 block and places it if possible.
    Modifies the grid directly.
    Returns True if a block was placed, False otherwise.
    """
    placed_block = False
    center_start_col = (cols // 2) - 2 # Assuming 4 lanes are centered

    # Define the condition for placing a 1111 block
    # Simple example: if there are dots in all four lanes in the same row
    for r in range(1, rows - 1): # Check rows within bounds
        lane_cols = [center_start_col + i for i in range(4)]
        # Check if columns are valid
        if not all(0 < c < cols - 1 for c in lane_cols):
             continue # Skip if lanes aren't where expected

        # Check if all those cells contain a DOT
        try: # Add try-except for safety if lane_cols indices are invalid
            if all(grid[r][c] == DOT for c in lane_cols):
                # Condition met, replace dots with BLOCK_1111
                for c in lane_cols:
                    grid[r][c] = BLOCK_1111
                print(f"INFO: Placed 1111 block in row {r}!")
                placed_block = True
                # Optional: Could return True immediately or check all rows
                # If only one block can be placed per cycle, return True here
                return True # Let's assume only one placement per cycle
        except IndexError:
             print(f"Warning: Index out of bounds checking row {r} for 1111 placement.")
             continue

    return placed_block

