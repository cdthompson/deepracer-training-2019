#!/bin/bash
#
# Upload local trained model to S3 for submission via DeepRacer Console
#
#

#set -x
set -e

usage() {
  echo "Usage: $0 <submission|evaluation> <local or s3:// path to model> [checkpoint number]"
  exit 1
}


if [ "x$1" == "x" ]; then
  echo "Missing target 'submission' or 'evaluation'"
  usage
fi

if [ ! "$1" == "submission" -a ! "$1" == "evaluation" ]; then
  echo "Target miss be either 'submission' or 'evaluation'"
  usage
fi

if [ "x$2" == "x" ]; then
  echo "Missing folder of model (local or s3)"
  usage
fi

if [ ! "x$3" == "x" ]; then
  CHECKPOINT=$3
  echo "Using checkpoint ${CHECKPOINT}"
fi

# Evaluation job id, NOT the training job id
TARGET_JOB=$1
TRAINED_PATH=$2

if [ ! "${TRAINED_PATH:0:5}" == "s3://" ]; then
  if [ ! -d "${TRAINED_PATH}" ]; then
    echo "Local trained folder '${TRAINED_PATH}' is not readable"
    exit 1
  fi

  if [ ! -r "${TRAINED_PATH}/checkpoint" ]; then
    echo "Local trained folder '${TRAINED_PATH}' does not contain a checkpoint file"
    exit 1
  fi
else
  set +e
  aws s3 ls ${TRAINED_PATH} | grep checkpoint > /dev/null
  RESULT=$?
  set -e
  if [ ! "${RESULT}" == "0" ]; then
    echo "Can't find checkpoint file at ${TRAINED_PATH}"
    exit 1
  fi
fi

#===========================
# CONSTANTS FOR ALL COMMANDS
#===========================

# S3_BUCKET: Bucket that stores training data for all
#                      training jobs.
#
# TODO: Don't use DeepRacer console's location, instead create a parallel
#       universe with proper VPC, S3, permissions, etc.
S3_BUCKET='aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62'

# ACCOUNT_ID: The AWS Account ID, useful for marking who initiated the
#             training jobs since they all use a shared S3 bucket
ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`

# NOV model in DeepRacer folder in S3
if [ "${TARGET_JOB}" == "submission" ]; then
  DUMMY_JOB_ID='DeepRacer-SageMaker-RoboMaker-comm-345864641105-20191106150504-509b3fa1-55de-4afb-9e49-e5e703343daa'
  echo "Are you sure you are ready to submit the model? [Y/n]"
  read answer
  if [ ! "${answer:0:1}" == "Y" ]; then
    echo "Aborting upload"
    exit 0
  fi
elif [ "${TARGET_JOB}" == "evaluation" ]; then
  DUMMY_JOB_ID='DeepRacer-SageMaker-RoboMaker-comm-345864641105-20191105225245-13068bfc-6230-401a-b32d-038093c60151'
else
  exit 1
fi

# Discover the most recent checkpoint none indicated
#
# checkpoint is formatted like:
# 
#   ```
#   model_checkpoint_path: "44_Step-140183.ckpt"
#   all_model_checkpoint_paths: "40_Step-119022.ckpt"
#   all_model_checkpoint_paths: "41_Step-122847.ckpt"
#   all_model_checkpoint_paths: "42_Step-128362.ckpt"
#   all_model_checkpoint_paths: "43_Step-134407.ckpt"
#   all_model_checkpoint_paths: "44_Step-140183.ckpt"
#   ```
#
if [ "x${CHECKPOINT}" == "x" ]; then
  CHECKPOINT=`aws s3 cp \
    "${TRAINED_PATH}checkpoint" \
    - | sed \
      -e 's/^model_checkpoint_path: "\([0-9]*\).*/\1/' \
      -e '/^all/d'`
  echo "Latest checkpoint is ${CHECKPOINT}"
fi

# Copies files:
#   model_metadata.json
#   X_Step-Y.ckpt.Z (for any X,Y,Z)
#   checkpoint

# NOTE: omicron dummy job id is 20190829122023-ea649aa3-5f05-4525-ba62-ddd21d6474e1
aws s3 cp \
  "${TRAINED_PATH}" \
  "s3://${S3_BUCKET}/${DUMMY_JOB_ID}/model/" \
  --recursive \
  --exclude '*' \
  --include "${CHECKPOINT}*" \
  --include "model_metadata.json"

# Find the actual filename (with step count) of the checkpoint
CHECKPOINT_PREFIX=`aws s3 ls \
  "${TRAINED_PATH}${CHECKPOINT}" | \
    grep index | sed "s/.*\(${CHECKPOINT}_.*\.ckpt\).*/\1/"`
echo "Checkpoint prefix: ${CHECKPOINT_PREFIX}"

echo "model_checkpoint_path: \"${CHECKPOINT_PREFIX}\"" |
  aws s3 cp \
  - \
  "s3://${S3_BUCKET}/${DUMMY_JOB_ID}/model/checkpoint"
