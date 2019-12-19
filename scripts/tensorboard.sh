#!/bin/bash

set -ex;

# This worked with DISPLAY=:0, which tells the 
# app to use unix socket at /tmp/.X11-unix for
# Xserver connection, so requires the --volume
# flag as well
#
docker exec \
	-i \
	-t \
	dr-training \
	/home/robomaker/entry_script2.sh tensorboard --logdir=/opt/ml/model/tensorboard
