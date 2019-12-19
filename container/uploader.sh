#!/bin/bash
#
# Sync a single local directory to S3.  This is NOT intended to work with minio
# as a destination
#

                                                                                
if [ "x${AWS_ACCESS_KEY_ID}" == "x" ]; then
  echo "AWS_ACCESS_KEY_ID must be defined!"
  exit 1
fi

if [ "x${AWS_SECRET_ACCESS_KEY}" == "x" ]; then
  echo "AWS_SECRET_ACCESS_KEY must be defined!"
  exit 1
fi

if [ "x${AWS_DEFAULT_REGION}" == "x" ]; then
  echo "AWS_DEFAULT_REGION must be defined!"
  exit 1
fi

LOCAL_PATH=$1
S3_URL=$2

usage() {
  echo "$0 <local path> <s3 prefix>"
  exit 1
}

if [ "x${S3_URL}" == "x" ]; then
  echo "S3 URL not specified!"
  usage
fi

# Print out the version of aws cli tool being used
aws --version

echo "Uploader copying from ${LOCAL_PATH} to ${S3_URL}"

while true; do \

  if [ ! -r "${LOCAL_PATH}" ]; then
    echo "Local path \"${LOCAL_PATH}\" is missing or is not readable"
  fi

  aws s3 sync ${LOCAL_PATH} ${S3_URL}; \
  sleep 30; \
done
