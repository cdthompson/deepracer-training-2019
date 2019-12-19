"""
AWS DeepRacer reward function
"""
import math
import time
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import LinearRing, LineString
from numpy import array

OVAL_TRACK_RACE_LINE = \
array([[2.77202313, 0.86236633],
       [2.96151437, 0.81752476],
       [3.15574541, 0.77947957],
       [3.35401022, 0.74758153],
       [3.5557018 , 0.72122517],
       [3.76029509, 0.69984402],
       [3.96733538, 0.68291194],
       [4.17642814, 0.66994281],
       [4.38726719, 0.66057006],
       [4.59958755, 0.65448141],
       [4.81320483, 0.65170448],
       [5.02722982, 0.65270569],
       [5.23958941, 0.6578628 ],
       [5.44976863, 0.66755716],
       [5.65735175, 0.68220305],
       [5.86193859, 0.70218515],
       [6.06314116, 0.72784067],
       [6.26058454, 0.75945803],
       [6.45390955, 0.79727605],
       [6.64273788, 0.84153424],
       [6.82657755, 0.89258713],
       [7.00490098, 0.95077319],
       [7.17718147, 1.01636738],
       [7.3425877 , 1.08992087],
       [7.50023223, 1.17190876],
       [7.64898651, 1.2628922 ],
       [7.78738344, 1.36351699],
       [7.91347317, 1.47447354],
       [8.02463565, 1.59632745],
       [8.11740041, 1.72905762],
       [8.19290898, 1.86962197],
       [8.25240687, 2.01571858],
       [8.2966585 , 2.16569229],
       [8.32643788, 2.31818976],
       [8.34223358, 2.47212347],
       [8.34443684, 2.6265478 ],
       [8.33333198, 2.78060814],
       [8.30891149, 2.93346852],
       [8.27061579, 3.08415975],
       [8.21785392, 3.23154487],
       [8.14927546, 3.37400838],
       [8.06326302, 3.50929051],
       [7.95756464, 3.63381225],
       [7.83754528, 3.7486062 ],
       [7.70510392, 3.85376707],
       [7.56156523, 3.94936186],
       [7.40816933, 4.03565557],
       [7.24586525, 4.11284122],
       [7.07554311, 4.18119668],
       [6.89812063, 4.24117074],
       [6.71436961, 4.29316522],
       [6.52507976, 4.33771344],
       [6.33104579, 4.37547577],
       [6.13297695, 4.40711235],
       [5.9314893 , 4.43325121],
       [5.72711442, 4.45447949],
       [5.52030763, 4.47133618],
       [5.31145501, 4.48430194],
       [5.10078344, 4.49344392],
       [4.88920292, 4.49869714],
       [4.67926187, 4.4999895 ],
       [4.47331831, 4.49732951],
       [4.27196051, 4.49078664],
       [4.0749199 , 4.48034629],
       [3.88171517, 4.46594003],
       [3.69194877, 4.44740695],
       [3.50531615, 4.42456111],
       [3.32161743, 4.39720122],
       [3.14075692, 4.36510565],
       [2.96275316, 4.32799753],
       [2.78773102, 4.28554112],
       [2.61599079, 4.23721767],
       [2.44792457, 4.18250188],
       [2.28410845, 4.1207434 ],
       [2.12531583, 4.05121276],
       [1.97244988, 3.97326162],
       [1.82705025, 3.88575605],
       [1.6909193 , 3.78780905],
       [1.56641859, 3.67860987],
       [1.45654372, 3.5576907 ],
       [1.36508965, 3.42535446],
       [1.29004027, 3.28537095],
       [1.23061846, 3.13981959],
       [1.18610649, 2.99033135],
       [1.15603146, 2.83819726],
       [1.13997112, 2.68451764],
       [1.13756347, 2.53025017],
       [1.14876101, 2.37627731],
       [1.17362963, 2.22349628],
       [1.21247633, 2.07289195],
       [1.26565315, 1.92555855],
       [1.33451394, 1.78308875],
       [1.42058923, 1.64766266],
       [1.52615003, 1.52277742],
       [1.64612036, 1.40758224],
       [1.77876545, 1.30215813],
       [1.92270231, 1.20645223],
       [2.0766165 , 1.12017207],
       [2.23943428, 1.04301758],
       [2.41019805, 0.9746333 ],
       [2.58800581, 0.91457886],
       [2.77202313, 0.86236633]])
