"""
AWS DeepRacer reward function using only progress
"""

#===============================================================================
#
# REWARD
#
#===============================================================================

def reward_function(params):
    # Skipping the explanation and verbose math here...
    baseline = 102
    motivator = -1
    distance_to_goal = 100.0 - params['progress']
    
    reward = baseline + \
             motivator + \
             -distance_to_goal
    # 1e-8 is a crash so we ALWAYS need to be higher than that
    return float(max(reward, 1e-3))
