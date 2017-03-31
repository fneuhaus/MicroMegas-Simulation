from .obj_loader import WavefrontOBJ
from pyglet.gl import *


class Mesh():
   def __init__(self, input_file, scale_factor):
      self.show = True
      self.mesh_obj = WavefrontOBJ(input_file, scale_factor=scale_factor)

   def draw(self):
      if self.show:
         glCallList(self.mesh_obj.gl_list)
