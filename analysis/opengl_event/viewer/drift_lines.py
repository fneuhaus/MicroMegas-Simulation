from .data_io import read_data
from .solarized import colors
import pyglet
from pyglet.gl import *
import numpy as np
from progressbar import ProgressBar, SimpleProgress, Percentage, Bar


class DriftLines():
   def __init__(self, input_file, event_id=1):
      self.event_id = event_id

      self.show = True
      self.init_vertex_lists(input_file)

   def init_vertex_lists(self, filename):
      self.vertex_lists = []
      self.start_points = []
      self.end_points = []

      event_data = read_data(filename, 'driftLineTree', event=self.event_id)
      num_drift_lines = len(event_data['x_e'])
      pbar = ProgressBar(widgets=['Track: ', SimpleProgress(sep='/'), ' ', Percentage(), ' ', Bar(marker='█', left='', right='')], maxval=num_drift_lines).start()
      for drift_line in range(num_drift_lines):
         pbar.update(drift_line)
         number_of_vertices = len(event_data['x_e'][drift_line])
         vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v3f/static')
         vertex_list.vertices = np.hstack(np.array([event_data['x_e'][drift_line], event_data['y_e'][drift_line], event_data['z_e'][drift_line]]).T)
         self.vertex_lists.append(vertex_list)
         self.start_points.append([event_data['x_e'][drift_line][0], event_data['y_e'][drift_line][0], event_data['z_e'][drift_line][0]])
         self.end_points.append([event_data['x_e'][drift_line][-1], event_data['y_e'][drift_line][-1], event_data['z_e'][drift_line][-1]])
      pbar.finish()

   def draw(self):
      if self.show:

         glPointSize(5)
         glBegin(GL_POINTS)
         glColor3f(*colors['green'])  # draw start points
         for start_point in self.start_points:
            glVertex3f(*start_point)
         glColor3f(*colors['red'])  # draw end points
         for end_point in self.end_points:
            glVertex3f(*end_point)
         glEnd()

         glColor4f(0, 0, 0, 0.3)  # draw drift lines
         for vertex_list in self.vertex_lists:
            vertex_list.draw(pyglet.gl.GL_LINE_STRIP)
