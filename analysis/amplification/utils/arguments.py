from argparse import ArgumentParser
import os.path
import glob


def parse_arguments(args):
   ''' Parse the arguments for analysis. '''
   argparser = ArgumentParser(description='Analyse the data for amplification.')
   argparser.add_argument('--input', required=True, nargs='+', help='Path to the input file.')

   args = argparser.parse_args(args)

   # Check if input file exists

   return args

