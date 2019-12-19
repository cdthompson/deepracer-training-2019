"""
AWS DeepRacer reward function using only progress

NOTE: This is great for maximizing individual step rewards, but the 
total episode reward will always be 100.  
"""

# Globals
g_last_progress_value = 0.0

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
    reward = progress_factor_delta(params) * time_factor_steps(params)
    return float(max(reward, 1e-3)) # make sure we never return exactly zero

def time_factor_steps(params):
    # Discount by number of elapsed steps
    if params['steps'] == 0:
        return 1.0
    else:
        # step 2 discounted 50%
        # desired scale: [1.0,0] over range of [0,200] steps (200 being a ~13s lap)
        #
        # Linear decay function: y = 1 + (1-x)/(200)
        return 1.0 + (1 - params['steps'])/200

def progress_factor_delta(params):
    # Progress range:  0..100
    # Step is roughly a 1/15s timeslice so can account for time-factor
    # Expected real value: [0,~1.0]
    global g_last_progress_value

    # Simple reward for outlier case of first step in the episode
    if params['steps'] == 0:
        reward = 1e-3
    else:
        reward = params['progress'] - g_last_progress_value
    g_last_progress_value = params['progress']
    return reward

def progress_factor_absolute(params):
    return params['progress']
