#!/bin/bash
# '''
# Generate the S3 paths needed for manually invoking a SageMaker+Robomaker
# training session
# '''

#set -x
set -e

usage() {
  echo "Usage: $0 <training job id> <track> <number episodes> [checkpoint]"
  exit 1
}

if [ "x$1" == "x" -o "x$2" == "x" -o "x$3" == "x" ]; then
  usage
fi

EVALUATION_PRETRAINED_JOB_ID=$1
world_name=$2
number_of_episodes=$3

if [ ! "x$4" == "x" ]; then
    CHECKPOINT=$4
fi


if [ "x${AWS_ACCESS_KEY_ID}" == "x" -o "x${AWS_SECRET_ACCESS_KEY}" == "x" -o "x${AWS_DEFAULT_REGION}" == "x" ]; then
  echo "AWS credentials not set!"
  echo "AWS_ACCESS_KEY_ID: \"${AWS_ACCESS_KEY_ID}\""
  echo "AWS_SECRET_ACCESS_KEY: \"${AWS_SECRET_ACCESS_KEY}\""
  echo "AWS_DEFAULT_REGION: \"${AWS_DEFAULT_REGION}\""
  exit 1
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

# S3_PREFIX: Path prefix under which data is stored for
#            all training sessions
S3_PREFIX='training-jobs'


# ACCOUNT_ID: The AWS Account ID, useful for marking who initiated the
#             training jobs since they all use a shared S3 bucket
ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`

APP_REGION='us-east-1'


# default deepracer simapp
#RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-051bbb71-b8cb-4898-a31f-979631825e54/1564689218391"
# neurips simapp
RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-neurips/1574899151419"
# custom colcon bundle
# TODO: Verify there aren't any environmental edits before this is used for evaluation
#RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-custom-test/1567095466134"


#=========
# HELPER FUNCTIONS
#=========

create_and_verify_folder() {
  CREATE_FOLDER_PATH=$1
  if [ "x${CREATE_FOLDER_PATH}" == "x" ]; then
    echo "create_and_verify_folder called with empty folder name"
    exit 1
  fi

  # Make sure it has a trailing '/' else we'll get a file
  if [ "${CREATE_FOLDER_PATH: -1}" != '/' ]; then
    CREATE_FOLDER_PATH="$CREATE_FOLDER_PATH/"
  fi

  # Check for existance
  set +e
  aws s3api get-object-acl --bucket ${S3_BUCKET} --key ${CREATE_FOLDER_PATH} > /dev/null 2>&1
  RESULT=$?
  set -e
  if [ ! $RESULT == 0 ]; then
    # Try to create it
    echo -n "Creating $1..."
    aws s3api put-object --bucket ${S3_BUCKET} --key ${CREATE_FOLDER_PATH} > /dev/null 2>&1
    echo "done"
  else
    echo "$1 exists"
  fi
}

#=========
# TRAINING 
#=========

# DATE: Date strings in jobs makes an alphabetic sort by name convenient to
#       move recent sessions to the top
DATE=`date "+%Y%m%d%H%M%S"`

# JOB_UUID: To make sure each job as a unique id, avoiding potential
#           collisions in DATE
JOB_UUID=`uuidgen`

JOB_ID="${DATE}-${JOB_UUID}"

echo
echo
echo "Job ID ${JOB_ID}"
echo
echo


#=======================
# ROBOMAKER JOB
#=======================

# Where the model will be read from
SOURCE_MODEL_PREFIX="${S3_PREFIX}/${EVALUATION_PRETRAINED_JOB_ID}/shared/model/"

# We make a sandboxed model directory for evaluation, so that we can evaluate arbitrary checkpoints
# The Robomaker app REQUIRES the '/model/' path part to be there
EVALUATION_PREFIX="${S3_PREFIX}/${EVALUATION_PRETRAINED_JOB_ID}/evaluations/${JOB_ID}/"
EVALUATION_CHECKPOINT_KEY="${EVALUATION_PREFIX}model/checkpoint"
EVALUATION_METRICS_KEY="${EVALUATION_PREFIX}EvaluationMetrics-${ACCOUNT_ID}-${JOB_ID}-${world_name}.json"
EVALUATION_MODEL_METADATA_KEY="${EVALUATION_PREFIX}model/model_metadata.json"

#=======================
# CREATE S3 RESOURCES
#=======================

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
    "s3://${S3_BUCKET}/${SOURCE_MODEL_PREFIX}checkpoint" \
    - | sed \
      -e 's/^model_checkpoint_path: "\([0-9]*\).*/\1/' \
      -e '/^all/d'`
  echo "Using latest checkpoint ${CHECKPOINT}"
else
  echo "Using checkpoint ${CHECKPOINT}"
fi

# Find the actual filename (with step count) of the checkpoint
CHECKPOINT_PREFIX=`aws s3 ls \
  "s3://${S3_BUCKET}/${SOURCE_MODEL_PREFIX}${CHECKPOINT}" | \
    grep index | sed "s/.*\(${CHECKPOINT}_.*\.ckpt\).*/\1/"`
echo "Checkpoint prefix: ${CHECKPOINT_PREFIX}"


# Verify source folders to read model from
create_and_verify_folder "${SOURCE_MODEL_PREFIX}"

