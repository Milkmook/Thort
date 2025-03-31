"""
Contains the AI agent's decision-making logic (choosing the 4-bit action).
"""
import random

def get_ai_learned_move(state_key, history, exploration_rate=0.1):
    """
    Chooses a 4-bit move based on remembered past outcomes (experience history).
    Uses epsilon-greedy exploration.
    """
    best_move = "0000" # Default move (do nothing)

    # Exploration: Try a random move sometimes
    if random.random() < exploration_rate:
        chosen_move = format(random.randint(0, 15), '04b')
        # print(f"AI explores: {chosen_move}")
        return chosen_move

    # Exploitation: Choose best known move for this state
    if state_key is not None and state_key in history:
        possible_moves = history[state_key]
        moves_scores = []
        for move, outcome in possible_moves.items():
            success = outcome['success']
            fail = outcome['fail']
            total_tries = success + fail
            if total_tries > 0:
                # Simple score: success rate
                # Could add bonus for exploration (e.g., UCB1) or use Q-values
                success_rate = success / total_tries
                moves_scores.append((success_rate, move))
            # else: # Move never tried or resulted only in fails? Handle appropriately
                 # moves_scores.append((-1.0, move)) # Assign low score if never succeeded?

        if moves_scores:
             # Choose move with highest success rate
             # Optional: Add small random factor to break ties consistently
             moves_scores.sort(key=lambda x: x[0] + random.random()*1e-6, reverse=True)
             best_move = moves_scores[0][1]
             # print(f"AI exploits: Chose {best_move} (Success Rate: {moves_scores[0][0]:.2f}) from state {hash(state_key)%1000}")
             return best_move
        # else: # State known, but no moves recorded or all failed? Explore.
             # pass # Will fall through to random exploration

    # If state is unknown or no successful history for known moves, explore
    chosen_move = format(random.randint(0, 15), '04b')
    # print(f"AI explores (unknown state or no history): {chosen_move}")
    return chosen_move

# --- Potential Future Enhancements ---
# - Implement more sophisticated RL algorithms (Q-learning, SARSA, DQN)
# - Use learned Q-values instead of simple success rates
# - Implement better tie-breaking or exploration strategies (e.g., UCB1)
