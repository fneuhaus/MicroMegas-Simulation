#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pyglet
from viewer import Window, World


class EventViewer():
	def __init__(self, input_files):
		self.world = World(input_files)
		self.window = Window(1200, 800, self.world, title='OpenGL Micromegas Event Viewer')
		pyglet.clock.set_fps_limit(60)
		pyglet.app.run()


if __name__ == '__main__':
	if len(sys.argv) > 1:
		EventViewer(sys.argv[1])
	else:
		EventViewer({
			'drift': '/localscratch/micromegas/simulation/outfiles/drift_lines.root',
			'avalanche': '/localscratch/micromegas/simulation/outfiles/drift_lines_avalanche.root',
			'mesh': '/localscratch/micromegas/simulation/avalanche/geometry/mesh.obj',
		})
