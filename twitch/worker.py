'''
Background worker to download logs and generate assets
'''
import json
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
plt.ioff()
import mpld3
import numpy as np
import os.path
import pandas as pd
import s3_fluent_logs
import time

s3_bucket='aws-deepracer-b6c3c104-eef5-4878-a257-d981cd204d62'

def log_worker(job_id, log_path, image_path):
  while True:

    # Download logs
    print("Refreshing logs")
    s3_prefix='training-jobs/%s/logs' % job_id
    s3_fluent_logs.download_logs(s3_bucket, s3_prefix, log_path)

    # Training worker is the only one that knows the real number of iterations
    df = s3_fluent_logs.extract_training_iterations(log_path)
    number_iterations = df['iteration'].max()

    # Generate simulation data
    df = s3_fluent_logs.extract_simulation(log_path)

    number_episodes = df['episode'].max()
    number_transitions = df.shape[0]

    if number_transitions == 0:
      time.sleep(30)
      continue

    # TODO: I KNOW there is a faster way to do this but later
    total_reward_per_episode = list()
    total_progress_per_episode = list()
    pace_per_episode = list()
    for epi in range(0, number_episodes+1):
      df_slice = df[df['episode'] == epi]
      total_reward_per_episode.append(np.sum(df_slice['reward']))
      total_progress_per_episode.append(np.max(df_slice['progress']))
      elapsed_time = float(np.max(df_slice['simtime'])) - float(np.min(df_slice['simtime']))
      pace_per_episode.append(elapsed_time * (100 / np.max(df_slice['progress'])))

    average_reward_per_iteration = list()
    deviation_reward_per_iteration = list()
    buffer_rew = list()
    for val in total_reward_per_episode:
        buffer_rew.append(val)
        if len(buffer_rew) == 20:
            average_reward_per_iteration.append(np.mean(buffer_rew))
            deviation_reward_per_iteration.append(np.std(buffer_rew))
            buffer_rew = list()

    average_pace_per_iteration = list()
    buffer_rew = list()
    for val in pace_per_episode:
        buffer_rew.append(val)
        if len(buffer_rew) == 20:
            average_pace_per_iteration.append(np.mean(buffer_rew))
            buffer_rew = list()

    # TODO: Don't hard-code 20 episodes per iteration
    average_progress_per_iteration = list()
    buffer_rew = list()
    for val in total_progress_per_episode:
        buffer_rew.append(val)
        if len(buffer_rew) == 20:
            average_progress_per_iteration.append(np.mean(buffer_rew))
            buffer_rew = list()

    fig = plt.figure(figsize=(13, 4))
    ax = fig.add_subplot(111)
    # Show only most recent 20 data points
    progress_data = average_progress_per_iteration[-21:-1]
    ax.plot(progress_data, linewidth=5)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax = ax.twinx()
    pace_data = average_pace_per_iteration[-21:-1]
    ax.plot(pace_data, color='red', linewidth=5)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax = ax.twinx()
    reward_data = average_reward_per_iteration[-21:-1]
    ax.plot(reward_data, color='green', linewidth=5)
    ax.set_yticklabels([])
    ax.set_xticklabels([])

    fig.patch.set_facecolor('black')
    fig.savefig(os.path.join(image_path,'training.png'), facecolor=fig.get_facecolor(), edgecolor='none', transparent=True)
    print("Saved new training.png")
    plt.close(fig)


    most_progress_episode = df.loc[df['progress'].idxmax()].episode
    most_rewarded_episode = total_reward_per_episode.index(np.max(total_reward_per_episode))
    fastest_episode = pace_per_episode.index(np.min(pace_per_episode))
    # Leave this as wall clock time for reporting, whereas pace is calculated
    # with sim-time
    session_start = float(np.min(df['timestamp']))
    session_duration = float(np.min(df['timestamp'])) - session_start
    
    metrics = {
      "fastest_episode": {
        "number": int(fastest_episode),
        "pace": float(pace_per_episode[fastest_episode])
      },
      "most_progress_episode": {
        "number": int(most_progress_episode),
        "progress": float(df['progress'].max())
      },
      "most_rewarded_episode": {
        "number": int(most_rewarded_episode),
        "reward": float(total_reward_per_episode[most_rewarded_episode])
      },
      "number_iterations": int(number_iterations),
      "number_episodes": int(number_episodes),
      "number_transitions": int(number_transitions),
      "session_duration": float(session_duration),
      "session_start": float(session_start)
    }
    with open(os.path.join(image_path,'summary.json'), 'w') as f:
        f.write(json.dumps(metrics))

    time.sleep(30)

