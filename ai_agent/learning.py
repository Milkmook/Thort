"""
Handles the experience history and learning updates for the AI agent.
"""

# Global dictionary to store experiences (State -> Action -> Outcome)
# In a more robust implementation, this might be part of an Agent class
experience_history = {}

def update_history(history, state_key, action_nibble, success):
    """
    Updates the experience history for a given state-action pair.
    'success' is typically defined as 'not game_over' for survival.
    """
    if state_key is None:
        # print("Warning: Cannot update history with None state_key.")
        return # Cannot update without a valid key

    if not isinstance(action_nibble, str) or len(action_nibble) != 4:
        # print(f"Warning: Invalid action '{action_nibble}' for history update.")
        return

    if state_key not in history:
        history[state_key] = {}
    if action_nibble not in history[state_key]:
        history[state_key][action_nibble] = {'success': 0, 'fail': 0}

    if success:
        history[state_key][action_nibble]['success'] += 1
    else:
        history[state_key][action_nibble]['fail'] += 1
    # print(f"Debug: Updated history for state {hash(state_key)%1000}, action {action_nibble}, success: {success}")

# --- Potential Future Enhancements ---
# - Use rewards instead of just success/fail
# - Implement forgetting old experiences or prioritizing recent ones
# - Use more sophisticated value updates (e.g., Q-learning update rule)
