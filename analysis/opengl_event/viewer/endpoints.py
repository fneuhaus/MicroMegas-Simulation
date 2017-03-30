from .data_io import read_data
from .solarized import colors
import pyglet
from pyglet.gl import *
import numpy as np


class EndPoints():
   def __init__(self, input_file, tree_name, event_id=1):
      self.filename = input_file
      self.tree_name = tree_name
      self.show = True
      self.init_endpoint_list(event_id)

   def init_endpoint_list(self, event_id):
      self.end_points = []

      event_data = read_data(self.filename, self.tree_name, event=event_id)
      num_endpoints = len(event_data['x1'])
      for endpoint in range(num_endpoints):
         self.end_points.append([ event_data['x1'][endpoint], event_data['y1'][endpoint], event_data['z1'][endpoint] ])

   def draw(self):
      if self.show:
         glPointSize(5)
         glBegin(GL_POINTS)
         glColor3f(*colors['red'])  # draw end points
         for end_point in self.end_points:
            glVertex3f(*end_point)
         glEnd()
