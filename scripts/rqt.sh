#!/bin/bash

set -ex;

# This command takes an optional ip address,
# which when omitted just disables security
# of xserver accepting connection from anywhere.
xhost +

# This worked with DISPLAY=:0, which tells the 
# app to use unix socket at /tmp/.X11-unix for
# Xserver connection, so requires the --volume
# flag as well
#
docker exec \
	-i \
	-t \
	--env "DISPLAY=$DISPLAY" \
	dr-simulation \
	/home/robomaker/entry_script2.sh rqt
