#!/bin/bash
#
# Read a raw stream of images, encode them as h264 ts packets,
# and send them across the network to a given endpoint
#

usage() {
	echo "Usage: $0 <destination url> [bitrate]"
	exit 1
}

DESTINATION=$1
if [ "x${DESTINATION}" == "x" ]; then
	echo "Destination url was not provided!"
	usage
fi

BITRATE=$2
if [ "x${BITRATE}" == "x" ]; then
	BITRATE=600k
fi

cd /home/robomaker/workspace/bundle-store/deepracer-simapp

# This should ideally be setup somewhere else
BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp source /home/robomaker/workspace/bundle-store/deepracer-simapp/setup.sh; export BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp

# Make each frame write as one chunk
export PYTHONUNBUFFERED=1

python -c "
import rospy
from sensor_msgs.msg import Image as sensor_image
import sys
rospy.init_node('streamer', anonymous=True)
rospy.Subscriber('/camera/zed/rgb/image_rect_color', sensor_image, lambda image: sys.stdout.write(image.data))
rospy.spin()" | \
ffmpeg \
	-f rawvideo \
	-pixel_format rgb24 \
	-video_size 640x480 \
	-framerate 15 \
	-i - \
	-preset ultrafast \
	-vcodec libx264 \
	-tune zerolatency \
	-b ${BITRATE} \
	-f mpegts \
	-pix_fmt yuv420p \
	-g 45 \
	-r 15 \
	${DESTINATION}
