'''
Download model checkpoints for analysis
'''

import boto3
import os
import glob
import pandas as pd

def list_available_checkpoints(s3_bucket, s3_model_path, dest_dir):
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=s3_bucket,
        Prefix=s3_model_path)
    checkpoints = list()
    if 'Contents' in response:
      # Model directories have for each checkpoint:
      #   {n}_Step-{m}.ckpt.meta
      #   {n}_Step-{m}.ckpt.index
      #   {n}_Step-{m}.ckpt.data-00000-of-00001
      #   checkpoint
      #   model_{n}.pb
      #
      for model in response['Contents']:
        if model['Key'].endswith('.pb'):
          checkpoints.append(os.path.basename(model['Key']))

    return checkpoints

def download_checkpoint(s3_bucket, s3_model_path, model_name, dest_dir):
    resource = boto3.resource('s3')
    dest_fname = os.path.join(dest_dir, model_name)
    if not os.path.isdir(dest_dir):
      os.makedirs(dest_dir, exist_ok=True)
    if not os.path.exists(dest_fname):
      client = boto3.client('s3')
      client.download_file(s3_bucket, 
                           os.path.join(s3_model_path, model_name), 
                           dest_fname)
    return dest_fname

def download_actions(s3_bucket, s3_model_path, dest_dir):
    resource = boto3.resource('s3')
    dest_fname = os.path.join(dest_dir, 'model_metadata.json')
    if not os.path.isdir(dest_dir):
      os.makedirs(dest_dir, exist_ok=True)
    if not os.path.exists(dest_fname):
      client = boto3.client('s3')
      client.download_file(s3_bucket, 
                           os.path.join(s3_model_path, 'model_metadata.json'), 
                           dest_fname)
    return dest_fname

