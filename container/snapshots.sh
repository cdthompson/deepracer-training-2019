#!/bin/bash
#
# Read a raw stream of images, encode them as h264 ts packets,
# and send them across the network to a given endpoint
#

usage() {
	echo "Usage: $0 <number of snapshots to take> <destination>"
	exit 1
}

NUMBER_OF_SNAPSHOTS=$1
if [ "x${NUMBER_OF_SNAPSHOTS}" == "x" ]; then
  echo "Destination url was not provided!"
  usage
fi

DESTINATION=$2
if [ "x${DESTINATION}" == "x" ]; then
  echo "Destination folder not provided"
  usage
fi

cd /home/robomaker/workspace/bundle-store/deepracer-simapp

# This should ideally be setup somewhere else
BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp source /home/robomaker/workspace/bundle-store/deepracer-simapp/setup.sh; export BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp

# Make each frame write as one chunk
export PYTHONUNBUFFERED=1

python3 -c "
import numpy as np
import os.path
from PIL import Image
import queue
import rospy
from sensor_msgs.msg import Image as sensor_image
import sys

TRAINING_IMAGE_SIZE = (160, 120)
FILL_COLOR = (108,106,105,255)
TOP_FILL_AREA = (0,0,160,30)
BOTTOM_FILL_AREA = (0,0,160,30)

image_queue = queue.Queue(1)

def callback(data):
  try:
    image_queue.put_nowait(data)
  except queue.Full:
    pass

rospy.init_node('snapshots', anonymous=True)
rospy.Subscriber('/camera/zed/rgb/image_rect_color', sensor_image, callback)

count = 1
limit = int(sys.argv[1])
dest_path = sys.argv[2]
while True:
  image_data = image_queue.get(block=True, timeout=None)
  image = Image.frombytes('RGB', (image_data.width, image_data.height), image_data.data, 'raw', 'RGB', 0, 1)
  image = image.resize(TRAINING_IMAGE_SIZE, resample=2)
  #image.paste(FILL_COLOR, box=TOP_FILL_AREA)
  #image.paste(FILL_COLOR, box=BOTTOM_FILL_AREA)
  np.save(os.path.join(dest_path, '%d.npy' % count), np.array(image))
  if count % 15 == 0:
    print('Wrote %d images' % count)
  if count >= limit:
    break
  count += 1
" \
  ${NUMBER_OF_SNAPSHOTS} \
  ${DESTINATION}
