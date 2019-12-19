#!/bin/bash

while true; do \
	top -b -n 1 -c -w | head -n 20 | tee -a cpu_mem.out; \
	sleep 5; \
done


