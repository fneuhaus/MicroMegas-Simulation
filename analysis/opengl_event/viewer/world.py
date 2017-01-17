from .data_io import read_data
from .solarized import colors
from .obj_loader import WavefrontOBJ
import pyglet
from pyglet.gl import *
import numpy as np
from progressbar import ProgressBar, SimpleProgress, Percentage, Bar


class World():
	def __init__(self, input_files, event_id=1):
		self.bounding_box = [(-1, 1), (-1, 1), (0, 3)]
		self.event_id = event_id

		# Set paths
		self.input_file_drift = input_files['drift'] if 'drift' in input_files else False
		self.input_file_avalanche = input_files['avalanche'] if 'avalanche' in input_files else False
		self.input_file_mesh = input_files['mesh'] if 'mesh' in input_files else False

		# Vertex dictionaries
		self.vertex_data = {}
		self.vertex_lists = {}
		self.start_points = {}
		self.end_points = {}

		self.mesh_obj = False
		self.draw_mesh = True
		self.draw_grid = True
		self.draw_drift = True if self.input_file_drift else False
		self.draw_avalanche = True if self.input_file_avalanche else False
		self.init_coordinate_system(1)
		# self.init_vertex_lists()

		# Load vertices
		if self.input_file_drift:
			self.vertex_data['drift'] = self.init_vertex_lists(self.input_file_drift)
		if self.input_file_avalanche:
			self.vertex_data['avalanche'] = self.init_vertex_lists(self.input_file_avalanche)

		# Load mesh if given
		if self.input_file_mesh:
			self.mesh_obj = WavefrontOBJ(self.input_file_mesh)
			glShadeModel(GL_SMOOTH)

	def init_vertex_lists(self, filename):
		vertex_lists = []
		start_points = []
		end_points = []

		event_data = read_data(filename, 'driftLineTree', event=self.event_id)
		num_drift_lines = len(event_data['x_e'])
		pbar = ProgressBar(widgets=['Track: ', SimpleProgress(sep='/'), ' ', Percentage(), ' ', Bar(marker='█', left='', right='')], maxval=num_drift_lines).start()
		for drift_line in range(num_drift_lines):
			pbar.update(drift_line)
			number_of_vertices = len(event_data['x_e'][drift_line])
			vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v3f/static')
			vertex_list.vertices = np.hstack(np.array([event_data['x_e'][drift_line], event_data['y_e'][drift_line], event_data['z_e'][drift_line]]).T)
			vertex_lists.append(vertex_list)
			start_points.append([event_data['x_e'][drift_line][0], event_data['y_e'][drift_line][0], event_data['z_e'][drift_line][0]])
			end_points.append([event_data['x_e'][drift_line][-1], event_data['y_e'][drift_line][-1], event_data['z_e'][drift_line][-1]])
		pbar.finish()

		return { 'vertex_lists': vertex_lists, 'start_points': start_points, 'end_points': end_points }

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
			glVertex3f(x, self.bounding_box[1][0], 0); glVertex3f(x, self.bounding_box[1][1], 0)
		for y in np.arange(self.bounding_box[1][0], self.bounding_box[1][1] + step_size, step_size):
			glVertex3f(self.bounding_box[0][0], y, 0); glVertex3f(self.bounding_box[0][1], y, 0)
		glEnd()
		glPopMatrix()
		glEndList()

	def draw_vertices(self, vertex_data):
		glPointSize(5)
		glBegin(GL_POINTS)
		glColor3f(*colors['green'])  # draw start points
		for start_point in vertex_data['start_points']:
			glVertex3f(*start_point)
		glColor3f(*colors['red'])  # draw end points
		for end_point in vertex_data['end_points']:
			glVertex3f(*end_point)
		glEnd()

		glColor4f(0, 0, 0, 0.3)  # draw drift lines
		for vertex_list in vertex_data['vertex_lists']:
			vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

	def draw(self):
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glTranslatef(0, 0, -1.5)

		if self.draw_grid:
			glCallList(1)  # draw coordinate system

		if self.draw_drift:
			if 'drift' in self.vertex_data:
				self.draw_vertices(self.vertex_data['drift'])

		if self.draw_avalanche:
			if 'avalanche' in self.vertex_data:
				self.draw_vertices(self.vertex_data['avalanche'])

		# Draw mesh if available
		if self.mesh_obj and self.draw_mesh:
			glCallList(self.mesh_obj.gl_list)

		glPopMatrix()
