#!/bin/bash
# '''
# Generate the S3 paths needed for manually invoking a SageMaker+Robomaker
# training session
# '''

#set -x
set -e

usage() {
  echo "Usage: $0 <command> [command arguments]"
  echo
  echo "Commands:"
  echo
  echo "  train <training inputs path>"
  echo
  echo "  evaluate <training job id> <track>"
  echo
  exit 1
}

if [ "x$1" == "x" ]; then
  usage
fi

COMMAND=$1

# Training
if [ "${COMMAND}" == "train" ]; then
  if [ "x$2" == "x" ]; then
    usage
  fi
  if [ ! -d $2 ]; then
    echo "$2 does not exist or is not a directory"
    exit 1
  fi

  TRAINING_INPUTS_PATH=$2
  LOCAL_REWARD_FUNCTION_PATH="${TRAINING_INPUTS_PATH}/reward.py"
  LOCAL_ACTIONS_CONFIG_PATH="${TRAINING_INPUTS_PATH}/model_metadata.json"
  TRAINING_PARAMETERS_PATH="${TRAINING_INPUTS_PATH}/training-parameters.env"

  if [ ! -r $LOCAL_REWARD_FUNCTION_PATH ]; then
    echo "${LOCAL_REWARD_FUNCTION_PATH} is not readable"
    exit 1
  fi

  if [ ! -r $LOCAL_ACTIONS_CONFIG_PATH ]; then
    echo "${LOCAL_ACTIONS_CONFIG_PATH} is not readable"
    exit 1
  fi

  if [ ! -r $TRAINING_PARAMETERS_PATH ]; then
    echo "${TRAINING_PARAMETERS_PATH} is not readable"
    exit 1
  fi

  source ${TRAINING_PARAMETERS_PATH}

# Evaluating
elif [ "${COMMAND}" == "evaluate" ]; then
  if [ "x$2" == "x" -o "x$3" == "x" ]; then
    usage
  fi
  EVALUATION_PRETRAINED_JOB_ID=$2
  world_name=$3
  job_duration="1200"
else
  usage
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
S3_BUCKET='dr-local'

# S3_PREFIX: Path prefix under which data is stored for
#            all training sessions
S3_PREFIX='training-jobs'


# ACCOUNT_ID: The AWS Account ID, useful for marking who initiated the
#             training jobs since they all use a shared S3 bucket
#ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`


# default
AWSCMD="aws"

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
  AWS_ACCESS_KEY_ID=minio AWS_SECRET_ACCESS_KEY=miniokey aws \
        --endpoint-url=http://${MINIO_IP}:9000 \
  	s3api get-object-acl --bucket ${S3_BUCKET} --key ${CREATE_FOLDER_PATH} > /dev/null 2>&1
  RESULT=$?
  set -e
  if [ ! $RESULT == 0 ]; then
    # Try to create it
    echo -n "Creating $1..."
    AWS_ACCESS_KEY_ID=minio AWS_SECRET_ACCESS_KEY=miniokey aws \
          --endpoint-url=http://${MINIO_IP}:9000 \
          s3api put-object --bucket ${S3_BUCKET} --key ${CREATE_FOLDER_PATH} > /dev/null 2>&1
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
# SAGEMAKER TRAINING JOB
#=======================


# SAGEMAKER_OUTPUT_DATA_S3_PREFIX: Where the final model.tar.gz file will be
#                                  placed once training is complete
SM_S3_OUTPUT_PREFIX="${S3_PREFIX}/${JOB_ID}/output/"
SM_S3_OUTPUT_PATH="s3://${S3_BUCKET}/${SM_S3_OUTPUT_PREFIX}/"

# SM_S3_REWARD_FUNCTION_PATH
SM_S3_REWARD_FUNCTION_PATH="${S3_PREFIX}/${JOB_ID}/reward.py"
SM_REWARD_FUNCTION_S3_SOURCE="s3://${S3_BUCKET}/${SM_S3_REWARD_FUNCTION_PATH}"

