#!/bin/bash

while true; do redis-cli -h 172.20.0.2 info memory | tee -a redis.out; sleep 5; done

