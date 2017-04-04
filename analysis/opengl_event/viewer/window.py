from .view import View
from .trackball_camera import norm1
import pyglet
from pyglet.window import key
from pyglet.gl import *
import numpy as np


class Window(pyglet.window.Window):
   def __init__(self, width, height, title='', event_id=1):
      super().__init__(width=width, height=height, caption=title)
      self.event_id = event_id
      self.init_opengl()
      self.view = View(self, event_id)
      self.keys = key.KeyStateHandler()
      self.push_handlers(self.keys)
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
      self.key_pressed = True
      if key.F1 <= symbol <= key.F12:
         object_id = symbol - key.F1
         if object_id < len(self.view.objects):
            self.view.objects[object_id].show ^= True
      if key._1 <= symbol <= key._3:
         self.view.camera.cam_eye = np.array([0., 0., self.view.camera.radius])
         self.view.camera.cam_focus = np.array([0., 0., 0.])
         self.view.camera.cam_up = np.array([0., 1., 0.])
         if symbol == key._1:
            self.view.camera.rot_quat = np.array([0, 0, 0, 1])
            self.view.camera.update_modelview()
         if symbol == key._2:
            self.view.camera.rot_quat = np.array([np.sqrt(0.5), 0, 0, np.sqrt(0.5)])
            self.view.camera.update_modelview()
         if symbol == key._3:
            self.view.camera.rot_quat = np.array([0.5, 0.5, 0.5, 0.5])
            self.view.camera.update_modelview()

   def on_text_motion(self, motion):
      if motion == key.LEFT:
         if self.event_id > 1:
            self.event_id -= 1
            self.view.show_event(self.event_id)
      if motion == key.RIGHT:
         self.event_id += 1
         self.view.show_event(self.event_id)

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
