#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import pyglet
import argparse
from viewer import Window, DriftLines, Mesh, Axes, EndPoints
import re


def parse_arguments(argv):
   def bounding_box(s):
      try:
         match = re.match('\[\(([0-9\.\-]+,[0-9\.\-]+)\),\(([0-9\.\-]+,[0-9\.\-]+)\),\(([0-9\.\-]+,[0-9\.\-]+)\)', s.replace(' ', ''))
         if match:
            return list(map(lambda x: tuple(map(float, x.split(','))), match.groups()))
      except:
         raise argparse.ArgumentTypeError(msg)

   parser = argparse.ArgumentParser(description='OpenGL viewer for events.')
   parser.add_argument('-f', '--folder', dest='folder', action='store', default=False, metavar='',
      help='specify the input folder (instead of individual files).')
   parser.add_argument('--event', dest='event_id', type=int, default=1,
      help='event id')
   parser.add_argument('--drift', dest='drift', default=False,
      help='specify the path for the drift file.')
   parser.add_argument('--drift-lines', dest='drift_lines', default=False,
      metavar='', help='specify the file where the drift lines are stored.')
   parser.add_argument('--avalanche', dest='avalanche', default=False,
      help='specify the path for the avalanche file.')
   parser.add_argument('--avalanche-lines', dest='avalanche_lines', default=False,
      help='specify the file were the drift lines for the avalanche are stored.')
   parser.add_argument('--mesh', dest='mesh', default=False,
      help='specify the file were the obj file of the mesh is stored.')
   parser.add_argument('--mesh-scale-factor', dest='mesh_scale_factor', type=float, default=1.,
      help='scale the loaded mesh by this factor.')
   parser.add_argument('--mesh-position', type=float, default=128., dest='mesh_position',
      help='z-position of the center of the mesh in um.')
   parser.add_argument('--bounding-box', type=bounding_box, default=[(-1, 1), (-1, 1), (0, 3)],
      help='bounding box for drawing the bounding box (includes the grid).')

   options = parser.parse_args(argv)

   if options.folder:
      # Check for drift
      options.drift = os.path.join(options.folder, 'drift.root') if os.path.isfile(os.path.join(options.folder, 'drift.root')) else False
      options.drift_lines = os.path.join(options.folder, 'drift_lines.root') if os.path.isfile(os.path.join(options.folder, 'drift_lines.root')) else False

      # Check for avalanche
      options.avalanche = os.path.join(options.folder, 'avalanche.root') if os.path.isfile(os.path.join(options.folder, 'avalanche.root')) else False
      options.avalanche_lines = os.path.join(options.folder, 'avalanche_lines.root') if os.path.isfile(os.path.join(options.folder, 'avalanche_lines.root')) else False

   return options


class EventViewer():
   def __init__(self, event_id):
      self.event_id = event_id
      self.window = Window(1200, 800, title='OpenGL Micromegas Event Viewer', event_id=event_id)

   def add_object(self, obj):
      self.window.view.add_object(obj)

   def run(self):
      pyglet.clock.set_fps_limit(60)
      pyglet.app.run()


if __name__ == '__main__':
   options = parse_arguments(sys.argv[1:])
   viewer = EventViewer(options.event_id)
   viewer.add_object(Axes(options.bounding_box))
   if options.drift:
      viewer.add_object(EndPoints(options.drift, 'driftTree', options.event_id))
   if options.drift_lines:
      viewer.add_object(DriftLines(options.drift_lines, options.event_id))
   if options.avalanche:
      viewer.add_object(EndPoints(options.avalanche, 'avalancheTree', options.event_id))
   if options.avalanche_lines:
      viewer.add_object(DriftLines(options.avalanche_lines, options.event_id))
   if options.mesh:
      viewer.add_object(Mesh(options.mesh, options.mesh_scale_factor, options.mesh_position))
   viewer.run()
