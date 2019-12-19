"""
Run some sane input values through the reward function
in order to validate that the aggregate reward values make
sense upon visual analysis, helpful in tuning factor weights.
"""
import math
from reward import reward_function

def generate_inputs(overrides):
  """ Populate default inputs expected by the reward function """
  default_inputs = {
      "all_wheels_on_track": True,        # flag to indicate if the vehicle
                                          #  is on the track
      "x": 0.0,                           # vehicle's x-coordinate in meters
      "y": 0.0,                           # vehicle's y-coordinate in meters
      "distance_from_center": 0.0,        # distance in meters from the track
                                          #  center
      "is_left_of_center": False,         # Flag to indicate if the vehicle is
                                          #  on the left side to the track
                                          #  center or not.
      "heading": 0,                       # vehicle's yaw in degrees
      "progress": 0,                      # percentage of track completed
      "steps": 0,                         # number steps completed
      "speed": 0.0,                       # vehicle's speed in meters per
                                          #  second (m/s)
      "steering_angle": 0.0,              # vehicle's steering angle in degrees
      "track_width": 10.0,                # width of the track
      "waypoints": [],                    # list of [x,y] as milestones along
                                          # the track center
      "closest_waypoints": [0, 1]         # indices of the two nearest waypoints
  }

  # Simple circle staring at the origin just to keep values somewhat usable
  scale = 20.0 # needs to at least be track_width/2
  for angle in [0, 30, 60, 90, 120, 150, 180, -150, -120, -90, -60, -30]:
    default_inputs['waypoints'].append(
        [
            scale * math.cos(math.radians(angle)),
            scale * math.sin(math.radians(angle))
        ]
    )
  merged = default_inputs.copy()
  merged.update(overrides)
  return merged


def print_reward(inputs, result):
  """ Print formatted inputs and reward values """
  print(inputs)
  print("result = %f" % result)


if __name__ == '__main__':
  inputs = generate_inputs({})
  print_reward(inputs, reward_function(inputs))
  inputs['speed'] = 6.0
  print_reward(inputs, reward_function(inputs))
  inputs['speed'] = 5.0
  inputs['steering_angle'] = 20.0
  print_reward(inputs, reward_function(inputs))
