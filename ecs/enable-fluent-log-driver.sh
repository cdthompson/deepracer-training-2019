#!/bin/bash
echo "ECS_AVAILABLE_LOGGING_DRIVERS=[\"json-file\",\"awslogs\",\"fluentd\"]" >> /etc/ecs/ecs.config
