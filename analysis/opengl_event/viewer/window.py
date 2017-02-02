from .view import View
from .trackball_camera import norm1
import pyglet
from pyglet.window import key
from pyglet.gl import *


class Window(pyglet.window.Window):
   def __init__(self, width, height, title=''):
      super().__init__(width=width, height=height, caption=title)
      self.init_opengl()
      self.view = View(self)
      # self.push_handlers(pyglet.window.event.WindowEventLogger()) # to show window events

   def init_opengl(self):
      # glClearColor(colors['base3'][0], colors['base3'][1], colors['base3'][2], 1.)
      glClearColor(1, 1, 1, 1)
      glEnable(GL_DEPTH_TEST)
      glEnable(GL_BLEND)

   def on_draw(self):
      self.clear()
      self.view.draw()

   def on_resize(self, width, height):
      self.view.update(width, height)

   def on_key_press(self, symbol, modifier):
      super().on_key_press(symbol, modifier)
      if key.F1 <= symbol <= key.F12:
         object_id = symbol - key.F1
         if object_id < len(self.view.objects):
            self.view.objects[object_id].show ^= True
      # if symbol == key.F1:
      #    self.world.draw_grid ^= True
      #    self.on_draw()
      # if symbol == key.F2:
      #    self.world.draw_mesh ^= True
      #    self.on_draw()
      # if symbol == key.F3:
      #    self.world.draw_drift ^= True
      # if symbol == key.F4:
      #    self.world.draw_avalanche ^= True

   def on_mouse_press(self, x, y, button, modifiers):
      norm_x, norm_y = norm1(x, self.width), norm1(y, self.height)
      if button == pyglet.window.mouse.LEFT and (not (modifiers & (pyglet.window.key.MOD_SHIFT | pyglet.window.key.MOD_CTRL | pyglet.window.key.MOD_ALT))):
         self.view.camera.mouse_roll(norm_x, norm_y, dragging=False)
      if button == pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_SHIFT:
         self.view.camera.mouse_move(norm_x, norm_y, self.view.fov, dragging=False)
      if button == pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_CTRL:
         self.view.camera.mouse_zoom(norm_x, norm_y, dragging=False)

   def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
      norm_x, norm_y = norm1(x, self.width), norm1(y, self.height)
      if button == pyglet.window.mouse.LEFT and (not (modifiers & (pyglet.window.key.MOD_SHIFT | pyglet.window.key.MOD_CTRL | pyglet.window.key.MOD_ALT))):
         self.view.camera.mouse_roll(norm_x, norm_y)
      if button == pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_SHIFT:
         self.view.camera.mouse_move(norm_x, norm_y, self.view.fov)
      if button == pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_CTRL:
         self.view.camera.mouse_zoom(norm_x, norm_y)

   def on_mouse_scroll(self, x, y, dx, dy):
      # zoom implemented according to: https://www.opengl.org/archives/resources/faq/technical/viewing.htm Section 8.040
      zoom_factor = 1.05
      self.view.fov *= zoom_factor if dy < 0 else 1 / zoom_factor
      self.view.hud.update_text()
