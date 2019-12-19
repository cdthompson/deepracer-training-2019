#!/bin/bash
#
# The simulation container must already be running.  This will push a stream to 
# the provided endpoint (hard-coded currently as my mac)
# 
# Add a '-d' flag here if this should just run in the background
#
docker exec \
	-it \
	dr-simulation \
	/home/robomaker/streamer.sh \
	udp://192.168.1.110:10000?pkt_size=1316 \
	3000k
