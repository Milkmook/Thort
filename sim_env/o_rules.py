"""
Contains logic for placing player 'O' barriers and moving them along paths.
Assumes access to constants and grid structure from grid_logic.
"""
from .grid_logic import EMPTY, WALL, LANE1, LANE2, LANE3, LANE4, DOT, PLAYER_O, BLOCK_1111, LANE_VALUES, LANE_MAP

def place_os(grid, input_nibble_str, lane_starts, rows, cols):
    """
    Places 'O's based on the 4-bit input string (e.g., '1011') at lane starts.
    Modifies the grid directly.
    """
    if not isinstance(input_nibble_str, str) or len(input_nibble_str) != 4:
        print(f"Error: Invalid input nibble '{input_nibble_str}'. Must be 4 bits string.")
        return

    for i in range(4):
        if input_nibble_str[i] == '1':
            lane_number = i + 1 # Lane 1 to 4
            internal_lane_val = LANE_MAP.get(lane_number)
            if internal_lane_val:
                start_pos = lane_starts.get(internal_lane_val)
                if start_pos:
                    start_r, start_c = start_pos
                    # Check bounds and if the start position is clear (a lane marker)
                    if 0 <= start_r < rows and 0 <= start_c < cols:
                        if grid[start_r][start_c] in LANE_VALUES:
                            grid[start_r][start_c] = PLAYER_O
                        # else: # Optional warning if blocked
                        #     print(f"Warning: Cannot place O in Lane {lane_number}, start pos {start_pos} blocked by {grid[start_r][start_c]}.")
                    # else: # Optional warning if start pos invalid
                    #      print(f"Warning: Start position {start_pos} for Lane {lane_number} is out of bounds.")
                # else: # Optional warning if start pos not found
                    # print(f"Warning: Start coordinate for Lane {lane_number} not defined in lane_starts.")
            # else: # Optional warning if lane mapping failed
                # print(f"Warning: Internal lane value for Lane {lane_number} not found.")

def move_os(grid, lane_paths, rows, cols):
    """
    Moves all Player 'O's one step along their predefined paths.
    Restores the original lane value to the cell they leave.
    Removes 'O' and returns score change if end of path is reached.
    Modifies the grid directly.
    Returns the total score change from Os reaching the end this cycle.
    """
    os_to_move = []
    score_change = 0
    # Find all Os and determine their lane value by looking up their position in paths
    o_positions_lanes = {} # Store { (r, c): lane_val }
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == PLAYER_O:
                found_lane = None
                for lane_val, path in lane_paths.items():
                    if (r, c) in path:
                        found_lane = lane_val
                        break
                if found_lane is not None:
                    os_to_move.append((r, c))
                    o_positions_lanes[(r,c)] = found_lane
                # else:
                    # Optional: Handle case where an O is somehow not on a defined path
                    # print(f"Warning: Player O at ({r},{c}) is not on any known lane path!")
                    # grid[r][c] = EMPTY # Remove orphan O?

    if not os_to_move:
        return 0

    # Use a copy to manage moves happening "simultaneously"
    new_grid = [row[:] for row in grid]

    for r, c in os_to_move:
        lane_val = o_positions_lanes.get((r, c))
        if not lane_val: continue # Should not happen if logic above is correct

        path = lane_paths[lane_val]
        try:
            current_index = path.index((r, c))
        except ValueError:
             # Should not happen if O was found correctly
             print(f"Error: O at ({r},{c}) claims to be Lane {lane_val} but not found in path.")
             continue

        if current_index + 1 < len(path):
            # Move to next step in the path
            nr, nc = path[current_index + 1]
            # Check if the next step is valid (not Wall, not another O, not a Dot?)
            # Current rule: Os can overwrite lane markers only? Let's assume they can move if next step is lane or empty
            # Let's also assume Os *block* dots but don't get blocked *by* dots
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != WALL and grid[nr][nc] != PLAYER_O:
                new_grid[nr][nc] = PLAYER_O # Move O to new position
                new_grid[r][c] = lane_val   # Restore original lane value
                # print(f"Debug: Moved O from ({r},{c}) to ({nr},{nc}), restored {lane_val}")
            else:
                # Cannot move, blocked or invalid path step - O stays put on new_grid
                new_grid[r][c] = PLAYER_O
                # print(f"Debug: O at ({r},{c}) blocked from moving to ({nr},{nc}) by {grid[nr][nc]}")

        else:
            # Reached the end of the defined path
            score_change += 1
            new_grid[r][c] = lane_val # Restore final path cell to lane value
            # print(f"Debug: O from Lane {lane_val} reached end at ({r},{c}). Score +1!")

    # Update the original grid
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = new_grid[r][c]

    return score_change
