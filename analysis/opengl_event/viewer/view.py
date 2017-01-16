from .hud import Hud
from .trackball_camera import TrackballCamera, norm1
from pyglet.gl import *


class View():
	def __init__(self, window, world):
		self.window = window
		self.world = world
		self.hud = Hud(self.window, self)
		self.camera = TrackballCamera(radius=4.)
		self.fov = 60.
		self.hud.update_text()

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
		self.world.draw()

		self.hud_projection()
		self.hud.draw()
