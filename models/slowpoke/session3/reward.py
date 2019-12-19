# Observations from deepracer_racetrack_env.py
#
# - progress will never decrease, even if track position goes less, it will
#   just show the highest progress reached on previous steps

# From racecar.xacro
#
# - hinge limits are -1.0..1.0 in radians as described by 
#   http://wiki.ros.org/urdf/XML/joint. This is ~57deg



def reward_function(params):                                                    
  TARGET_STEPS = 10000  # max steps before DR will cancel episode
  current_progress = params['progress']

  # Make a rabbit going exactly at the target speed
  progress_rabbit = params['steps'] / TARGET_STEPS
  
  # allowable distance away from target rabbit before we just cancel the
  # episode and retry (mostly for training efficiency)
  TARGET_PROGRESS_WINDOW = 10.0
  progress_delta = abs(progress_rabbit - current_progress)

  # This should output:
  #   1.0 if right on the rabbit
  #   0.5 if TARGET_PROGRESS_WINDOW/2 away from rabbit
  #   0.0 if TARGET_PROGRESS_WINDOW away from rabbit
  #   -n if outside of TARGET_PROGRESS_WINDOW (which promotes crash ending)
  reward = 1.0 - (progress_delta / TARGET_PROGRESS_WINDOW)

  print("progress=%4f, rabbit=%4f, delta=%4f, reward=%4f" % (current_progress,
                                                             progress_rabbit,
                                                             progress_delta,
                                                             reward))
  return float(reward)

if __name__ == "__main__":
  reward_function({'progress': 1.0, 'steps': 0})
