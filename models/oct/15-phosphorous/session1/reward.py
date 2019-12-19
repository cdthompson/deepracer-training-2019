START_BRAKING = 17
END_BRAKING = 25
BRAKE_SPEED = 1

""" Straight, please """
def reward_function(params):
    # No rewards shaping yet, just add a brake by track position
    if params['closest_waypoints'][0] >= START_BRAKING and params['closest_waypoints'][0] >= END_BRAKING and params['speed'] == BRAKE_SPEED:
        # BRAKE!
        reward = 1
    elif params['speed'] > BRAKE_SPEED:
        # Don't brake!
        reward = 1
    else:
        # You're doing it wrong!
        reward = 1e-3
    return reward
