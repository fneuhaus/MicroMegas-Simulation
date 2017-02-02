from .data_io import read_data
from .solarized import colors
import pyglet
from pyglet.gl import *
import numpy as np
from progressbar import ProgressBar, SimpleProgress, Percentage, Bar


class EndPoints():
   def __init__(self, input_file, tree_name, event_id=1):
      self.event_id = event_id

      self.show = True
      self.init_endpoint_list(input_file, tree_name)

   def init_endpoint_list(self, filename, tree_name):
      self.end_points = []

      event_data = read_data(filename, tree_name, event=self.event_id)
      num_endpoints = len(event_data['x1'])
      pbar = ProgressBar(widgets=['Track: ', SimpleProgress(sep='/'), ' ', Percentage(), ' ', Bar(marker='█', left='', right='')], maxval=num_endpoints).start()
      for endpoint in range(num_endpoints):
         pbar.update(endpoint)
         self.end_points.append([ event_data['x1'][endpoint], event_data['y1'][endpoint], event_data['z1'][endpoint] ])
      pbar.finish()

   def draw(self):
      if self.show:
         glPointSize(5)
         glBegin(GL_POINTS)
         glColor3f(*colors['red'])  # draw end points
         for end_point in self.end_points:
            glVertex3f(*end_point)
         glEnd()
