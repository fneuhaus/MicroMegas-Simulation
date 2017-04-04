from .solarized import colors
import pyglet
from pyglet.gl import *
import numpy as np


class Axes():
   def __init__(self, bounding_box=[(-1, 1), (-1, 1), (0, 3)]):
      self.bounding_box = bounding_box
      self.show = True
      self.init_coordinate_system(1)

   def init_coordinate_system(self, num_list):
      marker_len = .02
      step_size = .1

      glNewList(num_list, GL_COMPILE)
      glPushMatrix()
      glBegin(GL_LINE_STRIP)
      # bounding box
      glColor3f(*colors['base1'])
      glVertex3f(self.bounding_box[0][0], self.bounding_box[1][0], self.bounding_box[2][1])
      glVertex3f(self.bounding_box[0][1], self.bounding_box[1][0], self.bounding_box[2][1])
      glVertex3f(self.bounding_box[0][1], self.bounding_box[1][1], self.bounding_box[2][1])
      glVertex3f(self.bounding_box[0][0], self.bounding_box[1][1], self.bounding_box[2][1])
      glVertex3f(self.bounding_box[0][0], self.bounding_box[1][0], self.bounding_box[2][1])
      glEnd()

      glBegin(GL_LINES)
      # coordinate system
      glColor3f(*colors['red'])
      glVertex3f(self.bounding_box[0][0], 0, 0); glVertex3f(self.bounding_box[0][1], 0, 0)
      for x in np.arange(self.bounding_box[0][0], self.bounding_box[0][1], step_size):
         glVertex3f(x, -marker_len, 0); glVertex3f(x, marker_len, 0)
         glVertex3f(x, 0, -marker_len); glVertex3f(x, 0, marker_len)

      glColor3f(*colors['green'])
      glVertex3f(0, self.bounding_box[1][0], 0); glVertex3f(0, self.bounding_box[1][1], 0)
      for y in np.arange(self.bounding_box[1][0], self.bounding_box[1][1], step_size):
         glVertex3f(-marker_len, y, 0); glVertex3f(marker_len, y, 0)
         glVertex3f(0, y, -marker_len); glVertex3f(0, y, marker_len)

      glColor3f(*colors['blue'])
      glVertex3f(0, 0, self.bounding_box[2][0]); glVertex3f(0, 0, self.bounding_box[2][1])
      for z in np.arange(self.bounding_box[2][0], self.bounding_box[2][1], step_size):
         glVertex3f(-marker_len, 0, z); glVertex3f(marker_len, 0, z)
         glVertex3f(0, -marker_len, z); glVertex3f(0, marker_len, z)

      # x-y grid
      glColor3f(*colors['base1'])
      for x in np.arange(self.bounding_box[0][0], self.bounding_box[0][1] + step_size, step_size):
         if round(x, 2) % 0.5 == 0:
            glColor3f(*colors['orange'])
         glVertex3f(x, self.bounding_box[1][0], 0); glVertex3f(x, self.bounding_box[1][1], 0)
         if round(x, 2) % 0.5 == 0:
            glColor3f(*colors['base1'])
      for y in np.arange(self.bounding_box[1][0], self.bounding_box[1][1] + step_size, step_size):
         if round(y, 2) % 0.5 == 0:
            glColor3f(*colors['orange'])
         glVertex3f(self.bounding_box[0][0], y, 0); glVertex3f(self.bounding_box[0][1], y, 0)
         if round(y, 2) % 0.5 == 0:
            glColor3f(*colors['base1'])
      glEnd()
      glPopMatrix()
      glEndList()

   def draw(self):
      if self.show:
         glCallList(1)
