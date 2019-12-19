"""
AWS DeepRacer reward function
"""
import math
import time

# Constants
DEBUG_LOG_ENABLED = True

# Action space constants
MAX_SPEED = 8.5
MAX_STEERING_ANGLE = math.radians(30.0)

# TUNING: Adjust these to find tune factors affect on reward
#
# Reward weights, always 0..1.  These are relative to one another
SPEED_FACTOR_WEIGHT = 0.0
SPEED_FACTOR_EASING = 'linear'
WHEEL_FACTOR_WEIGHT = 0.0
WHEEL_FACTOR_EASING = 'linear'
HEADING_FACTOR_WEIGHT = 0.0
HEADING_FACTOR_EASING = 'linear'
STEERING_FACTOR_WEIGHT = 0.0
STEERING_FACTOR_EASING = 'linear'
PROGRESS_FACTOR_WEIGHT = 1.0
PROGRESS_FACTOR_EASING = 'linear'
LANE_FACTOR_WEIGHT = 0.2
LANE_FACTOR_EASING = 'quartic'

# Globals
g_last_progress_value = 0.0
g_last_progress_time = 0.0
g_last_speed_value = 0.0
g_last_steering_angle = 0.0

#===============================================================================
#
# REWARD
#
#===============================================================================

def reward_function(params):
  """Reward function is:

  f(s,w,h,t,p) = 1.0 * W(s,Ks) * W(w,Kw) * W(h,Kh) * W(t,Kt) * W(p,Kp) * W(l,Kl)

  s: speed factor, linear 0..1 for range of speed from 0 to MAX_SPEED
  w: wheel factor, non-linear 0..1 for wheels being off the track and
     vehicle in danger of going off the track.  We want to use the full
     width of the track for smoothing curves so we only apply wheel
     factor if the car is hanging off the track.
  h: heading factor, 0..1 for range of angle between car heading vector
     and the track direction vector.  This is the current heading
     based on the immediate direction of the car regardless of steering.
  t: steering factor, 0..1 for steering pressure if steering the wrong
     direction to correct the heading.
  p: progress factor
  l: lane factor

  W: Weighting function: (1.0 - (1.0 - f) * Kf)
  Kx: Weight of respective factor

      Example 1:
        s = 0
        Ks = 0.5
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 0) * 0.5 = 0.5

      Example 2:
        s = 0.25
        Ks = 1.0
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 0.25) * 1.0 = 0.25

      Example 2:
        s = 1.0
        Ks = 0.1
        reward = (1.0 - ((1.0 - s) * Ks)) = 1.0 - (1.0 - 1.0) * 1.0 = 1.0

  params:

  from https://docs.aws.amazon.com/deepracer/latest/developerguide/deepracer-reward-function-input.html

    Name                  Type                    Value(s)
    ----                  ----                    --------
    track_width           float                   0..Dtrack (varies)
    distance_from_center  float                   0..~track_width/2
    speed                 float                   0.0..5.0
    steering_angle        float                   -30..30
    all_wheels_on_track   Boolean                 True|False
    heading               float                   -180..+180
    waypoints             list of [float, float]  [[xw,0,yw,0] ... [xw,Max-1, yw,Max-1]]
    closest_waypoints     [int, int]              [0..Max-2, 1..Max-1]
    steps                 int                     0..Nstep
    progress              float                   0..100
    is_left_of_center     Boolean                 True|False
    is_reversed           Boolean                 True|False
    x                     float
    y                     float

  """

  # s: Speed Factor: ideal speed is max
  speed_factor = calculate_speed_factor(params)

  # w: Wheel Factor: apply pressure when wheels are off the track
  wheel_factor = calculate_wheel_factor(params)

  # h: Heading Factor
  heading_factor = calculate_heading_factor(params)

  # t: Steering Factor
  steering_factor = calculate_steering_factor(params)

  # p: Progress Factor: TBD
  progress_factor = calculate_progress_factor(params)

  # l: Lane Factor
  lane_factor = calculate_lane_factor(params)

  # Log for validation
  if DEBUG_LOG_ENABLED:
    print("s: %0.2f, w: %0.2f, h: %0.2f, t: %0.2f, p: %0.2f, l: %0.2f" %
          (speed_factor, wheel_factor, heading_factor, steering_factor,
           progress_factor, lane_factor))

  reward = 1.0
  reward *= apply_weight(speed_factor, SPEED_FACTOR_WEIGHT, SPEED_FACTOR_EASING)
  reward *= apply_weight(wheel_factor, WHEEL_FACTOR_WEIGHT, WHEEL_FACTOR_EASING)
  reward *= apply_weight(heading_factor, HEADING_FACTOR_WEIGHT,
                         HEADING_FACTOR_EASING)
  reward *= apply_weight(steering_factor, STEERING_FACTOR_WEIGHT,
                         STEERING_FACTOR_EASING)
  #reward *= apply_weight(progress_factor, PROGRESS_FACTOR_WEIGHT)
  reward *= progress_factor
  reward *= apply_weight(lane_factor, LANE_FACTOR_WEIGHT, LANE_FACTOR_EASING)

  return float(max(reward, 1e-3)) # make sure we never return exactly zero


