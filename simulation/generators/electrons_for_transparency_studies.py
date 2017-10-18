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
parser.add_argument('-z', '--z-pos', type=float, default=250,
      help='Z-Position for electrons (in um).')
parser.add_argument('--rand-xy', action='store_true')
args = parser.parse_args(sys.argv[1:])

f = ROOT.TFile(os.path.expanduser(args.output), 'RECREATE')
tree = ROOT.TTree('driftTree', 'Drift Tree')

eventID = array('i', [0])
nele = array('i', [0])
nelep = array('i', [0])
status = array('i', [0])
x0 = ROOT.vector('double')()
y0 = ROOT.vector('double')()
z0 = ROOT.vector('double')()
e0 = ROOT.vector('double')()
t0 = ROOT.vector('double')()
x1 = ROOT.vector('double')()
y1 = ROOT.vector('double')()
z1 = ROOT.vector('double')()
e1 = ROOT.vector('double')()
t1 = ROOT.vector('double')()

tree.Branch('eventID', eventID, 'eventID/I')
tree.Branch('nele', nele, 'nele/I')
tree.Branch('nelep', nelep, 'nelep/I')
tree.Branch('status', status, 'status/I')
tree.Branch('x0', x0)
tree.Branch('y0', y0)
tree.Branch('z0', z0)
tree.Branch('t0', t0)
tree.Branch('e0', e0)
tree.Branch('x1', x1)
tree.Branch('y1', y1)
tree.Branch('z1', z1)
tree.Branch('t1', t1)
tree.Branch('e1', e1)

nele[0] = 1
nelep[0] = 1
status[0] = 0
x0.push_back(0)
y0.push_back(0)
z0.push_back(0)
t0.push_back(0)
e0.push_back(0)
t1.push_back(0)
e1.push_back(0)

for i in range(args.num):
   eventID[0] = i
   if args.rand_xy:
      x1.push_back(np.random.uniform(0, 0.1))
      y1.push_back(np.random.uniform(0, 0.1))
   else:
      x1.push_back(0.)
      y1.push_back(0.)
   z1.push_back(args.z_pos * 1e-4)

   tree.Fill()
   x1.clear()
   y1.clear()
   z1.clear()

tree.Write()
del tree
f.Write()
f.Close()