# SM_S3_MODEL_METADATA_PATH
SM_S3_MODEL_METADATA_PATH="${S3_PREFIX}/${JOB_ID}/model_metadata.json"
SM_MODEL_METADATA_S3_KEY="s3://${S3_BUCKET}/${SM_S3_MODEL_METADATA_PATH}"

# SM_RM_SHARED_PATH
SM_RM_SHARED_BUCKET="${S3_BUCKET}"
if [ "${COMMAND}" == "train" ]; then
  SM_RM_SHARED_PREFIX="${S3_PREFIX}/${JOB_ID}/shared/"
  # SM_S3_PRETRAINED_BUCKET
  if [ ! "x$pretrained_id" == "x" ]; then
    SM_S3_PRETRAINED_BUCKET="${S3_BUCKET}"
    SM_S3_PRETRAINED_PREFIX="${S3_PREFIX}/${pretrained_id}/shared/"
  fi
else
  SM_RM_SHARED_PREFIX="${S3_PREFIX}/${EVALUATION_PRETRAINED_JOB_ID}/shared/"
fi



#=======================
# ROBOMAKER JOB
#=======================

# RM_TRAINING_METRICS_PATH
RM_METRICS_S3_BUCKET="${S3_BUCKET}"

# RM_METRICS_S3_OBJECT_KEY
RM_METRICS_S3_PREFIX="${S3_PREFIX}/${JOB_ID}/metrics/"
if [ "${COMMAND}" == "train" ]; then
  RM_METRICS_S3_OBJECT_KEY="${RM_METRICS_S3_PREFIX}TrainingMetrics-${ACCOUNT_ID}-${JOB_ID}.json"
else
  # Mark it with current job id so that we can run multiple evaluations on a single trained model
  RM_METRICS_S3_OBJECT_KEY="${RM_METRICS_S3_PREFIX}EvaluationMetrics-${ACCOUNT_ID}-${JOB_ID}.json"
fi

# RM_MODEL_METADATA_FILE_S3_KEY
RM_MODEL_METADATA_FILE_S3_KEY="${S3_PREFIX}/${JOB_ID}/model_metadata.json"

RM_SIMULATION_JOB_ACCOUNT_ID="${ACCOUNT_ID}"

RM_REWARD_FILE_S3_KEY="${S3_PREFIX}/${JOB_ID}/reward.py"

#=======
# CLEAN SLATE START
#=======
docker-compose down

#=======================
# CREATE S3 RESOURCES
#=======================

# Verify that s3 bucket exists.  This should have been done with one-time
# setup of DR resources.
UPLOADER_DEST_BUCKET=aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62 
aws s3api get-bucket-acl --bucket ${UPLOADER_DEST_BUCKET} > /dev/null

if [ ! $? == 0 ]; then
  echo "Bucket ${UPLOADER_DEST_BUCKET} does not exist"
  exit 1
else
  echo "Bucket ${UPLOADER_DEST_BUCKET} exists"
fi

export LOGGER_S3_DESTINATION_PATH="${S3_PREFIX}/${JOB_ID}/logs/"

#=======================
# TRAINING
#=======================


docker-compose up -d --no-deps dr-redis minio

MINIO_IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' minio`

# For minio run locally, it'll be port 9000
# Create empty folders in S3
create_and_verify_folder "${S3_PREFIX}"
if [ "${COMMAND}" == "train" ]; then
  # Only need to create these for training jobs
  create_and_verify_folder "${SM_RM_SHARED_PREFIX}"
  create_and_verify_folder "${SM_S3_OUTPUT_PREFIX}"
fi
create_and_verify_folder "${RM_METRICS_S3_PREFIX}"
create_and_verify_folder "${LOGGER_S3_DESTINATION_PATH}"


PRETRAINED_ARGS=""
if [ ! "x${SM_S3_PRETRAINED_BUCKET}" == "x" ]; then
  PRETRAINED_ARGS="--pretrained_s3_bucket ${SM_S3_PRETRAINED_BUCKET} --pretrained_s3_prefix ${SM_S3_PRETRAINED_PREFIX}"