#===============================================================================
#
# SPEED
#
#===============================================================================

def penalize_downshifting(speed):
  global g_last_speed_value
  if g_last_speed_value > speed:
    speed_factor = 1e-3
  else:
    speed_factor = 1.0
  g_last_speed_value = speed
  return speed_factor
  
def reward_upshifting(speed):
  global g_last_speed_value
  if g_last_speed_value < speed:
    speed_factor = 1.0
  else:
    speed_factor = 0.5
  g_last_speed_value = speed
  return speed_factor

def speed_or_acceleration(speed):
  """ Reward top speed AND any acceleration as well """
  global g_last_speed_value
  if speed > g_last_speed_value:
    speed_factor = 1.0
  else:
    speed_factor = percentage_speed(speed)
  return speed_factor

def percentage_speed(speed):
  return speed / MAX_SPEED

def calculate_speed_factor(params):
  """ Calculate the speed factor """

  # make calls here not affect each other
  speed_factor = percentage_speed(params['speed'])
  return min(speed_factor, 1.0)


#===============================================================================
#
# PROGRESS
#
#===============================================================================

def progress_over_time(progress):
  """ Calculate the progress per time.  Note that
  we rely on how the simulation code calculates
  progress which is an unknown algorithm.

  The nice thing about this algorithm is that is scales
  up rewards exponentially, as the differences in lower
  lap times are more valueable than at higher lap times.
  """
  global g_last_progress_value
  global g_last_progress_time
  current_time = time.time()
  # progress is 0..100
  if g_last_progress_value == 0:
    progress_factor = 1.0 # arbitrary but positive enough to promote going
  else:
    # time can be anything, but probably ~20s/lap, 15fps:
    #       1s/15frames = 67ms/frame = 0.067s
    #
    #   for 30s/lap: 30s*15f/s = 400 frames
    #         => expected progress of 100/400 = 0.25 per frame
    #         => 3.7
    #
    #   assuming 20s/lap: 20s*15f/s = 300 frames
    #         => expected progress of 100/300 = 0.3 progress per frame / 0.067s
    #         => 4.47
    #
    #   for 13s/lap: 13s*15f/s = 195 frames
    #         => expected progress of 100/195 = 0.51 per frame
    #         => 7.6
    #
    #   for 12s/lap: 12s*15f/s = 180 frames
    #         => expected progress of 100/180 = 0.55 per frame
    #         => 8.2
    #
    #   for 10s/lap: 10s*15f/s = 150 frames
    #         => expected progress of 100/150 = 0.67 per frame
    #         => 10
    #
    #   for 9s/lap: 9s*15f/s = 135 frames
    #         => expected progress of 100/135 = 0.74 per frame
    #         => 11.04
    #
    #   for 8s/lap: 8s*15f/s = 120 frames
    #         => expected progress of 100/120 = 0.83 per frame
    #         => 12.39
    #
    progress_factor = (progress - g_last_progress_value) / (current_time - g_last_progress_time)

  g_last_progress_value = progress
  g_last_progress_time = current_time
  return max(progress_factor, 0.0)  #make sure not going backwards

def calculate_progress_factor(params):
  progress_factor = progress_over_time(params['progress'])
  return progress_factor 

#===============================================================================
#
# WHEELS
#
#===============================================================================


def all_wheels_must_be_on_track(all_wheels_on_track):
  """ Return low factor if car doesn't have all its wheels on the track """
  if not all_wheels_on_track:
    wheel_factor = 1e-3   # hard code multiplier rather than making it
                          # continuous since we don't know the width of
                          # the car wheelbase
  else:
    wheel_factor = 1.0
  return wheel_factor


def calculate_wheel_factor(params):
  """ Calculate the wheel factor """
  wheel_factor = all_wheels_must_be_on_track(params['all_wheels_on_track'])
  return min(wheel_factor, 1.0)


#===============================================================================
#
# HEADING
#
#===============================================================================

def look_ahead_heading(waypoints, current_waypoint, heading):
  """ Apply pressure based on upcoming track heading """
  
  track_headings = []
  v_init = current_waypoint
  for i in range(3):
    v1 = waypoints[(current_waypoint + 2*i) % len(waypoints)]
    v2 = waypoints[(current_waypoint + 2*i + 1) % len(waypoints)]
    track_heading = angle_of_vector([v1,v2])
    track_headings.append(track_heading)
  print(track_headings)
  return 1.0

