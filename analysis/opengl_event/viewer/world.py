from .data_io import read_data
from .solarized import colors
import pyglet
from pyglet.gl import *
import numpy as np
from progressbar import ProgressBar, SimpleProgress, Percentage, Bar


class World():
	def __init__(self, input_files, event_id=1):
		self.bounding_box = [(-1, 1), (-1, 1), (0, 3)]
		self.event_id = event_id
		self.input_files = input_files
		self.init_coordinate_system(1)
		self.init_vertex_lists()

	def init_vertex_lists(self):
		if type(self.input_files) == dict:
			drift_input_files = []
			if 'drift' in self.input_files:
				drift_input_files.append(self.input_files['drift'])
			if 'avalanche' in self.input_files:
				drift_input_files.append(self.input_files['avalanche'])
		else:
			drift_input_files = [ self.input_files ]

		self.vertex_lists = []
		self.start_points = []
		self.end_points = []

		for input_file in drift_input_files:
			event_data = read_data(input_file, 'driftLineTree', event=self.event_id)
			num_drift_lines = len(event_data['x_e'])
			pbar = ProgressBar(widgets=['Track: ', SimpleProgress(sep='/'), ' ', Percentage(), ' ', Bar(marker='█', left='', right='')], maxval=num_drift_lines).start()
			for drift_line in range(num_drift_lines):
				pbar.update(drift_line)
				number_of_vertices = len(event_data['x_e'][drift_line])
				vertex_list = pyglet.graphics.vertex_list(number_of_vertices, 'v3f/static')
				vertex_list.vertices = np.hstack(np.array([event_data['x_e'][drift_line], event_data['y_e'][drift_line], event_data['z_e'][drift_line]]).T)
				self.vertex_lists.append(vertex_list)
				self.start_points.append([event_data['x_e'][drift_line][0], event_data['y_e'][drift_line][0], event_data['z_e'][drift_line][0]])
				self.end_points.append([event_data['x_e'][drift_line][-1], event_data['y_e'][drift_line][-1], event_data['z_e'][drift_line][-1]])
			pbar.finish()

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

	def draw(self):
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glTranslatef(0, 0, -1.5)

		glCallList(1)  # draw coordinate system

		glPointSize(5)
		glBegin(GL_POINTS)
		glColor3f(*colors['green'])  # draw start points
		for start_point in self.start_points:
			glVertex3f(*start_point)
		glColor3f(*colors['red'])  # draw end points
		for end_point in self.end_points:
			glVertex3f(*end_point)
		glEnd()

		glColor4f(0, 0, 0, 0.3)  # draw drift lines
		for vertex_list in self.vertex_lists:
			vertex_list.draw(pyglet.gl.GL_LINE_STRIP)

		glPopMatrix()
