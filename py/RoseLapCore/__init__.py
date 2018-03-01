import sys,os
sys.path.append(os.path.dirname(__file__))

__all__ = ['packer', 'input_processing', 'batcher']

import input_processing
import batcher
import packer
import argparse

def run(filename):
	tests, vehicle, tracks, model, out = input_processing.process_input(filename)
	results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)
	directory = packer.pack(results, out[0])

	return directory

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="name of batch config file")
	args = parser.parse_args()

	print('configuring...')
	tests, vehicle, tracks, model, out = input_processing.process_input(args.file)
	# tests, vehicle, tracks, model, out = input_processing.process_input("test_batch.yaml")
	print('batching...')
	results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)
	print('packing...')
	packer.pack(results, out[0])
	print('done!')