# Verify evaluation output folder
create_and_verify_folder "${EVALUATION_PREFIX}"


# Copy checkpoint files and metadata (actions) to evaluation folder
aws s3 cp \
  "s3://${S3_BUCKET}/${SOURCE_MODEL_PREFIX}" \
  "s3://${S3_BUCKET}/${EVALUATION_PREFIX}model/" \
  --recursive \
  --exclude '*' \
  --include "${CHECKPOINT}*" \
  --include "model_metadata.json"

# Write a checkpoint meta file indicating the model to load
echo "model_checkpoint_path: \"${CHECKPOINT_PREFIX}\"" |
  aws s3 cp \
  - \
  "s3://${S3_BUCKET}/${EVALUATION_CHECKPOINT_KEY}"


if [ ! "x${start_position}" == "x" ]; then
  START_POSITION=${start_position}
else
  START_POSITION=0.0
fi
if [ ! "x${change_start_position}" == "x" ]; then
  export CHANGE_START_POSITION=${change_start_position}
else
  export CHANGE_START_POSITION=false
fi
if [ ! "x${alternate_driving_direction}" == "x" ]; then
  export ALTERNATE_DRIVING_DIRECTION=${alternate_driving_direction}
else
  export ALTERNATE_DRIVING_DIRECTION=false
fi


#==============================================================
# KINESIS VIDEO STREAM (only needed for official simapp bundle)
#==============================================================

KVS_STREAM_NAME="dr-kvs-${JOB_ID}"

echo "Creating Kinesis video stream ${KVS_STREAM_NAME}"

aws --region ${APP_REGION} \
	kinesisvideo create-stream \
	--stream-name ${KVS_STREAM_NAME} \
	--media-type video/h264 \
	--data-retention-in-hours 24

#======================
# ROBOMAKER JOB - TRAINING AND EVALUATION
#======================

# Evaluation environment variables:
#
RM_SIMULATION_JSON="[
{                                                                       
  \"application\": \"${RM_APP_ARN}\",
  \"applicationVersion\": \"\$LATEST\",
  \"launchConfig\": {                                                   
    \"packageName\": \"deepracer_simulation_environment\",              
    \"launchFile\": \"evaluation.launch\",                    
    \"environmentVariables\": {                                       
      \"APP_REGION\":	\"${APP_REGION}\",
      \"KINESIS_VIDEO_STREAM_NAME\": \"${KVS_STREAM_NAME}\",
      \"METRICS_S3_BUCKET\": \"${S3_BUCKET}\",
      \"METRICS_S3_OBJECT_KEY\": \"${EVALUATION_METRICS_KEY}\",
      \"NUMBER_OF_TRIALS\":	\"${number_of_episodes}\",
      \"ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID\": \"${ACCOUNT_ID}\",
      \"MODEL_S3_BUCKET\":	\"${S3_BUCKET}\",
      \"MODEL_S3_PREFIX\":	\"${EVALUATION_PREFIX}\",
      \"WORLD_NAME\":	\"${world_name}\",
      \"START_POSITION\":	\"${START_POSITION}\",
      \"CHANGE_START_POSITION\":	\"${CHANGE_START_POSITION}\",
      \"ALTERNATE_DRIVING_DIRECTION\":	\"${ALTERNATE_DRIVING_DIRECTION}\"
    }                                                               
  }                                                                   
}
]"
echo -n "Creating evaluation job..."

RM_JOB_INPUT_JSON="{
  \"clientRequestToken\": \"\",
  \"maxJobDurationInSeconds\": 0,
  \"iamRole\": \"arn:aws:iam::345864641105:role/service-role/AWSDeepRacerRoboMakerAccessRole\",
  \"failureBehavior\": \"Fail\",
  \"simulationApplications\": ${RM_SIMULATION_JSON},
  \"tags\": {
    \"DeepRacer-Manually-Invoked-Training-Jobs\": \"true\",
    \"EVALUATION_JOB_ID\": \"${JOB_ID}\",
    \"TRAINING_JOB_ID\": \"${EVALUATION_PRETRAINED_JOB_ID}\"
  },
  \"vpcConfig\": {
    \"subnets\": [
      \"subnet-0b462e2666bfc8b42\",
      \"subnet-0c17dcc711ca0d647\",
      \"subnet-0308c84b560b7523f\",
      \"subnet-02859793120cd62b1\",
      \"subnet-0907b942eaf144f31\",
      \"subnet-0f34973fdfcaac137\"
    ],
    \"securityGroups\": [
      \"sg-0b9bd3a41e11cf278\"
    ],
    \"assignPublicIp\": true
  }
}"

echo " done"

aws robomaker create-simulation-job \
  --client-request-token "${JOB_ID}" \
  --max-job-duration-in-seconds 3600 \
  --cli-input-json "${RM_JOB_INPUT_JSON}" \
  > robomaker-${JOB_ID}.json

# Store the job details for reference
aws s3 cp \
  robomaker-${JOB_ID}.json \
  "s3://${S3_BUCKET}/${EVALUATION_PREFIX}"

echo "Poll evaluation results with: "
echo "  aws s3 cp s3://${S3_BUCKET}/${EVALUATION_METRICS_KEY} - | jq '.'"

exit 0
