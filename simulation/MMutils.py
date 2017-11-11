#!/usr/bin/env python
import sys
import numpy as np
import os.path


def determine_mesh_cells(filename):
   if not os.path.isfile(filename):
      return ''

   input_data = np.genfromtxt(filename, comments='%', dtype='float')
   range_x = np.max(np.abs(input_data[:,0]))
   range_y = np.max(np.abs(input_data[:,1]))
   min_z = np.min(input_data[:,2]) - 0.1
   #  max_x = np.max(input_data[:,0])
   #  max_y = np.max(input_data[:,1])
   max_z = np.max(input_data[:,2]) + 0.1
   len_x = len(set(input_data[:,0]))
   len_y = len(set(input_data[:,1]))
   len_z = len(set(input_data[:,2]))
   return 'fm->SetMesh({}, {}, {}, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4);'.format(
      len_x, len_y, len_z, -range_x, range_x, -range_y, range_y, min_z, max_z)


def main(argv):
   if len(argv) != 1:
      print('Usage: determine_mesh_cells.py <input file>')
      exit(1)

   print(determine_mesh_cells(argv[0]))


if __name__ == '__main__':
   main(sys.argv[1:])
