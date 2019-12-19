#!/bin/bash
# Create a colcon bundle ready for consumption by RoboMaker service as a 
# simulation application.  Patch the original bundle.tar file with files from 
# ./patch.
#
# NOTE!!! ONLY WORKS ON MAC OS because of the tar command with '@'
#

if [ ! -r "robomaker/bundle.tar" ]; then
  echo "Couldn't find robomaker/bundle.tar extracted from the deepracer-simapp.tar.gz file"
  exit 1
fi

if [ ! -r "robomaker/metadata.tar" ]; then
  echo "Couldn't find robomaker/metadata.tar extracted from the deepracer-simapp.tar.gz file"
  exit 1
fi

if [ ! -r "robomaker/version" ]; then
  echo "Couldn't find robomaker/version extracted from the deepracer-simapp.tar.gz file"
  exit 1
fi

# Get list of files to exclude from the bundle
EXCLUSION_FILE=excludes.txt
find patch/ -type f | cut -c 8- > ${EXCLUSION_FILE}

# bundle.tar, patched with files from ./patch
# TODO: dynamically find patch files here
tar -v -c \
  -f build/bundle.tar \
  -X ${EXCLUSION_FILE} \
  @robomaker/bundle.tar

# Append the patch files
cat ${EXCLUSION_FILE} | xargs tar -v -r \
  -C patch \
  -f build/bundle.tar

# clean up
if [ -w "${EXCLUSION_FILE}" ]; then
  # a little safety here by naming explicitly
  rm excludes.txt
fi

# metadata.tar, unmodified
cp -f robomaker/metadata.tar build/metadata.tar

# version, unmodified
cp -f robomaker/version build/version

# From my experience, it seems that the order of the files in the tgz are
# important, otherwise Robomaker will fail to run it.  Probably a colcon-ism.
tar -c -z \
  -C build \
  -f build/deepracer-simapp-custom.tar.gz \
  version metadata.tar bundle.tar
