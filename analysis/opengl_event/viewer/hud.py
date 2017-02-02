from pyglet import clock, font, image
from pyglet.gl import *


class Hud():
   def __init__(self, window, view):
      self.window = window
      self.view = view
      self.font = font.load('Helvetica', 10)
      self.fps = clock.ClockDisplay(font=self.font, interval=0.2, color=(0, 0, 0, 1))

   def update(self):
      '''Called on window resize.'''
      self.update_text()
      self.draw()

   def update_text(self, text=None):
      if not text:
         text = 'FOV: {:.3}'.format(self.view.fov)
      props = dict(x=self.window.width - 10, y=10, halign=font.Text.RIGHT, valign=font.Text.BOTTOM, color=(0, 0, 0, 0.5))
      self.text = font.Text(self.font, text, **props)

   def draw(self):
      glMatrixMode(GL_MODELVIEW)
      glPushMatrix()
      glLoadIdentity()
      self.text.draw()
      self.fps.draw()
      glPopMatrix()
