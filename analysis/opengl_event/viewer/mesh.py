from .obj_loader import WavefrontOBJ
from pyglet.gl import *


class Mesh():
   def __init__(self, input_file, scale_factor, mesh_position):
      self.show = True
      self.mesh_position = mesh_position
      self.mesh_obj = WavefrontOBJ(input_file, scale_factor=scale_factor)

   def draw(self):
      if self.show:
         glTranslatef(0, 0, self.mesh_position * 1e-3)
         glCallList(self.mesh_obj.gl_list)
         glTranslatef(0, 0, -self.mesh_position * 1e-3)
