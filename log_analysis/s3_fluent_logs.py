'''
Download local training logs backed up to s3, organized by job id
'''

import boto3
import os
import glob
import pandas as pd

EPISODE_PER_ITER=20

# Download all the log files for a session
def download_logs(s3_bucket, s3_log_path, dest_dir):
    client = boto3.client('s3')
    response = client.list_objects_v2(
        Bucket=s3_bucket,
        Prefix=s3_log_path)
    if 'Contents' in response:
      print("Found %d files in s3://%s/%s" % (len(response['Contents']), s3_bucket, s3_log_path))
      for log in response['Contents']:
        fname = os.path.basename(log['Key'])
        resource = boto3.resource('s3')
        dest_fname = os.path.join(dest_dir, fname)
        if not os.path.isdir(dest_dir):
          os.mkdir(dest_dir)
        if os.path.isfile(dest_fname) == False or os.stat(dest_fname).st_size != log['Size']:
          print("Downloading %s from %s to %s" % (fname, log['Key'], dest_fname))
          resource.Bucket(s3_bucket).download_file(log['Key'], dest_fname)
        else:
          print("Skipping previously downloaded file %s" % fname)
    else:
      print("No files found in s3://%s/%s" % (s3_bucket, s3_log_path))

# Get the launch sequence summary to confirm that it went successfully
def extract_summary(dest_dir):
  signatures = list(
    # (container, log)
    ('simulation', 'roslaunch server'),   # simulation: ROS started
    ('training', 'Successfully downloaded model metadata'),
    ('training', 'Uploaded hyperparameters.json'),
    ('training', 'Restoring pretrained model'),
    ('training', 'Loaded action space from file'),
    ('simulation', '/opt/amazon/RoboMakerGazebo/bin/gzserver -s'),
    ('simulation', 'python3 -m markov.rollout_worker'),
    ('simulation', 'Successfully downloaded model metadata'),
    ('simulation', 'Received IP from SageMaker successfully'),
    ('simulation', 'Received Sagemaker hyperparameters successfully!'),
    ('simulation', 'Connecting to redis'),
    ('training', 'Created TensorFlow device'),
    ('training', 'Loading checkpoint'),
    ('training', 'Checkpoint> Saving in path'),
    ('training', 'Connecting to redis at'),
    ('training', 'Subscribing to redis pubsub channel')
    ('simulation', 'Loaded action space from file'),
    ('simulation', 'Loading checkpoint'),
    ('simulation', 'Connecting to redis'),
    ('simulation', 'SIM_TRACE')
  )

# Get the data for policy training based on experiences received from rollout workers
def extract_training_epochs(dest_dir):
  df_list = list()
  for fname in glob.glob(os.path.join(dest_dir, '*')):
    df = pd.read_json(fname, lines=True)
    if not 'log' in df.columns:
      continue
    training_logs = df[df['log'].str.contains('KL divergence', na=False)]
    for _,row in training_logs.iterrows():
      # "log":"Policy training> Surrogate loss=-0.08960115909576416, KL divergence=0.031318552792072296, Entropy=3.070063352584839, training epoch=3, learning_rate=0.0003\r"
      parts = row['log'].split("Policy training> ")[1].strip().split(',')
      surrogate_loss = float(parts[0].split('Surrogate loss=')[1])
      kl_divergence = float(parts[1].split('KL divergence=')[1])
      entropy = float(parts[2].split('Entropy=')[1])
      epoch = float(parts[3].split('training epoch=')[1])
      learning_rate = float(parts[4].split('learning_rate=')[1])

      # "log_time":"2019-09-19T20:14:31+00:00"
      timestamp = row['log_time']
      df_list.append((timestamp, surrogate_loss, kl_divergence, entropy, epoch, learning_rate))

  columns = ['timestamp', 'surrogate_loss', 'kl_divergence', 'entropy', 'epoch', 'learning_rate']
  return pd.DataFrame(df_list, columns=columns).sort_values('timestamp',axis='index').reset_index(drop=True)

