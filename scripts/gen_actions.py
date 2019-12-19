import json
import math
import numpy as np


def generate_weighted_actions(speeds, max_angle, angle_increments):
  ''' Generate unevenly spaced action space where each speed will
      have 'angle_increments' number of angles to choose from
  '''
  actions = []
  for s in speeds:
    y = s                                 # speed is y-axis, angles are x-axis

    radius = max(speeds) + 0.5            # making this just a little more than
                                          # max speed causes the angles at max
                                          # speed to not all be zero

    x_scale = (max_angle / max(speeds))   # speeds are roughly 0-10, angles in
                                          # deg are 0-30, so we scale the circle
                                          # by the ratio (x/y)

    limit_x = x_scale*math.sqrt(radius**2 - y**2)   # x**2 + y**2 = r**2

    for i in range(-angle_increments,angle_increments+1):
      actions.append({ "steering_angle": i * limit_x/angle_increments, "speed": s})
  return actions


def generate_regular_actions(speeds, angles):
  ''' Generate evenly spaced action space from speed and angle values '''
  actions = []
  for s in speeds:
    for a in angles:
      actions.append({ "steering_angle": a, "speed": s})
  return actions


if __name__ == '__main__':
  # MAIN  


  # FULL RANGE:                 143 actions
  # actions = generate_regular_actions(list(range(0,11)), list(range(-30,35,5)))

  # ...without speed zero:      130 actions
  #actions = generate_regular_actions(list(range(1,11)), list(range(-30,35,5)))

  # ...without speed ten:      117 actions
  #actions = generate_regular_actions(list(range(1,10)), list(range(-30,35,5)))

  # ...assymetric turning angles, more on left side:    90 actions
  #actions = generate_regular_actions(list(range(1,10)), [-30,-25,-20,-15,-10,-5,0,5,15,25])

  # ...higher minimum speed:   80 actions
  #actions = generate_regular_actions(list(range(2,10)), [-30,-25,-20,-15,-10,-5,0,5,15,25])

  # ...cull out less useful extremes:     67 actions
  #clipped_action_space = []
  #for a in actions:
  #  x = a['steering_angle']
  #  y = a['speed']
  #  limit_y = math.sqrt(110-(x/3)**2) # 110 is slightly above r=10; if we used 10
  #                                    # exactly then the max steering angles will
  #                                    # all be omitted
  #  if y <= limit_y:
  #    clipped_action_space.append(a)
  #  else:
  #    print("Cropped speed %i steering angle %i" % (a['speed'], a['steering_angle']))
  #actions = clipped_action_space

  # 8 speeds (2..9) times 7 angles per speed = 56 actions
  #actions = generate_weighted_actions(list(range(2,10)), 30, 3)

  # 4 speeds (2,4,6,8) times 7 angles per speed = 28 actions
  #actions = generate_weighted_actions(list(range(2,10,2)), 30, 3)

  # 4 speeds (3,5,7,9) times 5 angles per speed = 20 actions
  #actions = generate_regular_actions(list(range(3,10,2)), np.linspace(40, -40, num=7))
  actions = generate_regular_actions([2], np.linspace(40, -40, num=7))

  # Format for model_metadata.json
  i=0
  for a in actions:
    a['index'] = i
    i+=1
  model_metadata = { 'action_space': actions }

  print(json.dumps(model_metadata))

