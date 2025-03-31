"""
Defines the GameEnvironment class, constants, and basic grid setup/utility functions.
"""
import random

# --- Constants ---
EMPTY = 0  # Represents safe sidings
WALL = 1
LANE1 = 2
LANE2 = 3
LANE3 = 4
LANE4 = 5
DOT = 6    # Using numbers for easier type checking internally
PLAYER_O = 7
BLOCK_1111 = 8 # Represents the placed goal block

LANE_MAP = {1: LANE1, 2: LANE2, 3: LANE3, 4: LANE4}
LANE_VALUES = {LANE1, LANE2, LANE3, LANE4}

# Default Grid dimensions (can be overridden)
DEFAULT_ROWS = 10
DEFAULT_COLS = 10

class GameEnvironment:
    """
    Manages the state and rules of the 'dot circulation' game simulation.
    """
    def __init__(self, rows=DEFAULT_ROWS, cols=DEFAULT_COLS):
        self.rows = rows
        self.cols = cols
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.lane_starts = {} # Populated by initialize_grid
        self.lane_paths = {LANE1: [], LANE2: [], LANE3: [], LANE4: []} # Populated by initialize_grid
        self.lane_start_coords = {} # Populated by initialize_grid
        self.dot_lane_pattern = [2, 3, 4, 3, 2, 1, 2] # Lane number (1-4)
        self.pattern_length = len(self.dot_lane_pattern)
        self.score = 0
        self.cycle = 0
        self.game_over = False
        self.initialize_grid()
        # Note: C library loading is removed from here, should be handled by orchestrator if needed

    def initialize_grid(self):
        """Sets up the initial grid layout with walls, lanes, and sidings."""
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.lane_starts = {}
        self.lane_paths = {LANE1: [], LANE2: [], LANE3: [], LANE4: []}
        self.lane_start_coords = {}
        self.score = 0
        self.cycle = 0
        self.game_over = False

        # Draw walls
        for r in range(self.rows):
            if 0 <= r < self.rows:
                 if 0 < self.cols: self.grid[r][0] = WALL
                 if self.cols - 1 >= 0: self.grid[r][self.cols-1] = WALL
            if r == 0 or r == self.rows - 1:
                for c in range(self.cols):
                     if 0 <= c < self.cols: self.grid[r][c] = WALL

        # Draw lanes (example: 4 lanes centered, straight down)
        # Modify this for more complex, pre-made maps based on hardware layout idea
        center_start_col = (self.cols // 2) - 2
        for r in range(1, self.rows - 1):
            for i in range(4): # 4 lanes
                lane_number = i + 1
                lane_val = LANE_MAP[lane_number]
                c = center_start_col + i
                if 0 < c < self.cols - 1: # Ensure lane is within walls
                    self.grid[r][c] = lane_val
                    self.lane_paths[lane_val].append((r, c))
                    if r == 1:
                        self.lane_starts[lane_val] = (r, c)
                        self.lane_start_coords[lane_number] = (r, c)

        # Add sidings (example)
        siding_col_left = center_start_col - 1
        siding_col_right = center_start_col + 4
        for r in range(3, self.rows - 3): # Example row range
             if 0 < siding_col_left < self.cols -1:
                 self.grid[r][siding_col_left] = EMPTY
             if 0 < siding_col_right < self.cols -1:
                  self.grid[r][siding_col_right] = EMPTY

        if len(self.lane_start_coords) != 4:
            print(f"ERROR: Could not determine start coordinates for all 4 lanes! Found: {self.lane_start_coords}")
            # Handle error appropriately, maybe raise exception

        # Place initial dots (optional, example)
        # start_lane2 = self.lane_start_coords.get(2)
        # if start_lane2 and self.rows > 5:
        #     self.grid[5][start_lane2[1]] = DOT

    def reset(self):
        """Resets the game to its initial state."""
        self.__init__(self.rows, self.cols) # Re-initialize

    def get_valid_neighbors(self, r, c):
        """Gets coordinates of valid adjacent cells (up, down, left, right)."""
        neighbors = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # Right, Left, Down, Up
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def print_grid(self):
        """Prints the current grid state to the console."""
        symbols = {
            EMPTY: ' . ', WALL: '███', LANE1: ' 1 ', LANE2: ' 2 ',
            LANE3: ' 3 ', LANE4: ' 4 ', DOT: ' ● ', PLAYER_O: ' O ',
            BLOCK_1111: ' ■ ' # Using a block for 1111 visually
        }
        print("-" * (self.cols * 3 + 2)) # Top border
        for r in range(self.rows):
            row_str = "|" + "".join(symbols.get(self.grid[r][c], ' ? ') for c in range(self.cols)) + "|"
            print(row_str)
        print("-" * (self.cols * 3 + 2)) # Bottom border

    # --- Methods for dot movement, O placement/movement, goal checking ---
    # --- will be imported from other files or defined here ---
    # Example placeholder if not importing:
    # def move_dots(self): pass
    # def generate_dot_pattern(self): pass
    # def place_os(self, input_nibble_str): pass
    # def move_os(self): pass
    # def check_and_place_1111(self): pass
    # def step(self, action): pass # Main step function