# END OVAL_TRACK_RACE_LINE

# Constants
DEBUG_LOG_ENABLED = True

# Action space constants
MAX_SPEED = 5.0
MAX_STEERING_ANGLE = 40.0

# Raceline track
RACE_LINE_WAYPOINTS = OVAL_TRACK_RACE_LINE 

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
PROGRESS_FACTOR_WEIGHT = 0.0
PROGRESS_FACTOR_EASING = 'linear'
LANE_FACTOR_WEIGHT = 0.0
LANE_FACTOR_EASING = 'quintic'
RACE_LINE_FACTOR_WEIGHT = 1.0
RACE_LINE_FACTOR_EASING = 'linear'

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

  # r: Race line factor (distance from)
  race_line_factor = calculate_race_line_factor(params)

  # Log for validation
  if DEBUG_LOG_ENABLED:
    print("s: %0.2f, w: %0.2f, h: %0.2f, t: %0.2f, p: %0.2f, l: %0.2f r: %0.2f" %
          (speed_factor, wheel_factor, heading_factor, steering_factor,
           progress_factor, lane_factor, race_line_factor))

  reward = 1.0
  reward *= apply_weight(speed_factor, SPEED_FACTOR_WEIGHT, SPEED_FACTOR_EASING)
  reward *= apply_weight(wheel_factor, WHEEL_FACTOR_WEIGHT, WHEEL_FACTOR_EASING)
  reward *= apply_weight(heading_factor, HEADING_FACTOR_WEIGHT,
                         HEADING_FACTOR_EASING)
  reward *= apply_weight(steering_factor, STEERING_FACTOR_WEIGHT,
                         STEERING_FACTOR_EASING)
  reward *= apply_weight(progress_factor, PROGRESS_FACTOR_WEIGHT)
  reward *= apply_weight(lane_factor, LANE_FACTOR_WEIGHT, LANE_FACTOR_EASING)
  reward *= apply_weight(race_line_factor, RACE_LINE_FACTOR_WEIGHT, RACE_LINE_FACTOR_EASING)

  return float(max(reward, 1e-3)) # make sure we never return exactly zero



#===============================================================================
#
# RACE LINE
#
#===============================================================================
def calculate_race_line_factor(params):
    # Reward for track position
    current_position = Point(params['x'], params['y'])
    race_line = LineString(RACE_LINE_WAYPOINTS)
    distance = current_position.distance(race_line)
    # clamp reward to range (0..1) mapped to distance (track_width..0).
    # This could be negative since the car center can be off the track but
    # still not disqualified.

    factor = 1.0 - distance / (params['track_width'] / 2.0)
    #print("x %0.2f y %0.2f distance %0.2f track_width %0.2f factor %0.7f" % (params['x'], params['y'], distance, params['track_width'], factor))
    return float(max(factor, 0.0))
  

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

def progress_since_last(progress):
  global g_last_progress_value
  # progress is 0..100. The logic in DR environment code ensures this always
  # increases for the episode, regardless if the car is going backward.
  if g_last_progress_value > progress:
    g_last_progress_value = 0
  progress_factor = (progress - g_last_progress_value) / 100 # divide by 100 to get percentage of track
  g_last_progress_value = progress
  return progress_factor

def calculate_progress_factor(params):
  progress_factor = 1.0
  return min(progress_factor, 1.0)

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
  lane_factor = percentage_distance_from_track_center(params['track_width'],
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


