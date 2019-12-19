#!/bin/bash
# Test launching container with gpu support for tensorflow

set -ex;

# See http://wiki.ros.org/docker/Tutorials/Hardware%20Acceleration#Intel
xhost +

docker run \
  -it \
  --volume=/tmp/.X11-unix:/tmp/.X11-unix \
  --device=/dev/dri:/dev/dri \
  --privileged \
  --env="DISPLAY=${DISPLAY}" \
  --rm \
  deepracer-robomaker-container:latest \
  bash
#  glxinfo | head -n 10

#  --device=/dev/dri/card0:/dev/dri/card0 \
#  --device=/dev/dri/renderD128:/dev/dri/renderD128 \
#  '/usr/bin/Xvfb -shmem -screen 10 1280x1024x24 & glxinfo | head -n 10'
#  /bin/bash
