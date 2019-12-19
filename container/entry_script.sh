#!/usr/bin/env bash
set -ex

if [[ -z "${ROBOMAKER_ROS_MASTER_URI}" ]]; then
    echo "ROBOMAKER_ROS_MASTER_URI is not set"
    exit 1
fi

if [[ -z "${ROBOMAKER_GAZEBO_MASTER_URI}" ]]; then
    echo "ROBOMAKER_GAZEBO_MASTER_URI is not set"
    exit 1
fi
export USERNAME=robomaker
source /opt/amazon/RoboMakerGazebo/share/gazebo/setup.sh
export GAZEBO_MODEL_DATABASE_URI=""
export LD_LIBRARY_PATH=/opt/amazon/RoboMakerGazebo/lib:$LD_LIBRARY_PATH
export PATH=/home/$USERNAME:/opt/amazon/RoboMakerGazebo/bin:$PATH
source /opt/ros/kinetic/setup.sh
source /opt/amazon/ros/kinetic/setup.bash
export PKG_CONFIG_PATH=/opt/amazon/RoboMakerGazebo/lib/pkgconfig:$PKG_CONFIG_PATH
export GAZEBO_PLUGIN_PATH=/opt/amazon/RoboMakerGazeboPlugin/plugins:/opt/amazon/RoboMakerGazebo/lib:$GAZEBO_PLUGIN_PATH

export ROS_MASTER_URI=${ROBOMAKER_ROS_MASTER_URI}
export GAZEBO_MASTER_URI=${ROBOMAKER_GAZEBO_MASTER_URI}

# disable python stdout/stderr buffer to output to file immediately
export PYTHONUNBUFFERED=1

exec "${@:1}"
