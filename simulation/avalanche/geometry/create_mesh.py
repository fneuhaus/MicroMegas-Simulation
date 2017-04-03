# -*- coding: utf-8 -*-
# Create a wire mesh

import FreeCAD, Part, Draft
from PySide import QtGui,QtCore
from math import *

class MeshGenerator(QtGui.QWidget):
   def __init__(self):
      super(MeshGenerator, self).__init__()
      self.initUI()
      
   def __del__(self):
      return
      
   def initUI(self):
      # Parameters
      self.label_mesh_lattice_const = QtGui.QLabel(u"Mesh lattice constant (µm) ", self)
      self.sb_mesh_lattice_const = QtGui.QDoubleSpinBox(self)
      self.sb_mesh_lattice_const.setMaximum(1000.)
      self.sb_mesh_lattice_const.setMinimum(.01)
      self.sb_mesh_lattice_const.setSingleStep(.1)
      self.sb_mesh_lattice_const.setValue(62.5)

      self.label_wire_diameter = QtGui.QLabel(u"Wire diameter (µm) ", self)
      self.sb_wire_diameter = QtGui.QDoubleSpinBox(self)
      self.sb_wire_diameter.setMaximum(500.)
      self.sb_wire_diameter.setMinimum(.01)
      self.sb_wire_diameter.setSingleStep(.1)
      self.sb_wire_diameter.setValue(25.)

      self.label_space_above_mesh = QtGui.QLabel(u"Space above mesh (µm) ", self)
      self.sb_space_above_mesh = QtGui.QDoubleSpinBox(self)
      self.sb_space_above_mesh.setMaximum(10000.)
      self.sb_space_above_mesh.setMinimum(0.)
      self.sb_space_above_mesh.setSingleStep(1.)
      self.sb_space_above_mesh.setValue(300.)

      self.label_space_below_mesh = QtGui.QLabel(u"Space below mesh (µm) ", self)
      self.sb_space_below_mesh = QtGui.QDoubleSpinBox(self)
      self.sb_space_below_mesh.setMaximum(1000.)
      self.sb_space_below_mesh.setMinimum(0.)
      self.sb_space_below_mesh.setSingleStep(1.)
      self.sb_space_below_mesh.setValue(128.)

      self.label_safety_distance = QtGui.QLabel(u"Safety distance between wires (µm) ", self)
      self.sb_safety_distance = QtGui.QDoubleSpinBox(self)
      self.sb_safety_distance.setMaximum(1000.)
      self.sb_safety_distance.setMinimum(0.)
      self.sb_safety_distance.setSingleStep(0.1)
      self.sb_safety_distance.setValue(1.)

      self.label_num_blocks = QtGui.QLabel(u"Number of blocks of wires that should be drawn", self)
      self.sb_num_blocks = QtGui.QSpinBox(self)
      self.sb_num_blocks.setMaximum(1000.)
      self.sb_num_blocks.setMinimum(1)
      self.sb_num_blocks.setSingleStep(1)
      self.sb_num_blocks.setValue(1)

      # Ok and cancel buttons
      self.button_create = QtGui.QPushButton("Create Gas Volume", self)
      self.button_mesh_only = QtGui.QPushButton("Create Mesh", self)
      self.button_exit = QtGui.QPushButton("Close", self)

      # Layout
      layout = QtGui.QGridLayout()
      layout.addWidget(self.label_mesh_lattice_const, 0, 0)
      layout.addWidget(self.sb_mesh_lattice_const, 0, 1)
      layout.addWidget(self.label_wire_diameter, 1, 0)
      layout.addWidget(self.sb_wire_diameter, 1, 1)
      layout.addWidget(self.label_space_above_mesh, 2, 0)
      layout.addWidget(self.sb_space_above_mesh, 2, 1)
      layout.addWidget(self.label_space_below_mesh, 3, 0)
      layout.addWidget(self.sb_space_below_mesh, 3, 1)
      layout.addWidget(self.label_safety_distance, 4, 0)
      layout.addWidget(self.sb_safety_distance, 4, 1)
      layout.addWidget(self.label_num_blocks, 5, 0)
      layout.addWidget(self.sb_num_blocks, 5, 1)
      layout.addWidget(self.button_create, 6, 0)
      layout.addWidget(self.button_mesh_only, 6, 1)
      layout.addWidget(self.button_exit, 6, 2)
      self.setLayout(layout)
      # Connectors
      QtCore.QObject.connect(self.button_create, QtCore.SIGNAL("pressed()"),self.generate_unit_cell)
      QtCore.QObject.connect(self.button_mesh_only, QtCore.SIGNAL("pressed()"),self.generate_mesh_only)
      QtCore.QObject.connect(self.button_exit, QtCore.SIGNAL("pressed()"),self.Close)

   def generate_mesh_only(self):
      self.generate_unit_cell(mesh_only=True)

   def generate_unit_cell(self, mesh_only=False):
      '''Generates a complete unit cell from single mesh wires.'''
      try:
         mesh_lattice_const = float(self.sb_mesh_lattice_const.text().replace(',', '.'))*1e-3
         wire_diameter = float(self.sb_wire_diameter.text().replace(',', '.'))*1e-3
         space_above_mesh = float(self.sb_space_above_mesh.text().replace(',', '.'))*1e-3
         space_below_mesh = float(self.sb_space_below_mesh.text().replace(',', '.'))*1e-3
         safety_distance = float(self.sb_safety_distance.text().replace(',', '.'))*1e-3 # to prevent overlap of wires, which can cause trouble in later union or common operations and some other glitches
         num_blocks = int(self.sb_num_blocks.text().replace(',', '.'))  # Number of wires to be drawn in each direction
      except:
         diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning, 'Evaluation error', 'Error in evaluating the parameters')
         diag.setWindowModality(QtCore.Qt.ApplicationModal)
         diag.exec_()
         return False

      wires = {}
      for direction in ["x", "y"]:
         wires[direction] = []
         for wire_num in range(num_blocks * 4 + 1): # draw 4 wires in each direction
            wire = self.generate_wire(wire_diameter, mesh_lattice_const, safety_distance=safety_distance, num_blocks=num_blocks)
            # position wire
            if direction == "x":
               wire.Placement.Base += FreeCAD.Vector(0, wire_num*mesh_lattice_const, 0)
               if wire_num%2:
                  wire.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 180)
               else:
                  wire.Placement.Base += FreeCAD.Vector(0, 0, 2*safety_distance)
            else:
               wire.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), 90)
               wire.Placement.Base += FreeCAD.Vector(wire_num*mesh_lattice_const, 0, 0)
               if not wire_num%2:
                  wire.Placement.Rotation = wire.Placement.Rotation.multiply(FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 180))
               else:
                  wire.Placement.Base += FreeCAD.Vector(0, 0, 2*safety_distance)

            wires[direction].append(wire)

      mesh = FreeCAD.activeDocument().addObject("Part::MultiFuse","Mesh")
      mesh.Shapes = wires["x"] + wires["y"]
      mesh.Placement.Base = FreeCAD.Vector(-2.*mesh_lattice_const, -2.*mesh_lattice_const, 0) # translate mesh to origin

      if not mesh_only:
         gas_box = FreeCAD.activeDocument().addObject("Part::Box","Gas")
         gas_box.Length = mesh_lattice_const*2.
         gas_box.Width = mesh_lattice_const*2.
         gas_box.Height = space_above_mesh + space_below_mesh + wire_diameter*2.
         gas_box.Placement.Base = FreeCAD.Vector(-mesh_lattice_const, -mesh_lattice_const, -space_below_mesh-wire_diameter)

         unit_cell = FreeCAD.activeDocument().addObject("Part::Cut", "Unit Cell")
         unit_cell.Base = gas_box
         unit_cell.Tool = mesh

      mesh.touch() # to force recomputation
      FreeCAD.ActiveDocument.recompute()


   def generate_wire(self, wire_diameter, mesh_lattice_const, safety_distance=0.1e-3, num_blocks=1):
      FreeCAD.Console.PrintMessage('test')
      '''Generates a single mesh wire in x direction.'''
      vectors = []
      num_steps = 20
      for i in range(num_blocks*int(num_steps)+1):
         t = float(i)/float(num_steps) * 2*pi * 2. + pi/2. # to start at max/min
         vector_x = 4. * mesh_lattice_const * float(i)/float(num_steps)
         vector_z = sin(t)*(wire_diameter/2.+safety_distance)
         vectors.append(FreeCAD.Vector(vector_x, 0, vector_z))

      FreeCAD.Console.PrintMessage('test')
      curve = Part.makePolygon(vectors)
      wire_spline = Draft.makeBSpline(curve, closed=False, face=False)
      circle = Draft.makeCircle(radius=wire_diameter/2., face=False, support=None)
      circle.MakeFace = False
      circle.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,wire_diameter/2.), FreeCAD.Rotation(FreeCAD.Vector(0,1,0), 90))

      wire = FreeCAD.activeDocument().addObject('Part::Feature', 'wire')
      sweep = Part.Wire(wire_spline.Shape).makePipeShell([circle.Shape], True, False)
      wire.Shape = sweep

      FreeCAD.activeDocument().removeObject(wire_spline.Name)
      FreeCAD.activeDocument().removeObject(circle.Name)
      FreeCAD.Console.PrintMessage('test')
      return wire

   def Close(self):
      self.close()
      d.close()

mw = FreeCADGui.getMainWindow()
d = QtGui.QDockWidget()
d.setWidget(MeshGenerator())
d.toggleViewAction().setText("Mesh Creator")
d.setAttribute(QtCore.Qt.WA_DeleteOnClose)
d.setWindowTitle("Mesh Creator")
mw.addDockWidget(QtCore. Qt.RightDockWidgetArea, d)
