#!/bin/bash

disk_usage() {
	echo "=== du ==="
	du -h ../data/dr-local/*
	echo "=== df ==="
	df
}

while true; do \
	disk_usage | tee -a disk.out; \
	sleep 5;
done
