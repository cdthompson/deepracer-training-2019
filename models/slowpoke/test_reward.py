"""
reward function unit tests
"""
import unittest
import math
import numpy
import time
import reward


class TestReward(unittest.TestCase):
  """ Test the reward.py module.  Hard-coded numeric values here are
  dependent upon reward constants not changing
  """

  def default_params(self):
    return {
        "all_wheels_on_track": True,        # flag to indicate if the vehicle
                                            #  is on the track
        "x": 0.0,                           # vehicle's x-coordinate in meters
        "y": 0.0,                           # vehicle's y-coordinate in meters
        "distance_from_center": 0.0,        # distance in meters from the track
                                            #  center
        "is_left_of_center": False,         # Flag to indicate if the vehicle is
                                            #  on the left side to the track
                                            #  center or not.
        "is_reversed": False,               # Flat to indicate if the vehicle is
                                            #  going the wrong direction
        "heading": 0,                       # vehicle's yaw in degrees
        "progress": 0,                      # percentage of track completed
        "steps": 0,                         # number steps completed
        "speed": 0.0,                       # vehicle's speed in meters per
                                            #  second (m/s)
        "steering_angle": 0.0,              # vehicle's steering angle in degrees
        "track_width": 10.0,                # width of the track
        "waypoints": [[0,0],[1,0]],         # list of [x,y] as milestones along
                                            # the track center
        "closest_waypoints": [0, 1]         # indices of the two nearest waypoints
    }

  def test_percentage_speed(self):
    reward.MAX_SPEED = 5.0
    self.assertEqual(reward.percentage_speed(1.0), 0.2)
    self.assertEqual(reward.percentage_speed(2.0), 0.4)
    self.assertEqual(reward.percentage_speed(3.0), 0.6)
    self.assertEqual(reward.percentage_speed(4.0), 0.8)
    self.assertEqual(reward.percentage_speed(5.0), 1.0)
    # be sure to clamp reward if we get unexpectedly high speed inputs

  def test_penalize_downshifting(self):
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.penalize_downshifting(5.0), 1.0)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.penalize_downshifting(8.0), 1.0)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.penalize_downshifting(2.0), 1e-3)

  def test_reward_upshifting(self):
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.reward_upshifting(5.0), 0.5)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.reward_upshifting(8.0), 1.0)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.reward_upshifting(2.0), 0.5)

  def test_calculate_speed_factor(self):
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.calculate_speed_factor({ 'speed': 5.0 }), 0.625)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.calculate_speed_factor({ 'speed': 8.0 }), 1.0)
    reward.g_last_speed_value = 5.0
    self.assertEqual(reward.calculate_speed_factor({ 'speed': 2.0 }), 0.25)

  def test_all_wheels_must_be_on_track(self):
    self.assertEqual(reward.all_wheels_must_be_on_track(True), 1.0)
    self.assertEqual(reward.all_wheels_must_be_on_track(False), 1e-3)

  def test_calculate_heading_factor(self):
    params = self.default_params()
    self.assertEqual(reward.calculate_heading_factor(params), 1.0)

  def test_heading_relative_to_target(self):
    params = self.default_params()
    reward.HEADING_TARGET = 0
    reward.HEADING_RANGE = 30
    # Test with zero heading target
    params['heading'] = 0
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     1.0)
    params['heading'] = 15
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    params['heading'] = -15
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    params['heading'] = 30
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.0)
    params['heading'] = 45
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.0)
    # Now test off-centered heading target.  This should not be a single
    # target of absolute angle but rather a target DELTA off of the angle.
    # This should result in 2 separate ideal rewards, one on the left and
    # one on the right of the track direction
    reward.HEADING_TARGET = 60
    # Positive (left) deltas
    params['heading'] = 60
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     1.0)
    params['heading'] = 45
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    params['heading'] = 75
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    # Negative (right) deltas
    params['heading'] = -60
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     1.0)
    params['heading'] = -45
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    params['heading'] = -75
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.5)
    params['heading'] = 0
    self.assertEqual(reward.heading_relative_to_target(params['waypoints'],
                                                       params['closest_waypoints'],
                                                       params['heading']),
                     0.0)


  def test_percentage_steering_angle(self):
    self.assertEqual(reward.percentage_steering_angle(0.0), 1.0)
    self.assertTrue(math.isclose(reward.percentage_steering_angle(math.radians(15.0)), 0.5))
    self.assertTrue(math.isclose(reward.percentage_steering_angle(math.radians(20.0)), 1/3))
    self.assertTrue(math.isclose(reward.percentage_steering_angle(math.radians(30.0)), 0.0))
    self.assertTrue(math.isclose(reward.percentage_steering_angle(math.radians(-30.0)), 0.0))
    self.assertTrue(math.isclose(reward.percentage_steering_angle(math.radians(-20.0)), 1/3))

  def test_penalize_steering_change(self):
    # Sharper turning
    reward.g_last_steering_angle = 0.0
    self.assertEqual(reward.penalize_steering_change(10.0, False, True), 1.0)
    reward.g_last_steering_angle = 0.0
    self.assertEqual(reward.penalize_steering_change(10.0, True, False), 0.0)
    reward.g_last_steering_angle = 0.0
    self.assertEqual(reward.penalize_steering_change(10.0, True, True), 0.0)
    # Straightening
    reward.g_last_steering_angle = 10.0
    self.assertEqual(reward.penalize_steering_change(0.0, False, True), 0.0)
    reward.g_last_steering_angle = 10.0
    self.assertEqual(reward.penalize_steering_change(0.0, True, False), 1.0)
    reward.g_last_steering_angle = 10.0
    self.assertEqual(reward.penalize_steering_change(0.0, True, True), 0.0)

  def test_calculate_progress_factor(self):
    params = self.default_params()
    self.assertEqual(reward.calculate_progress_factor(params), 1.0)

  def test_percentage_distance_from_track_center(self):
    self.assertEqual(reward.percentage_distance_from_track_center(10.0, 0.0), 1.0)
    self.assertEqual(reward.percentage_distance_from_track_center(10.0, 1.0), 0.8)
    self.assertTrue(math.isclose(reward.percentage_distance_from_track_center(10.0, 4.0), 0.2))
    # Check for case where distance is more than track width / 2
    self.assertTrue(math.isclose(reward.percentage_distance_from_track_center(10.0, 6.0), 0.0))

  def test_look_ahead_heading(self):
    waypoints = [
        [0.0,0.0],
        [0.0,1.0],
        [0.0,2.0]
    ]
    reward.look_ahead_heading(waypoints, 0, 0)

  def test_apply_weight(self):
    self.assertEqual(reward.apply_weight(0.5, 1.0), 0.5)
    self.assertEqual(reward.apply_weight(0.25, 0.1), 0.925)
    # Test clamping
    self.assertEqual(reward.apply_weight(1.5, 1.0), 1.0)
    self.assertEqual(reward.apply_weight(1.5, 0.5), 1.0)
    self.assertEqual(reward.apply_weight(1.0, 1.5), 1.0)
    self.assertEqual(reward.apply_weight(0.5, 1.5), 0.5)
    # Test easing                 (x)                 => y
    self.assertEqual(reward.apply_weight(0.75, 1.0, 'linear'), 0.75)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'linear'), 0.5)
    self.assertEqual(reward.apply_weight(0.25, 1.0, 'linear'), 0.25)

    self.assertEqual(reward.apply_weight(1.0, 1.0, 'quadratic'), 1.0)
    self.assertEqual(reward.apply_weight(0.9, 1.0, 'quadratic'), 0.99)
    self.assertEqual(reward.apply_weight(0.75, 1.0, 'quadratic'), 0.9375)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'quadratic'), 0.75)
    self.assertEqual(reward.apply_weight(0.25, 1.0, 'quadratic'), 0.4375)
    self.assertEqual(reward.apply_weight(0.0, 1.0, 'quadratic'), 0.0)

    self.assertEqual(reward.apply_weight(1.0, 1.0, 'cubic'), 1.0)
    self.assertEqual(reward.apply_weight(0.9, 1.0, 'cubic'), 0.999)
    self.assertEqual(reward.apply_weight(0.75, 1.0, 'cubic'), 0.984375)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'cubic'), 0.875)
    self.assertEqual(reward.apply_weight(0.25, 1.0, 'cubic'), 0.578125)
    self.assertEqual(reward.apply_weight(0.0, 1.0, 'cubic'), 0.0)

    self.assertEqual(reward.apply_weight(0.5, 1.0, 'quartic'), 0.9375)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'quintic'), 0.96875)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'septic'), 0.9921875)
    self.assertEqual(reward.apply_weight(0.5, 1.0, 'septic'), 0.9921875)
    self.assertEqual(reward.apply_weight(0.4, 1.0, 'nonic'), 0.989922304)

    # Identity
    self.assertEqual(reward.apply_weight(0.5, 0.0), 1.0)

  def test_reward_function(self):
    # TODO: mock out the dependent functions to test weighting
    params = self.default_params()
    params['speed'] = reward.MAX_SPEED
    self.assertEqual(reward.reward_function(params), 1.0)

  def test_angle_of_vector(self):
    vector = [ [0.0, 0.0], [1.0, 0.0] ] # up
    self.assertEqual(reward.angle_of_vector(vector), 0)
    vector = [ [0.0, 0.0], [1.0, 1.0] ] # diagonal up, right
    self.assertEqual(reward.angle_of_vector(vector), 45)
    vector = [ [0.0, 0.0], [1.0, -1.0] ] # diagonal up, left
    self.assertEqual(reward.angle_of_vector(vector), -45)
    vector = [ [0.0, 0.0], [0.0, 1.0] ] # left
    self.assertEqual(reward.angle_of_vector(vector), 90)
    vector = [ [0.0, 0.0], [0.0, -1.0] ] # right
    self.assertEqual(reward.angle_of_vector(vector), -90)
    vector = [ [0.0, 0.0], [-1.0, 1.0] ] # diagonal down, right
    self.assertEqual(reward.angle_of_vector(vector), 135)
    vector = [ [0.0, 0.0], [-1.0, -1.0] ] # diagonal down, left
    self.assertEqual(reward.angle_of_vector(vector), -135)
    vector = [ [0.0, 0.0], [-1.0, 0.0] ] # down
    self.assertEqual(reward.angle_of_vector(vector), 180)

  def test_vector_of_angle(self):
    """ Test each quadrant """
    vector = reward.vector_of_angle(30)
    self.assertListEqual(vector[0], [0.0, 0.0])
    self.assertTrue(math.isclose(vector[1][0], 0.5))
    self.assertTrue(math.isclose(vector[1][1], math.sqrt(3)/2))
    vector = reward.vector_of_angle(-45)
    self.assertListEqual(vector[0], [0.0, 0.0])
    self.assertTrue(math.isclose(vector[1][0], -math.sqrt(2)/2))
    self.assertTrue(math.isclose(vector[1][1], math.sqrt(2)/2))
    vector = reward.vector_of_angle(-120)
    self.assertListEqual(vector[0], [0.0, 0.0])
    self.assertTrue(math.isclose(vector[1][0], -math.sqrt(3)/2))
    self.assertTrue(math.isclose(vector[1][1], -0.5))
    vector = reward.vector_of_angle(180)
    self.assertListEqual(vector[0], [0.0, 0.0])
    self.assertTrue(math.isclose(vector[1][0], 0.0, abs_tol=1e-9))
    self.assertTrue(math.isclose(vector[1][1], -1.0))

  def test_progress_over_time(self):
    reward.g_last_progress_value = 20.0
    reward.g_last_progress_time = time.time() - 0.067 # 1 frame @ 15fps
    # For 20s lap, 20*15 frames = 300 frames => progress 100/300 = 0.33
    progress = reward.progress_over_time(20.3)
    # expect (21 - 20) / 0.067
    self.assertTrue(math.isclose(progress, 4.4771, abs_tol=1e-2))

  def test_speed_or_acceleration(self):
    reward.g_last_speed_value = 0.0
    self.assertEqual(reward.speed_or_acceleration(0.2), 1.0)

if __name__ == '__main__':
  unittest.main()