fi

# TF TRAINING
if [ "${COMMAND}" == "train" ]; then
  DUMP_GIFS='false'
  if [ ! "x${dump_gifs}" == "x" ]; then
    DUMP_GIFS=${dump_gifs}
  fi
  DUMP_MP4='false'
  if [ ! "x${dump_mp4}" == "x" ]; then
    DUMP_MP4=${dump_mp4}
  fi
  # Default tensorboard to false
  TENSORBOARD='false'
  if [ ! "x${tensorboard}" == "x" ]; then
    TENSORBOARD=${tensorboard}
  fi
  LR_DECAY_RATE=0
  if [ ! "x${lr_decay_rate}" == "x" ]; then
    LR_DECAY_RATE=${lr_decay_rate}
  fi
  LR_DECAY_STEPS=0
  if [ ! "x${lr_decay_steps}" == "x" ]; then
    LR_DECAY_STEPS=${lr_decay_steps}
  fi
else
  # evaluation
  DUMP_GIFS='true'
  DUMP_MP4='true'
fi

export SM_TRAINING_ENV="{\"hyperparameters\":
  {
    \"batch_size\": \"${batch_size}\",
    \"beta_entropy\": \"${beta_entropy}\",
    \"discount_factor\": \"${discount_factor}\",
    \"e_greedy_value\": \"${e_greedy_value}\",
    \"epsilon_steps\": \"${epsilon_steps}\",
    \"exploration_type\": \"${exploration_type}\",
    \"loss_type\": \"${loss_type}\",
    \"lr\": \"${lr}\",
    \"lr_decay_rate\": \"${LR_DECAY_RATE}\",
    \"lr_decay_steps\": \"${LR_DECAY_STEPS}\",
    \"num_episodes_between_training\": \"${num_episodes_between_training}\",
    \"num_epochs\": \"${num_epochs}\",
    \"stack_size\": \"${stack_size}\",
    \"term_cond_avg_score\": \"${term_cond_avg_score}\",
    \"term_cond_max_episodes\": \"${term_cond_max_episodes}\",
    \"tensorboard\": ${TENSORBOARD},
    \"dump_gifs\": ${DUMP_GIFS},
    \"dump_mp4\": ${DUMP_MP4}
  }}"
export JOB_ID
export APP_REGION=us-east-1
export AWS_ENDPOINT_URL="http://${MINIO_IP}:9000"
export KINESIS_VIDEO_STREAM_NAME=does-not-exist
export NUMBER_OF_EPISODES=0
export NUMBER_OF_TRIALS=0
export WORLD_NAME=${world_name}
export TARGET_REWARD_SCORE=None
export METRIC_NAME=TrainingRewardScore
export METRIC_NAMESPACE=AWSDeepRacer
export METRICS_S3_BUCKET=${SM_RM_SHARED_BUCKET}
export METRICS_S3_OBJECT_KEY=${RM_METRICS_S3_OBJECT_KEY}
export MODEL_METADATA_FILE_S3_KEY=${SM_S3_MODEL_METADATA_PATH}
export MODEL_S3_BUCKET=${SM_RM_SHARED_BUCKET}
export MODEL_S3_PREFIX=${SM_RM_SHARED_PREFIX}
export REWARD_FILE_S3_KEY=${SM_S3_REWARD_FUNCTION_PATH}
export ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID=${ACCOUNT_ID}
export SAGEMAKER_SHARED_S3_BUCKET=${SM_RM_SHARED_BUCKET}
export SAGEMAKER_SHARED_S3_PREFIX=${SM_RM_SHARED_PREFIX}
export TRAINING_JOB_ARN=fake-arn
export MAX_JOB_DURATION=${job_duration}
export AWS_ROBOMAKER_SIMULATION_JOB_ARN=fake-arn
export AWS_ROBOMAKER_SIMULATION_JOB_ID=fake-job-id
export AWS_ROBOMAKER_SIMULATION_RUN_ID=fake-run-id
export AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP="BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp source /home/robomaker/workspace/bundle-store/deepracer-simapp/setup.sh; export BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp;"
export ROBOMAKER_ROS_MASTER_URI="http://127.0.0.1:11311"
export ROBOMAKER_GAZEBO_MASTER_URI="http://127.0.0.1:11345"
export UPLOADER_S3_DESTINATION_URL="s3://aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62/${S3_PREFIX}/${JOB_ID}"
export UPLOADER_SOURCE_PATH="${S3_BUCKET}/${S3_PREFIX}/${JOB_ID}"
export LAUNCH_FILE=distributed_training.launch
export DISPLAY
if [ ! "x${start_position}" == "x" ]; then
  export START_POSITION=${start_position}
