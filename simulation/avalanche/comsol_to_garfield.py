#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
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
   input_data = np.genfromtxt(file_name, comments='%', dtype='float')
   output_data = np.zeros((input_data.shape[0],input_data.shape[1]+1))
   output_data[:,:-1] = input_data

   for i in range(len(output_data)):
      # COMSOL gives NaN for inside wire
      output_data[i][0:3] = scale_factor * output_data[i][0:3]
      if np.isnan(output_data[i][6]):
         output_data[i][3:7] = np.array([0., 0., 0., potential_in_wire])
         output_data[i][-1] = 1
      #  output_data[i][0:3] = 1000 * output_data[i][0:3]
      #  output_data[i][3:6] = output_data[i][3:6] / 10

   #  print('Plotting to \'field.png\'...')
   #  plot_field(output_data)

   print('Writing: \'{}\''.format(file_name_clean))
   np.savetxt(file_name_clean, output_data, fmt=['%.7g']*7+['%d'])
   print('x: [{}e-4,{}e-4]\ny: [{}e-4,{}e-4]\nz: [{}e-4,{}e-4]'.format(output_data[:,0].min(), output_data[:,0].max(), output_data[:,1].min(), output_data[:,1].max(), output_data[:,2].min(), output_data[:,2].max()))


if __name__=='__main__':
   if not 3 <= len(sys.argv) <= 5:
      print('Usage: {} <input_file> <output_file> <field in wire> <scale factor>'.format(sys.argv[0]))
      sys.exit(1)
   
   main()
