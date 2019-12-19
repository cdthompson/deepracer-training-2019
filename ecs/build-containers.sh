#!/bin/bash
#
# Quik helper to build all the necessary containers for ECS
#

NOCACHE=""
#NOCACHE="--no-cache"

build_container() {
	IMAGE_NAME="dr-$1"
	IMAGE_TAG=latest
	DOCKERFILE_PATH="container/Dockerfile.dr-${1}"
	CONTEXT_PATH='.'
	docker build \
		${NOCACHE} \
		-t ${IMAGE_NAME}:${IMAGE_TAG} \
		-f ${DOCKERFILE_PATH} \
		${CONTEXT_PATH}
}

# logger
build_container logger

# redis
build_container redis

# simulation
build_container simulation

# training
build_container training
