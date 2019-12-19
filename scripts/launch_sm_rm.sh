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
  echo "  train <reward function path> <actions configuration path> <training parameters path>"
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
  if [ "x$2" == "x" -o "x$3" == "x" -o "x$4" == "x" ]; then
    usage
  fi
  if [ ! -r $2 ]; then
    echo "$2 is not readable"
    exit 1
  fi

  if [ ! -r $3 ]; then
    echo "$3 is not readable"
    exit 1
  fi

  if [ ! -r $4 ]; then
    echo "$4 is not readable"
    exit 1
  fi
  LOCAL_REWARD_FUNCTION_PATH=$2
  LOCAL_ACTIONS_CONFIG_PATH=$3
  TRAINING_PARAMETERS_PATH=$4
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
S3_PREFIX='DeepRacer-Manually-Invoked-Training-Jobs'


# ACCOUNT_ID: The AWS Account ID, useful for marking who initiated the
#             training jobs since they all use a shared S3 bucket
ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`


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
# SAGEMAKER TRAINING JOB
#=======================


# SAGEMAKER_OUTPUT_DATA_S3_PREFIX: Where the final model.tar.gz file will be
#                                  placed once training is complete
SM_S3_OUTPUT_PREFIX="${S3_PREFIX}/${JOB_ID}/DeepRacer-SageMaker-rlmdl-${ACCOUNT_ID}-${JOB_ID}"
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
  SM_RM_SHARED_PREFIX="${S3_PREFIX}/${JOB_ID}/DeepRacer-SageMaker-RoboMaker-comm-${ACCOUNT_ID}-${JOB_ID}/"
  # SM_S3_PRETRAINED_BUCKET
  if [ ! "x$pretrained_id" == "x" ]; then
    SM_S3_PRETRAINED_BUCKET="${S3_BUCKET}"
    SM_S3_PRETRAINED_PREFIX="${S3_PREFIX}/${pretrained_id}/DeepRacer-SageMaker-RoboMaker-comm-${ACCOUNT_ID}-${pretrained_id}"
  fi
else
  SM_RM_SHARED_PREFIX="${S3_PREFIX}/${EVALUATION_PRETRAINED_JOB_ID}/DeepRacer-SageMaker-RoboMaker-comm-${ACCOUNT_ID}-${EVALUATION_PRETRAINED_JOB_ID}/"
fi

# SM_JOB_JSON
SM_JOB_NAME=deepracer-${JOB_ID}

# See https://aws.amazon.com/sagemaker/pricing/
#
# Default is ml.c4.2xlarge, which is $0.557
# ml.c5.2xlarge is $0.476

SM_INSTANCE_TYPE="ml.c5.2xlarge"

#=======================
# ROBOMAKER JOB
#=======================

# RM_TRAINING_METRICS_PATH
RM_METRICS_S3_BUCKET="${S3_BUCKET}"

# RM_METRICS_S3_OBJECT_KEY
RM_METRICS_S3_PREFIX="${S3_PREFIX}/${JOB_ID}/DeepRacer-Metrics/"
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

# Dynamic robomaker app managed by AWS
#RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-051bbb71-b8cb-4898-a31f-979631825e54/1564689218391"
# Static robomaker app managed by me, locked to particular version
#RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-2019-07-31/1567038960461"
# First attempt at custom colcon bundle so we can start hacking on it
RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-custom-test/1567095466134"
RM_NUMBER_OF_WORKERS=1

# Unused for training, specifies a total number of episodes for the simulation to run
if [ "${COMMAND}" == "evaluate" ]; then
  RM_NUMBER_OF_TRIALS=5
else
  RM_NUMBER_OF_EPISODES=0
  RM_TRAINING_LAUNCH_FILE="distributed_training.launch"

  # parallel_training is our hand-coded support for multiple simultaneous
  # simulations feeding the same trainer
  # NOTE! This currently does not work
  #RM_TRAINING_LAUNCH_FILE="parallel_training.launch"
  #RM_APP_ARN="arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-distributed/1566183015534"
  #RM_NUMBER_OF_WORKERS=2
fi



#=======================
# CREATE S3 RESOURCES
#=======================


# Verify that bucket exists.  This should have been done with one-time
# setup of DR resources.
aws s3api get-bucket-acl --bucket ${S3_BUCKET} > /dev/null

if [ ! $? == 0 ]; then
  echo "Bucket ${S3_BUCKET} does not exist"
  exit 1
else
  echo "Bucket ${S3_BUCKET} exists"
fi

# Create empty folders in S3
create_and_verify_folder "${S3_PREFIX}"
if [ "${COMMAND}" == "train" ]; then
  # Only need to create these for training jobs
  create_and_verify_folder "${SM_RM_SHARED_PREFIX}"
  create_and_verify_folder "${SM_S3_OUTPUT_PREFIX}"
fi
create_and_verify_folder "${RM_METRICS_S3_PREFIX}"


if [ "${COMMAND}" == "train" ]; then

  # Upload reward and hyperparameter files
  echo -n "Uploading reward function to ${SM_S3_REWARD_FUNCTION_PATH}..."
  aws s3api put-object \
    --bucket "${S3_BUCKET}" \
    --key "${SM_S3_REWARD_FUNCTION_PATH}" \
    --metadata "Content-Type=text/x-python-script; charset=UTF-8" \
    --tagging "SageMaker=true" \
    --body "${LOCAL_REWARD_FUNCTION_PATH}" \
    > /dev/null 2>&1

  if [ ! $? == 0 ]; then
    echo "failed"
    exit 1
  else
    echo "done"
  fi
  
  echo -n "Uploading action space config to ${SM_S3_MODEL_METADATA_PATH}..."
  aws s3api put-object \
    --bucket "${S3_BUCKET}" \
    --key "${SM_S3_MODEL_METADATA_PATH}" \
    --metadata "Content-Type=application/json; charset=UTF-8" \
    --tagging "SageMaker=true" \
    --body "${LOCAL_ACTIONS_CONFIG_PATH}" \
    > /dev/null 2>&1

  if [ ! $? == 0 ]; then
    echo "failed"
    exit 1
  else
    echo "done"
  fi

  PRETRAINED_BUCKET_JSON_TAG=""
  PRETRAINED_PREFIX_JSON_TAG=""
  if [ ! "x${SM_S3_PRETRAINED_BUCKET}" == "x" ]; then
    PRETRAINED_BUCKET_JSON_TAG="\"pretrained_s3_bucket\": \"${SM_S3_PRETRAINED_BUCKET}\","
    PRETRAINED_PREFIX_JSON_TAG="\"pretrained_s3_prefix\": \"${SM_S3_PRETRAINED_PREFIX}\","
  fi

  SM_HYPERPARAMETERS_JSON="                                                       
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
    \"aws_region\": \"us-east-1\",                                                
    \"model_metadata_s3_key\": \"${SM_MODEL_METADATA_S3_KEY}\",                   
    ${PRETRAINED_BUCKET_JSON_TAG}
    ${PRETRAINED_PREFIX_JSON_TAG}
    \"pretrained_s3_bucket\": \"${SM_S3_PRETRAINED_BUCKET}\",                     
    \"pretrained_s3_prefix\": \"${SM_S3_PRETRAINED_PREFIX}\",                     
    \"reward_function_s3_source\": \"${SM_REWARD_FUNCTION_S3_SOURCE}\",
    \"s3_bucket\": \"${SM_RM_SHARED_BUCKET}\",                                    
    \"s3_prefix\": \"${SM_RM_SHARED_PREFIX}\",                                    
    \"stack_size\": \"${stack_size}\"                                             
  }"

  SM_JOB_INPUT_JSON="{
      \"TrainingJobName\": \"\",
      \"HyperParameters\": {
          \"KeyName\": \"\"
      },
      \"AlgorithmSpecification\": {
          \"TrainingImage\": \"220744436658.dkr.ecr.us-east-1.amazonaws.com/deepracersm:latest\",
          \"TrainingInputMode\": \"File\"
      },
      \"RoleArn\": \"arn:aws:iam::345864641105:role/service-role/AWSDeepRacerSageMakerAccessRole\",
      \"OutputDataConfig\": {
          \"KmsKeyId\": \"\",
          \"S3OutputPath\": \"\"
      },
      \"ResourceConfig\": {
          \"InstanceType\": \"${SM_INSTANCE_TYPE}\",
          \"InstanceCount\": 1,
          \"VolumeSizeInGB\": 10,
          \"VolumeKmsKeyId\": \"\"
      },
      \"VpcConfig\": {
          \"SecurityGroupIds\": [
              \"sg-0b9bd3a41e11cf278\"
          ],
          \"Subnets\": [
              \"subnet-0b462e2666bfc8b42\",
              \"subnet-0c17dcc711ca0d647\",
              \"subnet-0308c84b560b7523f\",
              \"subnet-02859793120cd62b1\",
              \"subnet-0907b942eaf144f31\",
              \"subnet-0f34973fdfcaac137\"
          ]
      },
      \"StoppingCondition\": {
          \"MaxRuntimeInSeconds\": 7200
      },
      \"Tags\": [
        {
          \"Key\": \"DeepRacer-Manually-Invoked-Training-Jobs\",
          \"Value\": \"true\"
        },
        {
          \"Key\": \"JOB_ID\", 
          \"Value\": \"${JOB_ID}\"
        }
      ]
  }"

  echo -n "Creating sagemaker training job..."
  aws sagemaker create-training-job \
    --training-job-name "${SM_JOB_NAME}" \
    --hyper-parameters "${SM_HYPERPARAMETERS_JSON}" \
    --stopping-condition "MaxRuntimeInSeconds=${job_duration}" \
    --output-data-config "S3OutputPath=${SM_S3_OUTPUT_PATH}" \
    --cli-input-json "${SM_JOB_INPUT_JSON}" \
    > sagemaker-${JOB_ID}.json


  SM_TRAINING_JOB_ARN=`jq -r '.TrainingJobArn' sagemaker-${JOB_ID}.json`
  echo "done ${SM_TRAINING_JOB_ARN}"

  #
  # TODO: Poll status of job until it is training.  Seems that Sagemaker takes
  #       a while to provision the machine and download the container
  #
  #
  #[18:20:43] gitlab-veeta-tv:deepracer $ aws sagemaker describe-training-job --training-job-name deepracer-20190813181737-62ECC629-5B16-4A51-9524-EC0D7D403CCD
  #{
  #    "TrainingJobName": "deepracer-20190813181737-62ECC629-5B16-4A51-9524-EC0D7D403CCD",
  #    "TrainingJobArn": "arn:aws:sagemaker:us-east-1:345864641105:training-job/deepracer-20190813181737-62ecc629-5b16-4a51-9524-ec0d7d403ccd",
  #    "TrainingJobStatus": "InProgress",
  #    "SecondaryStatus": "Training",
  #    ...

fi # train


#======================
# ROBOMAKER JOB - TRAINING AND EVALUATION
#======================

# Evaluation environment variables:
#
if [ "${COMMAND}" == "evaluate" ]; then
  RM_SIMULATION_JSON="[
  {                                                                       
    \"application\": \"${RM_APP_ARN}\",
    \"applicationVersion\": \"\$LATEST\",
    \"launchConfig\": {                                                   
      \"packageName\": \"deepracer_simulation_environment\",              
      \"launchFile\": \"evaluation.launch\",                    
      \"environmentVariables\": {                                       
        \"APP_REGION\":	\"us-east-1\",
        \"KINESIS_VIDEO_STREAM_NAME\": \"does-not-exist\",
        \"METRICS_S3_BUCKET\": \"${RM_METRICS_S3_BUCKET}\",
        \"METRICS_S3_OBJECT_KEY\": \"${RM_METRICS_S3_OBJECT_KEY}\",
        \"NUMBER_OF_TRIALS\":	\"${RM_NUMBER_OF_TRIALS}\",
        \"ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID\": \"${ACCOUNT_ID}\",
        \"MODEL_S3_BUCKET\":	\"${SM_RM_SHARED_BUCKET}\",
        \"MODEL_S3_PREFIX\":	\"${SM_RM_SHARED_PREFIX}\",
        \"WORLD_NAME\":	\"${world_name}\"
      }                                                               
    }                                                                   
  }
  ]"
  echo -n "Creating evaluation simulation job..."
else
  # train
  RM_SIMULATION_JSON="[
  {                                                                       
    \"application\": \"${RM_APP_ARN}\",
    \"applicationVersion\": \"\$LATEST\",
    \"launchConfig\": {                                                   
      \"packageName\": \"deepracer_simulation_environment\",              
      \"launchFile\": \"${RM_TRAINING_LAUNCH_FILE}\",
      \"environmentVariables\": {                                       
        \"APP_REGION\":	\"us-east-1\",
        \"KINESIS_VIDEO_STREAM_NAME\": \"does-not-exist\",
        \"METRICS_S3_BUCKET\": \"${RM_METRICS_S3_BUCKET}\",
        \"METRICS_S3_OBJECT_KEY\": \"${RM_METRICS_S3_OBJECT_KEY}\",
        \"METRIC_NAME\": \"TrainingRewardScore\",
        \"METRIC_NAMESPACE\":	\"AWSDeepRacer\",
        \"MODEL_METADATA_FILE_S3_KEY\":	\"${RM_MODEL_METADATA_FILE_S3_KEY}\",
        \"NUMBER_OF_EPISODES\":	\"${RM_NUMBER_OF_EPISODES}\",
        \"REWARD_FILE_S3_KEY\":	\"${RM_REWARD_FILE_S3_KEY}\",
        \"ROBOMAKER_SIMULATION_JOB_ACCOUNT_ID\": \"${ACCOUNT_ID}\",
        \"SAGEMAKER_SHARED_S3_BUCKET\":	\"${SM_RM_SHARED_BUCKET}\",
        \"SAGEMAKER_SHARED_S3_PREFIX\":	\"${SM_RM_SHARED_PREFIX}\",
        \"TARGET_REWARD_SCORE\": \"None\",
        \"TRAINING_JOB_ARN\":	\"${SM_TRAINING_JOB_ARN}\",
        \"WORLD_NAME\":	\"${world_name}\"
      }                                                               
    }                                                                   
  }
  ]"
  echo -n "Creating ${RM_NUMBER_OF_WORKERS} training simulation job(s)..."
fi

for i in $(seq 1 $RM_NUMBER_OF_WORKERS); do
  WORKER_ID=$i
  RM_JOB_INPUT_JSON="{
    \"clientRequestToken\": \"\",
    \"maxJobDurationInSeconds\": 0,
    \"iamRole\": \"arn:aws:iam::345864641105:role/service-role/AWSDeepRacerRoboMakerAccessRole\",
    \"failureBehavior\": \"Fail\",
    \"simulationApplications\": ${RM_SIMULATION_JSON},
    \"tags\": {
      \"DeepRacer-Manually-Invoked-Training-Jobs\": \"true\",
      \"JOB_ID\": \"${JOB_ID}\",
      \"WORKER_ID\": \"${WORKER_ID}\"
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

  aws robomaker create-simulation-job \
    --client-request-token "${JOB_ID}-${WORKER_ID}" \
    --max-job-duration-in-seconds "${job_duration}" \
    --cli-input-json "${RM_JOB_INPUT_JSON}" \
    > robomaker-${COMMAND}-${JOB_ID}-${WORKER_ID}.json
  echo -n " ${WORKER_ID}"
done

echo " done"

exit 0
