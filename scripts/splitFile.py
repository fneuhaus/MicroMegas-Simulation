#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import argparse
import sys
import re
import math
import os


def get_tree_list(input_file):
	tree_list = [key.GetName() for key in input_file.GetListOfKeys() if key.GetClassName() == 'TTree']
	return tree_list


def check_for_tree(input_file_name, input_tree_name):
	tree_list = get_tree_list(input_file_name)

	if len(tree_list) == 0:
		print('No tree in {} found!'.format(input_file_name))
		sys.exit(1)

	if input_tree_name:
		if input_tree_name not in tree_list:
			print('Could not find tree {} in {}'.format(input_tree_name, input_file_name))
			sys.exit(1)
		else:
			return input_tree_name
	else:
		if len(tree_list) == 1:
			print('Choosing tree {} to split.'.format(tree_list[0]))
			return tree_list[0]

		if len(tree_list) > 1:
			print('Multiple trees found: {}. Provide -t/--tree!'.format(', '.join(tree_list)))
			sys.exit(1)
	return None


def splitFile(args):
	from ROOT import TFile, TTree  # here, otherwise -h/--help will not work

	if (not args.nevents and not args.njobs) or (args.nevents and args.njobs):
		print('Give either -j/--njobs or -n/--nevents!')
		sys.exit(1)

	if not args.batch:
		if args.nevents:
			print('Splitting file {} into parts of {} events each.'.format(args.inputFileName, args.nevents))
		else:
			print('Splitting file {} into {} parts.'.format(args.inputFileName, args.njobs))

	input_file = TFile(args.inputFileName, 'read')
	args.tree = check_for_tree(input_file, args.tree)
	if not args.tree:
		print('Error getting the right tree name!')
		sys.exit(1)
	input_tree = input_file.Get(args.tree)

	output_file_names = []
	nevents = input_tree.GetEntries()

	if not args.batch:
		print('Found {} events in tree {}.'.format(nevents, args.tree))

	if args.njobs:
		# Number of jobs given, distribute the events over the files as evenly as possible
		event_blocks = []
		left_events = nevents
		done_events = 0
		for i in range(args.njobs):
			events_for_block = int(math.ceil(float(left_events) / (args.njobs - i)))
			event_blocks.append((i, range(nevents)[done_events:done_events + events_for_block + 1]))
			left_events -= events_for_block
			done_events += events_for_block
	else:
		event_blocks = list(enumerate([range(nevents)[i:i + args.nevents] for i in range(0, nevents, args.nevents)]))
	last_block_num = event_blocks[-1][0]
	file_num_length = max(3, len(str(last_block_num)))

	for file_num, event_nums in event_blocks:
		folder = os.path.dirname(args.inputFileName)
		input_file_name = os.path.basename(args.inputFileName)
		input_file_base, extension = os.path.splitext(input_file_name)
		output_file_name = '{}/{:0>{}}_{}{}'.format(folder, str(file_num), file_num_length, input_file_base, extension)
		output_file_names.append(output_file_name)
		output_file = TFile(output_file_name, 'recreate')
		output_tree = input_tree.CloneTree(0)

		for event_num in event_nums:
			input_tree.GetEntry(event_num)
			output_tree.Fill()
		output_file.Write()
		output_file.Close()

	if not args.batch:
		print('Wrote: {}'.format(', '.join(output_file_names)))
	else:
		for output_file_name in output_file_names:
			print(output_file_name)


def main():
	parser = argparse.ArgumentParser(description='Split ROOT file in multiple files.')
	parser.add_argument('inputFileName', help='ROOT input file to split')
	parser.add_argument('-n', '--nevents', help='Number of events per file', type=int)
	parser.add_argument('-j', '--njobs', help='Number of jobs to split up to', type=int)
	parser.add_argument('-t', '--tree', help='TTree to split')
	parser.add_argument('-b', '--batch', help='Run in batch mode, only outputting the resulting files', action='store_true')

	args = parser.parse_args()
	splitFile(args)


if __name__ == '__main__':
	main()
