import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import pandas as pd
import gzip
import glob
import math

from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import LinearRing, LineString
from datetime import datetime


EPISODE_PER_ITER = 20

def load_worker_data(fname):
    data = []
    with open(fname, 'r') as f:
        for line in f.readlines():
            if "Training>" in line:
                data.append(line.split("Training> ")[1])
    return data

def load_trainer_data(fname):
    data = []
    with open(fname, 'r') as f:
        for line in f.readlines():
            if "Policy training>" in line:
                data.append(line.split("Policy training> ")[1])
    return data

def convert_worker_to_pandas(data):
    """
    Training> Name=main_level/agent, Worker=0, Episode=1, Total reward=94.49, Steps=20, Training iteration=0
    """        
    df_list = list()
    
    for d in data:
        parts = d.rstrip().split(", ")
        worker = int(parts[1][7:])
        episode = int(parts[2][8:])
        reward = float(parts[3][13:])
        steps = int(parts[4][6:])
        iteration = int(parts[5][19:])

        df_list.append((worker, episode, reward, steps, iteration))

    header = ['worker', 'episode', 'reward', 'steps', 'iteration']
    
    df = pd.DataFrame(df_list, columns=header)
    return df

def convert_trainer_to_pandas(data):
  """
  Policy training> Surrogate loss=-0.0012997969752177596, KL divergence=0.00924558937549591, Entropy=3.166605234146118, training epoch=0 , learning_rate=0.0003
  """

  df_list = list()
  for d in data:
    parts = d.rstrip().split(", ")
    loss = float(parts[0][15:])
    divergence = float(parts[1][14:])
    entropy = float(parts[2][8:])
    epoch = int(parts[3][15:])
    lr = float(parts[4][14:])
    df_list.append((loss, divergence, entropy, epoch, lr))

  header = ['Surrogate loss', 'KL divergence', 'Entropy', 'Training epoch', 'Learning rate']

  df = pd.DataFrame(df_list, columns=header)
  return df


def episode_parser(data, action_map=True, episode_map=True):
    '''
    Arrange data per episode
    '''
    action_map = {} # Action => [x,y,reward] 
    episode_map = {} # Episode number => [x,y,action,reward] 

 
    for d in data[:]:
        parts = d.rstrip().split("SIM_TRACE_LOG:")[-1].split(",")
        e = int(parts[0])
        x = float(parts[2]) 
        y = float(parts[3])
        angle = float(parts[5])
        ttl = float(parts[6])
        action = int(parts[7])
        reward = float(parts[8])

        try:
            episode_map[e]
        except KeyError:
            episode_map[e] = np.array([0,0,0,0,0,0]) #dummy
        episode_map[e] = np.vstack((episode_map[e], np.array([x,y,action,reward,angle,ttl])))

        try:
            action_map[action]
        except KeyError:
            action_map[action] = []
        action_map[action].append([x, y, reward])
                
    # top laps
    total_rewards = {}
    for x in episode_map.keys():
        arr = episode_map[x]
        total_rewards[x] = np.sum(arr[:,3])

    import operator
    top_idx = dict(sorted(total_rewards.items(), key=operator.itemgetter(1), reverse=True)[:])
    sorted_idx = list(top_idx.keys())

    return action_map, episode_map, sorted_idx

def make_error_boxes(ax, xdata, ydata, xerror, yerror, facecolor='r',
                     edgecolor='r', alpha=0.3):

    # Create list for all the error patches
    errorboxes = []

    # Loop over data points; create box from errors at each point
    for x, y, xe, ye in zip(xdata, ydata, xerror.T, yerror.T):
        rect = Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum())
        errorboxes.append(rect)

    # Create patch collection with specified colour/alpha
    pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,
                         edgecolor=edgecolor)

    # Add collection to axes
    ax.add_collection(pc)

    # Plot errorbars
    #artists = ax.errorbar(xdata, ydata, xerr=xerror, yerr=yerror,
    #                      fmt='None', ecolor='k')

    return 0

