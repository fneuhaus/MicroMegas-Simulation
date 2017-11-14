#!/usr/bin/env python
import sys
import numpy as np
import os.path


def determine_mesh_cells(filename):
   if not os.path.isfile(filename):
      return ''

   input_data = np.genfromtxt(filename, comments='%', dtype='float')
   x_data, y_data, z_data = set(input_data[:,0]), set(input_data[:,1]), set(input_data[:,2])
   x_min, x_max, x_len = min(x_data), max(x_data), len(x_data)
   y_min, y_max, y_len = min(y_data), max(y_data), len(y_data)
   z_min, z_max, z_len = min(z_data) - 0.1, max(z_data) + 0.1, len(z_data)
   return 'fm->SetMesh({}, {}, {}, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4);'.format(
      x_len, y_len, z_len, x_min, x_max, y_min, y_max, z_min, z_max)


def main(argv):
   if len(argv) != 1:
      print('Usage: determine_mesh_cells.py <input file>')
      exit(1)

   print(determine_mesh_cells(argv[0]))


if __name__ == '__main__':
   main(sys.argv[1:])
