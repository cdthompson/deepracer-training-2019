import boto3
import botocore
import json
import re
import requests
from requests_aws4auth import AWS4Auth


region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-veera-346apxkqjujdihhftplt7w42mu.us-east-1.es.amazonaws.com' # the Amazon ES domain, including https://
index = 'lambda-s3-index'
type = 'lambda-type'
url = host + '/' + index + '/' + type

headers = { "Content-Type": "application/json" }

s3 = boto3.client('s3')

# Regular expressions used to parse some simple log lines
key_pattern = re.compile('.*/logs/\d+_\d+.json')

# Lambda execution starts here
def handler(event, context):
    for record in event['Records']:

        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print("Lambda triggered on %s:%s" % (bucket,key))

        if key_pattern.match(key) is not None:
            # Get, read, and split the file into lines
            try:
                obj = s3.get_object(Bucket=bucket, Key=key)
                body = obj['Body'].read()
                lines = body.splitlines()
                print("Forwarding to ElasticSearch")
                for line in lines:
                    r = requests.post(url, auth=awsauth, data=line, headers=headers)
                    r.raise_for_status()
            except botocore.exceptions.ClientError as e:
                print("S3 get_object failed with: {}".format(e.response["Error"]["Code"]))
        else:
            print("Ignoring non-matching log file")
