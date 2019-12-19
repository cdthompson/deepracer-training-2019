#!/bin/bash
#
# The simulation container must already be running.  This script
# will dump 'n' snapshots as numpy arrays to the given destination 
# path.  The snapshots from Gazebo are manipulated the same way
# as in the rollout worker agent so should be suitable to plumb
# into a tensorflow model for analysis.
# 
NUMBER_OF_SNAPSHOTS=90
DESTINATION_INSIDE_CONTAINER=/opt/ml/model
docker exec \
	-it \
	dr-simulation \
	/home/robomaker/snapshots.sh \
	${NUMBER_OF_SNAPSHOTS} \
	${DESTINATION_INSIDE_CONTAINER}
