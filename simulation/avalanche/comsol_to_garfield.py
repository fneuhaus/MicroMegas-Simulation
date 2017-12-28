#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os.path
import numpy as np


def plot_field(data):
   import matplotlib as mpl
   mpl.use('Agg')
   from pylab import cm
   import matplotlib.pyplot as plt
   from mpl_toolkits.mplot3d import Axes3D
   fig = plt.figure(figsize=(20,16))

   x = data[:,0]
   y = data[:,1]
   z = data[:,2]
   V = data[:,6]

   ax = fig.add_subplot(111, projection='3d', aspect='equal')
   colmap = cm.ScalarMappable(cmap=cm.hsv)
   colmap.set_array(V)

   ax.scatter(x, y, z, c=cm.hsv(V/np.max(V)), marker='o', lw=0, s=.3, alpha=.5)
   fig.colorbar(colmap)

   for z in (-64, 64):
      for x in (-64, 64):
         for y in (-64, 64):
            ax.plot([x],[y],[z])

   #plt.show()
   plt.savefig("field.png")


def main():
   file_name = sys.argv[1]
   file_name_clean = sys.argv[2]
   potential_in_wire = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.
   scale_factor = float(sys.argv[4]) if len(sys.argv) >= 5 else 1.
   print('Reading: \'{}\''.format(file_name))

   file_name_clean_base = os.path.splitext(os.path.basename(file_name_clean))[0]
   file_name_cache = os.path.join(os.path.dirname(file_name_clean), f'.{file_name_clean_base}.cache')

   input_data = np.genfromtxt(file_name, comments='%', dtype='float')
   output_data = np.zeros((input_data.shape[0], input_data.shape[1] + 1))
   output_data[:,:-1] = input_data
   x_min, y_min, z_min = 10000, 10000, 10000
   x_max, y_max, z_max = 0, 0, 0

   for i in range(len(output_data)):
      # COMSOL gives NaN for inside wire
      output_data[i][0:3] = scale_factor * output_data[i][0:3]
      if np.isnan(output_data[i][6]):
         output_data[i][3:7] = np.array([0., 0., 0., potential_in_wire])
         output_data[i][-1] = 1
      if output_data[i][0] < x_min:
         x_min = output_data[i][0]
      if output_data[i][0] > x_max:
         x_max = output_data[i][0]
      if output_data[i][1] < y_min:
         y_min = output_data[i][1]
      if output_data[i][1] > y_max:
         y_max = output_data[i][1]
      if output_data[i][2] < z_min:
         z_min = output_data[i][2]
      if output_data[i][2] > z_max:
         z_max = output_data[i][2]

   #  print('Plotting to \'field.png\'...')
   #  plot_field(output_data)

   print('Writing: \'{}\''.format(file_name_clean))
   np.savetxt(file_name_clean, output_data, fmt=['%.7g']*7+['%d'])

   x_len, y_len, z_len = len(set(output_data[:,0])), len(set(output_data[:,1])), len(set(output_data[:,2]))
   result = 'fm->SetMesh({}, {}, {}, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4, {}e-4);'.format(
      x_len, y_len, z_len, x_min, x_max, y_min, y_max, z_min - 0.1, z_max + 0.1)
   with open(file_name_cache, 'w') as f:
      f.write(result)
   print('Writing cache file: "{}"'.format(file_name_cache))

   print('x: [{}e-4, {}e-4]\ny: [{}e-4, {}e-4]\nz: [{}e-4, {}e-4]'.format(x_min, x_max, y_min, y_max, z_min, z_max))


if __name__=='__main__':
   if not 3 <= len(sys.argv) <= 5:
      print('Usage: {} <input_file> <output_file> <field in wire> <scale factor>'.format(sys.argv[0]))
      sys.exit(1)
   
   main()