# Get the experience iteration summary upon receipt from rollout workers
def extract_training_iterations(dest_dir):
  df_list = list()
  for fname in glob.glob(os.path.join(dest_dir, '*')):
    df = pd.read_json(fname, lines=True)
    if not 'log' in df.columns:
      continue
    df = df.dropna(subset=['log'])
    training_logs = df[df['container_name'].str.contains('dr-training', na=False)]
    training_logs = training_logs[training_logs['log'].str.contains('Name=main_level/agent', na=False)]
    for _,row in training_logs.iterrows():
      # "log":"Training> Name=main_level/agent, Worker=0, Episode=781, Total reward=67.4, Steps=20564, Training iteration=39\r","container_id":"8963076f3fa49d5c0aac3129ba277675445e45819daf31505b41647ca2c2ec84","container_name":"/dr-training","log_time":"2019-09-20T06:02:54+00:00"}
      parts = row['log'].split("Training> ")[1].strip().split(',')
      name = parts[0].split('Name=')[1]
      worker = int(parts[1].split('Worker=')[1])
      episode = int(parts[2].split('Episode=')[1])
      reward = float(parts[3].split('Total reward=')[1])
      steps = int(parts[4].split('Steps=')[1])
      iteration = int(parts[5].split('Training iteration=')[1])

      # "log_time":"2019-09-19T20:14:31+00:00"
      timestamp = row['log_time']
      df_list.append((timestamp, name, worker, episode, reward, steps, iteration))

  columns = ['timestamp', 'name', 'worker', 'episode', 'reward', 'steps','iteration']
  return pd.DataFrame(df_list, columns=columns).sort_values('timestamp',axis='index').reset_index(drop=True)


def extract_simulation(dest_dir):
  df_list = list()
  for fname in glob.glob(os.path.join(dest_dir, '*')):
    df = pd.read_json(fname, lines=True)
    if not 'log' in df.columns:
      continue
    df = df.dropna(subset=['log'])
    simulation_logs = df[df['log'].str.contains('SIM_TRACE_LOG', na=False)]
    for _,row in simulation_logs.iterrows():
      # "log":"SIM_TRACE_LOG:2,13,1.5996,-2.1772,-1.8202,0.17,8.50,20,4.1155,False,False,4.7425,25,22.92,1568923409.9931474"
      parts = row['log'].split("SIM_TRACE_LOG:")[1].strip().split(',')
      episode = int(parts[0])
      steps = int(parts[1])
      x = float(parts[2])
      y = float(parts[3])
      ##cWp = get_closest_waypoint(x, y, wpts)
      yaw = float(parts[4])
      steer = float(parts[5])
      throttle = float(parts[6])
      action = float(parts[7])
      reward = float(parts[8])
      done = 0 if 'False' in parts[9] else 1
      all_wheels_on_track = parts[10]
      progress = float(parts[11])
      closest_waypoint = int(parts[12])
      track_len = float(parts[13])
      tstamp = parts[14]
      if len(parts) > 15:
        # I added a simulation time field recently
        sim_time = float(parts[15])
      else:
        sim_time = 0.0

      # "log_time":"2019-09-19T20:03:29+00:00"
      timestamp = row['log_time']

      # TODO: Don't hard-code this
      iteration = int(episode / EPISODE_PER_ITER) +1
      df_list.append((iteration, episode, steps, x, y, yaw, steer, throttle, action, reward, done, all_wheels_on_track, progress,
                        closest_waypoint, track_len, tstamp, sim_time))

  columns = ['iteration', 'episode', 'steps', 'x', 'y', 'yaw', 'steer', 'throttle', 'action', 'reward', 'done', 'on_track', 'progress', 'closest_waypoint', 'track_len', 'timestamp', 'simtime']
  df = pd.DataFrame(df_list, columns=columns).sort_values('timestamp',axis='index')
  #ignore the first two dummy values that coach throws at the start.
  df = df[2:]
  return df.reset_index(drop=True)
