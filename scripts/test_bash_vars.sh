
SM_MODEL_METADATA_S3_KEY="AAA"
SM_S3_PRETRAINED_BUCKET="AAA"
SM_S3_PRETRAINED_PREFIX="AAA"
SM_REWARD_FUNCTION_S3_SOURCE="AAA"
SM_RM_SHARED_BUCKET="AAA"
SM_RM_SHARED_PREFIX="AAA"
#TEMPLATE=`cat sagemaker-job-hyperparameters2.json`
source sagemaker_job_hyperparameters.env

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
  \"pretrained_s3_bucket\": \"${SM_S3_PRETRAINED_BUCKET}\",
  \"pretrained_s3_prefix\": \"${SM_S3_PRETRAINED_PREFIX}\",
  \"reward_function_s3_source\": \"${SM_REWARD_FUNCTION_S3_SOURCE}\",
  \"s3_bucket\": \"${SM_RM_SHARED_BUCKET}\",
  \"s3_prefix\": \"${SM_RM_SHARED_PREFIX}\",
  \"stack_size\": \"${stack_size}\"
}"          

echo ${TEMPLATE}

echo ${SM_HYPERPARAMETERS_JSON}
