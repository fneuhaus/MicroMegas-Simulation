#!/usr/bin/env python3
import numpy as np
from array import array
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import argparse
import sys
import os.path


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', required=True, help='Output path.')
parser.add_argument('-n', '--num', type=int, default=10000)
parser.add_argument('-z', '--z-pos', type=float, default=10,
      help='Z-Position for electrons (in mm).')
parser.add_argument('-e', '--energy', type=float, default=1000,
      help='Initial energy of the electrons.')
parser.add_argument('--rand-xy', action='store_true')
parser.add_argument('--x-pos', type=float, default=62.5/2)
parser.add_argument('--y-pos', type=float, default=62.5/2)
args = parser.parse_args(sys.argv[1:])

f = ROOT.TFile(os.path.expanduser(args.output), 'RECREATE')
tree = ROOT.TTree('detectorTree', 'Detector Tree')

event_id = array('i', [0])
primary_energy = array('d', [0])
primary_px = array('d', [0])
primary_py = array('d', [0])
primary_pz = array('d', [0])
phi = array('d', [0])
theta = array('d', [0])
e_kin_vertex = array('d', [0])
e_kin = array('d', [0])
z_vertex = array('d', [1])
track_length = array('d', [0])
pos_x = array('d', [0])
pos_y = array('d', [0])
pos_z = array('d', [0.7])
px = array('d', [0])
py = array('d', [0])
pz = array('d', [-1])
t = array('d', [0])

tree.Branch('eventID', event_id, 'eventID/I')
tree.Branch('primaryEnergy', primary_energy, 'primaryEnergy/D')
tree.Branch('primaryPx', primary_px, 'primaryPx/D')
tree.Branch('primaryPy', primary_py, 'primaryPy/D')
tree.Branch('primaryPz', primary_pz, 'primaryPz/D')
tree.Branch('phi', phi, 'phi/D')
tree.Branch('theta', theta, 'theta/D')
tree.Branch('EKinVertex', e_kin_vertex, 'EKinVertex/D')
tree.Branch('Ekin', e_kin, 'Ekin/D')
tree.Branch('ZVertex', z_vertex, 'ZVertex/D')
tree.Branch('PosX', pos_x, 'PosX/D')
tree.Branch('PosY', pos_y, 'PosY/D')
tree.Branch('PosZ', pos_z, 'PosZ/D')
tree.Branch('Px', px, 'Px/D')
tree.Branch('Py', py, 'Pz/D')
tree.Branch('Pz', pz, 'Py/D')
tree.Branch('t', t, 't/D')

for i in range(args.num):
   event_id[0] = i
   px[0] = np.random.uniform(-1, 1)
   py[0] = np.random.uniform(-1, 1)
   pz[0] = np.random.uniform(-1, 1)
   if args.rand_xy:
      pos_x[0] = np.random.uniform(-62.5e-4, 62.5e-4)
      pos_y[0] = np.random.uniform(-62.5e-4, 62.5e-4)
   else:
      pos_x[0] = args.x_pos * 1e-4
      pos_y[0] = args.y_pos * 1e-4
   pos_z[0] = args.z_pos * 1e-1
   e_kin[0] = args.energy
   e_kin_vertex[0] = args.energy

   tree.Fill()

tree.Write()
del tree
f.Write()
f.Close()
