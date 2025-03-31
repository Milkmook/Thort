"""
Defines functions for representing the game state for the AI agent.
"""
from sim_env.grid_logic import ROWS, COLS, DOT, PLAYER_O # Assuming constants are accessible

def get_grid_state_key(grid):
    """
    Represents the grid state as a tuple of sorted dot and O positions.
    This is a basic representation and might need refinement for better learning.
    """
    dot_positions = []
    o_positions = []
    for r in range(len(grid)): # Use len(grid) instead of global ROWS
        for c in range(len(grid[0])): # Use len(grid[0]) instead of global COLS
            if grid[r][c] == DOT:
                dot_positions.append((r, c))
            elif grid[r][c] == PLAYER_O:
                o_positions.append((r, c))

    # Return a tuple of sorted position tuples, making it hashable
    # Sorting ensures the order doesn't matter for the state key
    state_key = (tuple(sorted(dot_positions)), tuple(sorted(o_positions)))
    return state_key

# --- Potential Future Refinements ---
# def get_feature_based_state(grid):
#     """ More advanced state representation using features. """
#     features = []
#     # Example features:
#     # - Number of dots
#     # - Number of Os
#     # - Position of leading/trailing dot
#     # - For each dot: distance to nearest O downstream, siding available?
#     # - Next dot lane from pattern
#     # ... calculate features ...
#     return tuple(features) # Return a tuple of feature values
