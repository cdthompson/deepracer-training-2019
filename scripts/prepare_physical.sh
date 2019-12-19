#!/bin/bash
#
# Upload local trained model to S3 for submission via DeepRacer Console
#
#

#set -x
set -e

usage() {
  echo "Usage: $0 <local or s3:// path to model> [checkpoint number]"
  exit 1
}


if [ "x$1" == "x" ]; then
  echo "Missing folder of model (local or s3)"
  usage
fi

if [ ! "x$2" == "x" ]; then
  CHECKPOINT=$2
  echo "Using checkpoint ${CHECKPOINT}"
fi

TRAINED_PATH=$1

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

# TODO: sandbox these in a tmp directory
MODEL_PATH=model.pb
METADATA_PATH=model_metadata.json

# NOTE: omicron dummy job id is 20190829122023-ea649aa3-5f05-4525-ba62-ddd21d6474e1
aws s3 cp \
  "${TRAINED_PATH}model_${CHECKPOINT}.pb" \
  ${MODEL_PATH}
  

aws s3 cp \
  "${TRAINED_PATH}model_metadata.json" \
  ${METADATA_PATH}

# Prevent extended attributes from being added to the archive
# Also remove last 3 random characters
COPYFILE_DISABLE=1 \
    tar \
    -czf \
    model.tar.gz \
    ${MODEL_PATH} \
    ${METADATA_PATH}

rm ${MODEL_PATH}
rm ${METADATA_PATH}