def calculate_heading_factor(params):
  """ Calculate the heading factor """
  """
  # SUPRESS: This is too experimental while we haven't finished tracks yet
  closest_waypoints = params['closest_waypoints']
  waypoints = params['waypoints']
  heading = params['heading']

  # Calculate the immediate track angle
  wp1 = waypoints[closest_waypoints[0]]
  wp2 = waypoints[closest_waypoints[1]]
  ta1 = angle_of_vector([wp1,wp2])
  print("track angle 1: %i" % ta1)

  # h: Heading Factor: apply pressure as heading is different than track angle

  # Find closest angle, accounting for possibility of wrapping
  a = abs(ta1 - heading)
  b = abs(ta1 - (heading + 360))
  heading_delta = min(a,b)
  # hard fail if going backwards
  if heading_delta > 90:
    heading_factor = 1e-3
  elif heading_delta > 45:
    heading_factor = 0.5
  else:
    heading_factor = 1.0
  """
  heading_factor = 1.0
  heading_factor = look_ahead_heading(params['waypoints'],
                                      params['closest_waypoints'][0],
                                      params['heading'])
  return min(heading_factor, 1.0)


#===============================================================================
#
# STEERING
#
#===============================================================================

def penalize_steering_change(steering_angle, greater=True, less=True):
  ''' 
  Penalize steering changes 
    
  @greater: penalize sharper turning
  @less: penalize straightening
  '''
  global g_last_steering_angle
  if abs(steering_angle) > g_last_steering_angle and greater:
    # turning sharper
    steering_penalty = 1.0
  elif abs(steering_angle) < g_last_steering_angle and less:
    # straightening
    steering_penalty = 1.0
  else:
    steering_penalty = 0.0
  g_last_steering_angle = abs(steering_angle)
  return 1.0 - steering_penalty

def percentage_steering_angle(steering_angle):
  steering_severity = abs(steering_angle) / MAX_STEERING_ANGLE
  return max(min(1.0 - steering_severity, 1.0), 0.0)

def calculate_steering_factor(params):
  """ Calculate the steering factor """
  steering_factor = percentage_steering_angle(params['steering_angle'])
  return min(steering_factor, 1.0)


#===============================================================================
#
# LANE
#
#===============================================================================

def percentage_distance_from_track_center(track_width, distance_from_center):
  """ Return a linear percentage distance along the track width from
  the center to the outside
  """
  # make sure not negative, in case distance_from_center is over the track_width
  distance = distance_from_center / (track_width/2.0)
  return max(min(1.0 - distance, 1.0), 0.0)

def penalize_off_track(track_width, distance_from_center):
  if distance_from_center >= (track_width/2.0):
    penalty = 1.0
  else:
    penalty = 0.0
  return (1.0 - penalty)

def calculate_lane_factor(params):
  """ Calulcate the reward for the position on the track.
  Be careful to account for the wheel factor here, possibly merge
  the two later.
  """
  lane_factor = penalize_off_track(params['track_width'],
                                   params['distance_from_center'])
  return min(lane_factor, 1.0)


#===============================================================================
#
# HELPER METHODS
#
#===============================================================================

def apply_weight(factor, weight, easing='linear'):
  """Apply a weight to factor, clamping both arguments at 1.0

  Factor values will be 0..1. This function will cause the range of the
  factor values to be reduced according to:

    f = 1 - weight * (1 - factor)^easing

  In simple terms, a weight of 0.5 will cause the factor to only have weighted
  values of 0.5..1.0. If we further apply an easing, the decay from 1.0 toward
  the weighted minimum will be along a curve.
  """

  f_clamp = min(factor, 1.0)
  w_clamp = min(weight, 1.0)
  if EASING_FUNCTIONS[easing]:
    ease = EASING_FUNCTIONS[easing]
  else:
    ease = EASING_FUNCTIONS['linear']

  return 1.0 - w_clamp * ease(1.0 - f_clamp)


def vector_of_angle(angle):
  """ Unit vector of an angle in degrees. """
  return [[0.0, 0.0], [math.sin(math.radians(angle)), math.cos(math.radians(angle))]]


def angle_of_vector(vector):
  """ Calculate the angle of the vector in degrees relative to
  a normal 2d coordinate system.  This is useful for finding the
  angle between two waypoints.

    vector: [[x0,y0],[x1,y1]]

  """
  rad = math.atan2(vector[1][1] - vector[0][1], vector[1][0] - vector[0][0])
  return math.degrees(rad)

#
# SCALING FUNCTIONS
#

def ease_linear(x):
  return x

def ease_quadratic(x):
  return x*x

def ease_cubic(x):
  return abs(x*x*x)

def ease_quartic(x):
  return x*x*x*x

def ease_quintic(x):
  return abs(x*x*x*x*x)

def ease_septic(x):
  return abs(x*x*x*x*x*x*x)

def ease_nonic(x):
  return abs(x*x*x*x*x*x*x*x*x)

EASING_FUNCTIONS = {
    'linear': ease_linear,
    'quadratic': ease_quadratic,
    'cubic': ease_cubic,
    'quartic': ease_quartic,
    'quintic': ease_quintic,
    'septic': ease_septic,
    'nonic': ease_nonic
}

