#!/bin/bash

# S3_BUCKET: Bucket that stores training data for all                           
#                      training jobs.                                           
S3_BUCKET='aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62'                  

S3_KEY=deepracer-simapp-custom.tar.gz 
                                                                                
# WARNING!! This overwrites the existing S3 object
aws s3 cp \
  build/deepracer-simapp-custom.tar.gz \
  s3://${S3_BUCKET}/${S3_KEY}

aws robomaker update-simulation-application \
  --application 'arn:aws:robomaker:us-east-1:345864641105:simulation-application/deepracer-simapp-custom-test/1567095466134' \
  --rendering-engine name=OGRE,version=1.x \
  --simulation-software-suite name=Gazebo,version=7 \
  --robot-software-suite name=ROS,version=Kinetic \
  --sources architecture=X86_64,s3Bucket=${S3_BUCKET},s3Key=${S3_KEY}
