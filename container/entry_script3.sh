#!/bin/bash

set -ex

eval $AWS_ROBOMAKER_SIMULATION_APPLICATION_SETUP

ARGS=""
#    parser.add_argument('-pk', '--preset_s3_key',
#                        help="(string) Name of a preset to download from S3",
#                        type=str,
#                        required=False)
#    parser.add_argument('-ek', '--environment_s3_key',
#                        help="(string) Name of an environment file to download from S3",
#                        type=str,
#                        required=False)


#    parser.add_argument('--model_metadata_s3_key',
#                        help="(string) Model Metadata File S3 Key",
#                        type=str,
#                        required=False)
ARGS="${ARGS} --model_metadata_s3_key ${model_metadata_s3_key}"

#    parser.add_argument('-c', '--checkpoint-dir',
#                        help='(string) Path to a folder containing a checkpoint to write the model to.',
#                        type=str,
#                        default='./checkpoint')
ARGS="${ARGS} --checkpoint-dir ${s3_prefix}"

#    parser.add_argument('--s3_prefix',
#                        help='(string) S3 prefix',
#                        type=str,
#                        default='sagemaker')
ARGS="${ARGS} --s3_prefix ${s3_prefix}"

#    parser.add_argument('--pretrained-checkpoint-dir',
#                        help='(string) Path to a folder for downloading a pre-trained model',
#                        type=str,
#                        default=PRETRAINED_MODEL_DIR)

#    parser.add_argument('--s3_bucket',
#                        help='(string) S3 bucket',
#                        type=str,
#                        default=os.environ.get("SAGEMAKER_SHARED_S3_BUCKET_PATH", "gsaur-test"))
ARGS="${ARGS} --s3_bucket ${s3_bucket}"

#    parser.add_argument('--framework',
#                        help='(string) tensorflow or mxnet',
#                        type=str,
#                        default='tensorflow')

#    parser.add_argument('--pretrained_s3_bucket',
#                        help='(string) S3 bucket for pre-trained model',
#                        type=str)
ARGS="${ARGS} --pretrained_s3_bucket ${pretrained_s3_bucket}"

#    parser.add_argument('--pretrained_s3_prefix',
#                        help='(string) S3 prefix for pre-trained model',
#                        type=str,
#                        default='sagemaker')
ARGS="${ARGS} --pretrained_s3_prefix ${pretrained_s3_prefix}"

#    parser.add_argument('--aws_region',
#                        help='(string) AWS region',
#                        type=str,
#                        default=os.environ.get("AWS_REGION", "us-east-1"))
ARGS="${ARGS} --aws_region ${aws_region}"

export PYTHONUNBUFFERED=1

python3 -m markov.training_worker ${ARGS}

