#!/bin/bash
# Test launching container with gpu support for tensorflow

set -ex;

# This worked with DISPLAY=:0, which tells the 
# app to use unix socket at /tmp/.X11-unix for
# Xserver connection, so requires the --volume
# flag as well
#
docker run \
	-i \
	-t \
	--rm \
	--runtime=nvidia \
	-v ${PWD}/patch/opt/install/sagemaker_rl_agent/lib/python3.5/site-packages/markov:/home/robomaker/workspace/bundle-store/deepracer-simapp/opt/install/sagemaker_rl_agent/lib/python3.5/site-packages/markov \
	-e NVIDIA_VISIBLE_DEVICES=0 \
	-e NODE_TYPE=SAGEMAKER_TRAINING_WORKER \
	-e APP_REGION=us-east-1 \
        -e AWS_ACCESS_KEY_ID=minio \
        -e AWS_SECRET_ACCESS_KEY=miniokey \
        -e AWS_ENDPOINT_URL="http://192.168.80.2:9000" \
        -e REDIS_HOST=redis \
	--network 'gitlab-cdthompson-deepracer_default' \
	deepracer-cuda \
        "python3 -m markov.training_worker --aws_region us-east-1 --model_metadata_s3_key model_metadata.json --checkpoint-dir cuda/ --s3_bucket dr-local --s3_prefix cuda/"
