# NOTE!!!! These MUST map to the action space or rewards will not work
ACTIONS = {
    "sharp left":  0,
    "easy left":   1,
    "straight":    2,
    "easy right":  3,
    "sharp right": 4,
}

# NOTE: These are specific to Canada_Training.npy waypoints
CHECKPOINTS = [
    # checkpoint, preceding action (makes loop easier)
    (20,
     "straight"),
    (40,
     "sharp left"),
    (85,
     "straight"),
    (95,
     "easy left"),
    (130,
     "straight"),
    (150,
     "easy left"),
    (10000,
     "straight")
]

# Test reward function
def reward_function(params):
    global ACTIONS
    global CHECKPOINTS
    closest_waypoint = params["closest_waypoints"][0]
    for i in range(len(CHECKPOINTS)):
        checkpoint, action = CHECKPOINTS[i]
        if closest_waypoint < checkpoint:
            
            if params["action"] == ACTIONS[action]:
                # full reward it using the right action for the leg
                return 1.0
            elif abs(params["action"] - ACTIONS[action]) == 1:
                # allow the car to use adjacent actions without too much penalty
                return 0.25
            else:
                return 1e-3