fi
if [ ! "x${change_start_position}" == "x" ]; then
  export CHANGE_START_POSITION=${change_start_position}
fi
if [ ! "x${alternate_driving_direction}" == "x" ]; then
  export ALTERNATE_DRIVING_DIRECTION=${alternate_driving_direction}
fi
if [ ! "x${sim_update_rate}" == "x" ]; then
  export SIM_UPDATE_RATE=${sim_update_rate}
fi

export TRAINING_WORKER_ARGS="--aws_region ${APP_REGION} --model_metadata_s3_key ${MODEL_METADATA_FILE_S3_KEY} --checkpoint-dir ${SAGEMAKER_SHARED_S3_PREFIX} --s3_bucket ${SAGEMAKER_SHARED_S3_BUCKET} --s3_prefix ${SAGEMAKER_SHARED_S3_PREFIX} ${PRETRAINED_ARGS}"

if [ "${COMMAND}" == "train" ]; then

  # Upload reward and hyperparameter files
  echo -n "Uploading reward function to ${SM_S3_REWARD_FUNCTION_PATH}..."
  AWS_ACCESS_KEY_ID=minio AWS_SECRET_ACCESS_KEY=miniokey aws \
    --endpoint-url=http://${MINIO_IP}:9000 \
    s3api put-object \
    --bucket "${S3_BUCKET}" \
    --key "${SM_S3_REWARD_FUNCTION_PATH}" \
    --metadata "Content-Type=text/x-python-script; charset=UTF-8" \
    --body "${LOCAL_REWARD_FUNCTION_PATH}"  \
    > /dev/null 2>&1

  if [ ! $? == 0 ]; then
    echo "failed"
    exit 1
  else
    echo "done"
  fi
  
  echo -n "Uploading action space config to ${SM_S3_MODEL_METADATA_PATH}..."
  AWS_ACCESS_KEY_ID=minio AWS_SECRET_ACCESS_KEY=miniokey aws \
    --endpoint-url=http://${MINIO_IP}:9000 \
    s3api put-object \
    --bucket "${S3_BUCKET}" \
    --key "${SM_S3_MODEL_METADATA_PATH}" \
    --metadata "Content-Type=application/json; charset=UTF-8" \
    --body "${LOCAL_ACTIONS_CONFIG_PATH}" \
    > /dev/null 2>&1

  if [ ! $? == 0 ]; then
    echo "failed"
    exit 1
  else
    echo "done"
  fi

  echo -n "Creating training job..."
  docker-compose up --no-recreate -d

else

  # NOTE!!! This can only work for models that are cached locally

  EVALUATION_MODEL_PREFIX="${S3_PREFIX}/${EVALUATION_PRETRAINED_JOB_ID}/shared/"

  # model to be evaluated
  export MODEL_S3_BUCKET=${SM_RM_SHARED_BUCKET}
  export MODEL_S3_PREFIX=${EVALUATION_MODEL_PREFIX}
  export NUMBER_OF_TRIALS=5
  export LAUNCH_FILE=evaluation.launch

  # Don't include dr-training for evaluation sessions
  echo -n "Creating evaluation job..."
  docker-compose up --no-recreate -d dr-simulation

fi # train