def v_color(ob):
    
    COLOR = {
        True: '#6699cc',
        False: '#ffcc33'
    }

    return COLOR[ob.is_simple]


def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, '.', color='#999999', zorder=1)


def plot_bounds(ax, ob):
    x, y = zip(*list((p.x, p.y) for p in ob.boundary))
    ax.plot(x, y, '.', color='#000000', zorder=1)

def plot_line(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color='cyan', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

def print_border(ax, waypoints, inner_border_waypoints, outer_border_waypoints):
    line = LineString(waypoints)
    plot_coords(ax, line)
    plot_line(ax, line)

    line = LineString(inner_border_waypoints)
    plot_coords(ax, line)
    plot_line(ax, line)

    line = LineString(outer_border_waypoints)
    plot_coords(ax, line)
    plot_line(ax, line)

def get_closest_waypoint(x, y, waypoints):
    res = 0
    index = 0
    min_distance = float('inf')
    for row in waypoints:
        distance = math.sqrt((row[0] - x) * (row[0] - x) + (row[1] - y) * (row[1] - y))
        if distance < min_distance:
            min_distance = distance
            res = index
        index = index + 1
    return res
    
def plot_grid_world(episode_df, inner, outer, scale=10.0, plot=True):
    """
    plot a scaled version of lap, along with throttle taken a each position
    """
    stats = []
    outer = [(val[0] / scale, val[1] / scale) for val in outer]
    inner = [(val[0] / scale, val[1] / scale) for val in inner]

    max_x = int(np.max([val[0] for val in outer]))
    max_y = int(np.max([val[1] for val in outer]))

    print(max_x, max_y)
    grid = np.zeros((max_x+1, max_y+1))

    # create shapely ring for outter and inner
    outer_polygon = Polygon(outer)
    inner_polygon = Polygon(inner)

    print('Outer polygon length = %.2f (meters)' % (outer_polygon.length / scale))
    print('Inner polygon length = %.2f (meters)' % (inner_polygon.length / scale))

    dist = 0.0
    for ii in range(1, len(episode_df)):
        dist += math.sqrt((episode_df['x'].iloc[ii] - episode_df['x'].iloc[ii-1])**2 + (episode_df['y'].iloc[ii] - episode_df['y'].iloc[ii-1])**2)
    dist /= 100.0

   
    t0 = datetime.fromtimestamp(float(episode_df['timestamp'].iloc[0]))
    t1 = datetime.fromtimestamp(float(episode_df['timestamp'].iloc[len(episode_df) - 1]))

    lap_time = (t1-t0).total_seconds()

    average_throttle = np.nanmean(episode_df['throttle'])
    max_throttle = np.nanmax(episode_df['throttle'])
    min_throttle = np.nanmin(episode_df['throttle'])
    velocity = dist/lap_time

    print('Distance, lap time = %.2f (meters), %.2f (sec)' % (dist, lap_time))
    print('Average throttle, velocity = %.2f (Gazebo), %.2f (meters/sec)' % (average_throttle, velocity))

    stats.append((dist, lap_time, velocity, average_throttle, min_throttle, max_throttle))


    if plot == True:
        for y in range(max_y):
            for x in range(max_x):
                point = Point((x, y))

                # this is the track
                if (not inner_polygon.contains(point)) and (outer_polygon.contains(point)):
                    grid[x][y] = -1.0

                # find df slice that fits into this
                df_slice = episode_df[(episode_df['x'] >= (x - 1) * scale) & (episode_df['x'] < x * scale) & \
                                   (episode_df['y'] >= (y - 1) * scale) & (episode_df['y'] < y * scale)]

                if len(df_slice) > 0:
                    #average_throttle = np.nanmean(df_slice['throttle'])
                    grid[x][y] = np.nanmean(df_slice['throttle'])

        fig = plt.figure(figsize=(7,7))
        imgplot = plt.imshow(grid)
        plt.colorbar(orientation='vertical')
        plt.title('Lap time (sec) = %.2f' %lap_time)
        #plt.savefig('grid.png')

    return lap_time, average_throttle, stats
