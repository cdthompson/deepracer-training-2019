#!/bin/bash

while true; do \
	nvidia-smi | tee -a gpu.out; \
	sleep 5; \
done

