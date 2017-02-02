from .obj_loader import WavefrontOBJ
from pyglet.gl import *


class Mesh():
   def __init__(self, input_file):
      self.show = True
      self.mesh_obj = WavefrontOBJ(input_file)

   def draw(self):
      if self.show:
         glCallList(self.mesh_obj.gl_list)
