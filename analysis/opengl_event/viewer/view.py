from .hud import Hud
from .trackball_camera import TrackballCamera, norm1
from .endpoints import EndPoints
from pyglet.gl import *


class View():
   def __init__(self, window):
      self.window = window
      self.objects = []
      self.hud = Hud(self.window, self)
      self.camera = TrackballCamera(radius=4.)
      self.fov = 60.
      self.hud.update_text()

   def add_object(self, obj):
      self.objects.append(obj)

   def show_event(self, event_id):
      # For now only updating endpoints
      for obj in self.objects:
         if type(obj) == EndPoints: 
            obj.init_endpoint_list(event_id)
      self.draw()

   def update(self, width, height):
      glViewport(0, 0, width, height)
      self.hud.update()
      self.camera.update_modelview()

   def world_projection(self):
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()
      aspect_ratio = self.window.width / self.window.height
      gluPerspective(self.fov, aspect_ratio, 0.01, 100)

   def hud_projection(self):
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()
      gluOrtho2D(0, self.window.width, 0, self.window.height)

   def draw(self):
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      self.world_projection()
      glMatrixMode(GL_MODELVIEW)
      glPushMatrix()
      glTranslatef(0, 0, -1.5)
      for obj in self.objects:
         obj.draw()
      glPopMatrix()

      self.hud_projection()
      self.hud.draw()
