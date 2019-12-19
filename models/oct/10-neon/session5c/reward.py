"""
AWS DeepRacer reward function using sparse rewards
"""
# CONSTANTS
CHECKPOINT_DISTANCE = 10  # progress point at which we return a reward
TARGET_STEPS = 100        # budget of steps we want to complete the course

# Globals
g_last_checkpoint_progress = 0.0
g_last_checkpoint_steps = 0

#===============================================================================
#
# REWARD
#
#
# Things that don't work:
#
#  progress_delta / time_delta => leads to exponential rewards as car goes faster
#  progress_delta / progress_total => increased rewards for longer episodes
#
#  progress_delta + 
#===============================================================================

def reward_function(params):
    # Progress range:  0..100
    # Step is roughly a 1/15s timeslice so can account for time-factor
    # Expected real value: [0,~1.0]
    global g_last_checkpoint_progress
    global g_last_checkpoint_steps

    # Simple reward for outlier case of first step in the episode
    if params['steps'] == 0:
        reward = 1e-3
        g_last_checkpoint_progress = 0
        g_last_checkpoint_steps = 0
    elif params['progress'] // CHECKPOINT_DISTANCE != g_last_checkpoint_progress // CHECKPOINT_DISTANCE:
        # passed a checkpoint
        budget_checkpoint_steps = TARGET_STEPS / CHECKPOINT_DISTANCE
        elapsed_checkpoint_steps = (params['steps'] - g_last_checkpoint_steps)
        reward = budget_checkpoint_steps / (params['steps'] - g_last_checkpoint_steps)
        print(params['steps'], g_last_checkpoint_steps, budget_checkpoint_steps, elapsed_checkpoint_steps, reward)
        g_last_checkpoint_progress = params['progress']
        g_last_checkpoint_steps = params['steps']
    else:
        # for incremental progress
        reward = 1e-3
    return reward
