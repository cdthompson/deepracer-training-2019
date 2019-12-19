import numpy as np
import sys

def convert(track_fname):
  #canada_race = np.load('canada_race.npy')
  track_array = np.load(track_fname)

  print("Loaded ", track_fname, " with shape ", track_array.shape)
  np.set_printoptions(edgeitems=3,infstr='inf', linewidth=75, nanstr='nan', precision=8, suppress=False, threshold=100000, formatter=None)

  track_array_not_loop = track_array[0:-1]
  print("Truncated array to ", track_array_not_loop.shape)

  #print(np.array_repr(canada_race))
  #with open('canada_race.py','w') as f:
  #with open('Canada_Training.py','w') as f:
  #  f.write(np.array_repr(canada_race))

if __name__ == "__main__":
    track_fname = sys.argv[1]
    convert(track_fname)
