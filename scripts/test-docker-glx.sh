#!/bin/bash

set -ex;

xhost +
docker run \
	-i \
	-t \
	--rm \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env "DISPLAY=$DISPLAY" \
	--device=/dev/dri:/dev/dri \
	--privileged \
	deepracer-robomaker-container \
	glxgears

