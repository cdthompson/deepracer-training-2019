import numpy as np
from PIL import Image
import sys

def numpy_to_png(source, dest):
  image = Image.fromarray(np.load(source))
  image.save(dest,"PNG")

if __name__ == "__main__":
  source = sys.argv[1]
  dest = source.split('.npy')[0] + '.png'
  print(source, " to ", dest)
  numpy_to_png(source, dest)

