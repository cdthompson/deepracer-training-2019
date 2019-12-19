#!/bin/bash

#set -x
set -e

if [ "x$1" == "x" ]; then
  usage
fi

TRAINING_JOB_ID=$1

# S3_BUCKET: Bucket that stores training data for all
#                      training jobs.
#
S3_BUCKET='aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62'

# S3_PREFIX: Path prefix under which data is stored for
#            all training sessions
S3_PREFIX='DeepRacer-Manually-Invoked-Training-Jobs'

# ACCOUNT_ID: The AWS Account ID, useful for marking who initiated the
#             training jobs since they all use a shared S3 bucket
ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`

aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/${TRAINING_JOB_ID}/DeepRacer-Metrics/TrainingMetrics-${ACCOUNT_ID}-${TRAINING_JOB_ID}.json - | jq '.'
