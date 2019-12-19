#!/bin/bash
# Launch the robomaker simapp container

set -x

# Generate a unique job id
DATE=`date "+%Y%m%d%H%M%S"`
JOB_UUID=`uuidgen`
JOB_ID="${DATE}-${JOB_UUID}"

#===================================================================
# Location: SageMakerRoboMaker, Local, or... something else later
#===================================================================


# SageMaker/RoboMaker launch
#JOB_S3_BUCKET=aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62
#JOB_S3_PREFIX=dr-sm-rm-${JOB_ID}

# TODO: EC2/ECS/EKS launches

# Local training launch (using minio)
JOB_S3_BUCKET=data
JOB_S3_PREFIX="dr-local-${JOB_ID}"
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=miniokey


#===================================================================
# SIMULATION
#===================================================================

# INPUTS TO SIMULATION
export ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID=345864641105
export APP_REGION=us-east-1
export WORLD_NAME=Mexico_track
export KINESIS_VIDEO_STREAM_NAME=does-not-exist
export PACKAGE_NAME=deepracer_simulation_environment
export ALTERNATE_DRIVING_DIRECTION=False
export TARGET_REWARD_SCORE=None
export METRIC_NAME=TrainingRewardScore
export METRIC_NAMESPACE=AWSDeepRacer
export METRICS_S3_BUCKET=${JOB_S3_BUCKET}
export NODE_TYPE=SIMULATION_WORKER

# TRAINING
export NUMBER_OF_EPISODES=0
export LAUNCH_FILE=distributed_training.launch
export METRICS_S3_OBJECT_KEY=evaluation-metrics.json
export MODEL_METADATA_FILE_S3_KEY=${JOB_S3_PREFIX}/model_metadata.json
export REWARD_FILE_S3_KEY=${JOB_S3_PREFIX}/reward_function.py
export SAGEMAKER_SHARED_S3_BUCKET=${JOB_S3_BUCKET}
export SAGEMAKER_SHARED_S3_PREFIX=${JOB_S3_PREFIX}

# EVALUATION
#export NUMBER_OF_TRIALS=0
#export LAUNCH_FILE=evaluation.launch
#export METRICS_S3_OBJECT_KEY=training-metrics.json
#export MODEL_S3_BUCKET=aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62
#export MODEL_S3_PREFIX=deepracer-custom-simulation-5-comm

# TF TRAINING
export XSM_TRAINING_ENV="{\"hyperparameters\":
  {
    \"batch_size\": \"${batch_size}\",
    \"beta_entropy\": \"${beta_entropy}\",
    \"discount_factor\": \"${discount_factor}\",
    \"e_greedy_value\": \"${e_greedy_value}\",
    \"epsilon_steps\": \"${epsilon_steps}\",
    \"exploration_type\": \"${exploration_type}\",
    \"loss_type\": \"${loss_type}\",
    \"lr\": \"${lr}\",
    \"num_episodes_between_training\": \"${num_episodes_between_training}\",
    \"num_epochs\": \"${num_epochs}\",
    \"stack_size\": \"${stack_size}\",
    \"term_cond_avg_score\": \"${term_cond_avg_score}\",
    \"term_cond_max_episodes\": \"${term_cond_max_episodes}\",
  }}"



export AWS_ROBOMAKER_SIMULATION_JOB_ARN=fake-arn
export AWS_ROBOMAKER_SIMULATION_JOB_ID=fake-job-id
export AWS_ROBOMAKER_SIMULATION_RUN_ID=fake-run-id
export AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP="BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp source /home/robomaker/workspace/bundle-store/deepracer-simapp/setup.sh; export BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp;"

# Docker helpers
CONTAINER_NAME=dr
COMMAND="/home/robomaker/entry_script2.sh stdbuf -oL -eL roslaunch ${PACKAGE_NAME} ${LAUNCH_FILE}"


# TRAINING WORKER / SAGEMEKER ONLY
#ARGS="--aws_region ${APP_REGION} --model_metadata_s3_key ${MODEL_METADATA_FILE_S3_KEY} --checkpoint-dir ${SAGEMAKER_SHARED_S3_PREFIX} --s3_bucket ${SAGEMAKER_SHARED_S3_BUCKET} --s3_prefix ${SAGEMAKER_SHARED_S3_PREFIX}"
#COMMAND="/home/robomaker/entry_script2.sh python3 -m markov.training_worker ${ARGS}"
#export NODE_TYPE=SAGEMAKER_TRAINING_WORKER



# Run training
docker run -i \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_ROBOMAKER_SIMULATION_JOB_ARN \
  -e AWS_ROBOMAKER_SIMULATION_JOB_ID \
  -e AWS_ROBOMAKER_SIMULATION_RUN_ID \
  -e AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP="BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp source /home/robomaker/workspace/bundle-store/deepracer-simapp/setup.sh; export BUNDLE_CURRENT_PREFIX=/home/robomaker/workspace/bundle-store/deepracer-simapp;" \
  -e 'ROBOMAKER_ROS_MASTER_URI=http://127.0.0.1:44269' \
  -e 'ROBOMAKER_GAZEBO_MASTER_URI=http://127.0.0.1:44269' \
  -e APP_REGION \
  -e KINESIS_VIDEO_STREAM_NAME \
  -e NUMBER_OF_TRIALS \
  -e NUMBER_OF_EPISODES \
  -e WORLD_NAME \
  -e ALTERNATE_DRIVING_DIRECTION \
  -e TARGET_REWARD_SCORE \
  -e METRIC_NAME \
  -e METRIC_NAMESPACE \
  -e METRICS_S3_BUCKET \
  -e METRICS_S3_OBJECT_KEY \
  -e MODEL_METADATA_FILE_S3_KEY \
  -e REWARD_FILE_S3_KEY \
  -e MODEL_S3_BUCKET \
  -e MODEL_S3_PREFIX \
  -e ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID \
  -e SAGEMAKER_SHARED_S3_BUCKET \
  -e SAGEMAKER_SHARED_S3_PREFIX \
  -e 'TRAINING_JOB_ARN=arn:aws:sagemaker:us-east-1:345864641105:training-job/test-robomaker-sagemaker-job' \
  -e SM_TRAINING_ENV \
  -e "aws_region=${APP_REGION}" \
  -e "model_metadata_s3_key=${MODEL_METADATA_FILE_S3_KEY}" \
  -e "reward_function_s3_source=${REWARRD_FILE_S3_KEY}" \
  -e "s3_bucket=${SAGEMAKER_SHARED_S3_BUCKET}" \
  -e "s3_prefix=${SAGEMAKER_SHARED_S3_PREFIX}" \
  -e NODE_TYPE \
  -w /home/robomaker/workspace/bundle-store/deepracer-simapp/ \
  -t \
  --name ${CONTAINER_NAME} \
  --rm \
  deepracer-robomaker-container:latest \
  "${COMMAND}"

#  bash
#  'bash -c "eval ${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP} /home/robomaker/entry_script.sh stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch"'


#  env

#  'bash -c "${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP} stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch"'

#  'bash -c "${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP} stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch"'

#  'bash -c "set -ex;${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP} exec stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch"'

#  'bash -c "set -ex;${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP} env"'

#  'bash -c set -ex;${AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP}; cd /home/robomaker/workspace/bundle-store/deepracer-simapp; /home/robomaker/entry_script.sh stdbuf -oL -eL roslaunch deepracer_simulation_environment distributed_training.launch'

####
exit 0
####

# Attach gazebo to the running container (or maybe just launch a new one?)
docker exec -i \
  -e "DISPLAY" \
  -e "QT_X11_NO_MITSHM=1" \
