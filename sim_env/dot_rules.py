"""
Contains logic for dot generation and movement.
Assumes access to constants and grid structure from grid_logic.
"""
import random
from .grid_logic import EMPTY, WALL, LANE1, LANE2, LANE3, LANE4, DOT, PLAYER_O, BLOCK_1111, LANE_VALUES

def get_valid_neighbors(r, c, grid, rows, cols):
    """Gets coordinates of valid adjacent cells (up, down, left, right)."""
    # Note: This duplicates the one in grid_logic, ideally structure better
    #       e.g., pass grid dimensions or make it a method of GameEnvironment
    neighbors = []
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # Right, Left, Down, Up
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append((nr, nc))
    return neighbors

def move_dots(grid, rows, cols):
    """
    Moves all dots according to the rules.
    Dots MUST move each cycle by swapping with an adjacent LANE (2-5) or EMPTY (0).
    They cannot move into WALL (1), PLAYER_O (7), other DOT (6), or BLOCK_1111 (8).
    Returns True if any dot is trapped, False otherwise.
    Modifies the grid directly.
    """
    dots_to_move = []
    # Find all dots first
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == DOT:
                dots_to_move.append((r, c))

    if not dots_to_move:
        return False # No dots to move

    trapped_this_cycle = False
    moved_dots_coords = set(dots_to_move) # Track original positions
    new_dot_positions = {} # Store new positions: new_coord -> original_coord

    random.shuffle(dots_to_move) # Move in random order to avoid bias

    for r, c in dots_to_move:
        valid_swap_locations = []
        neighbors = get_valid_neighbors(r, c, grid, rows, cols)

        for nr, nc in neighbors:
            target_cell = grid[nr][nc]
            # Check if target is a swappable location AND not occupied by a dot that hasn't moved yet
            # or a dot that already moved into it this cycle
            if (target_cell in LANE_VALUES or target_cell == EMPTY) and \
               (nr, nc) not in moved_dots_coords and \
               (nr, nc) not in new_dot_positions:
                valid_swap_locations.append((nr, nc))

        if not valid_swap_locations:
            print(f"INFO: Dot at ({r},{c}) is trapped!")
            trapped_this_cycle = True
            # Keep dot in place if trapped, penalty handled elsewhere
            new_dot_positions[(r,c)] = (r,c) # Mark as processed, staying put
        else:
            # --- Movement Strategy ---
            # Simple strategy: prioritize moving down, then random among remaining.
            down_moves = [(nr, nc) for nr, nc in valid_swap_locations if nr > r]
            if down_moves:
                 move_to_r, move_to_c = random.choice(down_moves)
            else:
                 move_to_r, move_to_c = random.choice(valid_swap_locations)

            # Store the move: new position maps to original position
            new_dot_positions[(move_to_r, move_to_c)] = (r, c)

    # --- Update grid based on moves ---
    # Create a temporary grid to avoid conflicts during update
    next_grid_state = [row[:] for row in grid]

    # Clear old dot positions (that actually moved)
    for r, c in dots_to_move:
         is_staying_put = new_dot_positions.get((r,c)) == (r,c)
         if not is_staying_put:
             # Find what the original cell value was at the destination
             # (where the dot moved FROM in the original grid)
             original_dest_value = grid[r][c] # This is the DOT
             # Find the cell value the dot is moving TO in the original grid
             # This requires finding which new_pos corresponds to original (r,c)
             original_target_value = EMPTY # Default assumption
             for new_pos, orig_pos in new_dot_positions.items():
                 if orig_pos == (r,c) and new_pos != (r,c):
                     original_target_value = grid[new_pos[0]][new_pos[1]]
                     break
             next_grid_state[r][c] = original_target_value # Restore original value

    # Place dots in new positions
    for (nr, nc), (orig_r, orig_c) in new_dot_positions.items():
        next_grid_state[nr][nc] = DOT

    # Copy changes back to the main grid
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = next_grid_state[r][c]


    return trapped_this_cycle

def generate_dot_pattern(grid, cycle, lane_start_coords, dot_lane_pattern, pattern_length, rows, cols):
    """
    Generates a dot at the start based on the repeating pattern.
    Modifies the grid directly.
    """
    if not lane_start_coords: # Ensure coords were found
        # print("Warning: Lane start coordinates not available for dot generation.")
        return

    # Determine which step in the pattern we are on
    # Use cycle number directly (assuming cycle starts at 1 for first real step)
    if cycle <= 0: return # Don't generate on cycle 0 or before

    pattern_index = (cycle - 1) % pattern_length # cycle 1 -> index 0
    target_lane_number = dot_lane_pattern[pattern_index]

    # Get the coordinate for that lane's start
    target_pos = lane_start_coords.get(target_lane_number)

    if target_pos:
        target_r, target_c = target_pos
        # Check bounds just in case
        if 0 <= target_r < rows and 0 <= target_c < cols:
            # Check if the target start position is currently a lane marker (clear to place dot)
            if grid[target_r][target_c] in LANE_VALUES:
                grid[target_r][target_c] = DOT
                # print(f"Debug: Cycle {cycle} placed dot in Lane {target_lane_number} at {target_pos}")
            # else:
                # print(f"Debug: Cycle {cycle} start for Lane {target_lane_number} blocked by {grid[target_r][target_c]}")
        # else:
             # print(f"Debug: Cycle {cycle} target position {target_pos} out of bounds.")
    # else:
         # print(f"Debug: Cycle {cycle} could not find start coordinate for lane {target_lane_number}.")
         pass # Error should have been caught earlier
