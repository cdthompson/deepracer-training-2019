#!/bin/bash

docker exec -it dr-simulation /home/robomaker/entry_script2.sh gz stats | tee -a gazebo.out

