#!/usr/bin/env python3
from utils import parse_arguments
import sys
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


#Particle left drift area
GARFIELD_STATUS_LEFT = -1

# Calculcation abandoned (error, should not happen)
GARFIELD_STATUS_ABANDONED = -3

# Particle not inside a drift medium
GARFIELD_STATUS_NOT_IN_MEDIUM = -5

# Attachment
GARFIELD_STATUS_ATTACHMENT = -7


def analyse_file(filename):
   input_file = ROOT.TFile(filename, 'read')

   #  for i in range(input_tree.get_entries_fast()):
   amplifications = []
   for event in input_file.avalancheTree:
      if event.nele_drift != 0:
         amplifications.append(event.nele / event.nele_drift)

   print('{}: {}'.format(filename, np.mean(amplifications)))


if __name__ == '__main__':
   args = parse_arguments(sys.argv[1:])
   for filename in args.input:
      analyse_file(filename)
