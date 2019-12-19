#!/bin/bash

set -e;

eval $AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP
export USERNAME=robomaker
export PATH=/home/$USERNAME:/opt/amazon/RoboMakerGazebo/bin:$PATH
export LD_LIBRARY_PATH=/opt/amazon/RoboMakerGazebo/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/opt/amazon/RoboMakerGazebo/lib/pkgconfig/:$PKG_CONFIG_PATH
export GAZEBO_PLUGIN_PATH=/opt/amazon/RoboMakerGazeboPlugin/plugins:/opt/amazon/RoboMakerGazebo/lib:/home/robomaker/workspace/bundle-store/deepracer-simapp/opt/ros/kinetic/lib:$GAZEBO_PLUGIN_PATH
#stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch
export ROS_MASTER_URI=${ROBOMAKER_ROS_MASTER_URI}
export GAZEBO_MASTER_URI=${ROBOMAKER_GAZEBO_MASTER_URI}

export PYTHONUNBUFFERED=1

# Run Xvfb for gazebo, otherwise its camera will not output images
# TODO: See if we can still get rqt and friends visible from outside this container
export DISPLAY=:0
/usr/bin/Xvfb -shmem -screen 0 1280x1024x24 &

# Allow a few moments for Xvfb to start up, then dump OpenGL info
sleep 3
glxinfo | grep '\(Vencor\|Device\|Accel\|Video\ memory\|Version\|Version\)'

exec "${@:1}"
