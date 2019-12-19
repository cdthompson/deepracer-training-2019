#!/bin/bash
eval ${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP}
rosnode list | grep rl_coach | xargs rosnode ping -c 5
