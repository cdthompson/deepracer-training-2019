"""
AWS DeepRacer reward function using sparse rewards
"""
# CONSTANTS
TARGET_STEPS = 100        # budget of steps we want to complete the course
NEON_PROGRESS_CHECKPOINTS = [
    0,
    10,
    20,
    32,
    40,
    50,
    63,
    73,
    83,
    91,
    100,
    10000
]

#PROGRESS_CHECKPOINTS = [  # Hand-picked checkpoints along the Canada Training track since
#                          # the curvature of the track can skew the checkpoint line and
#                          # cause the car to hunt a bad line
#    0,  # we don't hand out a reward at zero, just here for algorithms
#    6,
#    18,
#    25,
#    33,
#    45,
#    57.5,
#    68,
#    76,
#    87,
#    100,
#    10000
#]
# Use this if the start point has shifted by -4%
PROGRESS_CHECKPOINTS_SHIFTED = [
    0,
    14,
    24,
    36,
    44,
    54,
    67,
    77,
    87,
    95,
    100,
    10000
]

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

def checkpoint_for_progress(progress):
    for i in range(len(PROGRESS_CHECKPOINTS_SHIFTED)):
        if PROGRESS_CHECKPOINTS_SHIFTED[i] > progress:
            return i-1
    return -1

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
    else:
        previous_checkpoint_index = checkpoint_for_progress(g_last_checkpoint_progress)
        current_checkpoint_index = checkpoint_for_progress(params['progress'])
        if previous_checkpoint_index < current_checkpoint_index:
            # passed a checkpoint
            budget_checkpoint_steps = (TARGET_STEPS / 100.0) * (PROGRESS_CHECKPOINTS_SHIFTED[current_checkpoint_index] - PROGRESS_CHECKPOINTS_SHIFTED[previous_checkpoint_index])
            elapsed_checkpoint_steps = (params['steps'] - g_last_checkpoint_steps)
            reward = budget_checkpoint_steps / (params['steps'] - g_last_checkpoint_steps)
            print(params['steps'], g_last_checkpoint_steps, budget_checkpoint_steps, elapsed_checkpoint_steps, reward)
            g_last_checkpoint_progress = params['progress']
            g_last_checkpoint_steps = params['steps']
        else:
            # for incremental progress, small reward for straight
            if params['steering_angle'] == 0:
                reward = 1e-2
            else:
                reward = 1e-3
    return reward
