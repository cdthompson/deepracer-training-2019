#!/bin/bash
#
# Increase the priority of the rollout worker so that it doesn't drop frames
#
pgrep -f rollout | xargs renice -10
pgrep -f streamer | xargs renice 20
pgrep -f ffmpeg | xargs renice 20
