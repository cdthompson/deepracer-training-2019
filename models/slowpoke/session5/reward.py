
def reward_function(params):                                                    
  track_width = params['track_width']
  distance_from_center = params['distance_from_center']

  # Penalize if the car is too far away from the center
  marker_1 = 0.1 * track_width
  marker_2 = 0.5 * track_width

  if distance_from_center <= marker_1:
    reward = 1.0
  elif distance_from_center <= marker_2:
    reward = 0.5
  else:
    reward = 1e-3  # likely crashed/ close to off track

  return float(reward)
