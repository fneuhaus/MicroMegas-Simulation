#!/usr/bin/env python
import sys
import numpy as np
import os.path


def determine_mesh_cells(filename, force=False):
   if not os.path.isfile(filename):
      return ''
   
   input_file_basename = os.path.splitext(os.path.basename(filename))[0]
   input_file_cache = os.path.join(os.path.dirname(filename), f'.{input_file_basename}.cache')

   if not force and os.path.exists(input_file_cache):
      with open(input_file_cache) as f:
         return f.read().strip()

   input_data = np.genfromtxt(filename, comments='%', dtype='float')
   x_data, y_data, z_data = set(input_data[:,0]), set(input_data[:,1]), set(input_data[:,2])
   x_min, x_max, x_len = min(x_data), max(x_data), len(x_data)
   y_min, y_max, y_len = min(y_data), max(y_data), len(y_data)
   z_min, z_max, z_len = min(z_data) - 0.1, max(z_data) + 0.1, len(z_data)

   result = 'fm->SetMesh({}, {}, {}, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4);'.format(
      x_len, y_len, z_len, x_min, x_max, y_min, y_max, z_min, z_max)
   with open(input_file_cache, 'w') as f:
      f.write(result)
   return result


def main(argv):
   if not 1 <= len(argv) <= 2:
      print('Usage: determine_mesh_cells.py <input file> <force>')
      exit(1)

   input_file = argv[0]
   force = bool(argv[1]) if len(argv) == 2 else False
   print(determine_mesh_cells(input_file, force))


if __name__ == '__main__':
   main(sys.argv[1:])
