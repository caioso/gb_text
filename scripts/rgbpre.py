#!/usr/bin/env python3

from multiprocessing import Condition
import os
import argparse
from typing import List

# Custom imports
from passes.block_mapping_pass import BlocksMappingPass
from passes.condition_pass import ConditionPass
from passes.find_includes_pass import FindIncludesPass
from passes.function_pass import FunctionPass
from passes.register_alias_pass import RegisterAliasPass
from utils import Utils

# sys.tracebacklimit = 0

def main():
  parser = argparse.ArgumentParser(description='rgb pre-processor')
  parser.add_argument('-i', '--input', type=str,
                      help='Input file name', nargs=1)
  parser.add_argument('-o', '--output', type=str,
                      help='Output file name', nargs=1)
  parser.add_argument('-I', '--include', type=str,
                      help='Include directory', nargs="*")
  args = parser.parse_args()

  # Acquire arguments
  input_path = args.input[0]
  output_path = args.output[0]
  include_path = args.include
  if include_path == None:
    include_path = []
  include_path.append(os.getcwd())
  include_path = list(set(include_path))

  # process file
  process_file(input_path, output_path, include_path)


def process_file(input_file: str, output_file: str, include_path: List[str]) -> None:
  file_source = Utils.load_file_source(input_file, include_path)
  raw_source = file_source.copy()
  included_file_list = FindIncludesPass(input_file, file_source, include_path)
  included_files, identifiers = included_file_list.process()
  blocks_detection_pass = BlocksMappingPass(input_file, file_source)
  file_source, blocks = blocks_detection_pass.process()
  functions_pass = FunctionPass(input_file, file_source, blocks)
  functions, file_source = functions_pass.process()
  reg_alias_pass = RegisterAliasPass(input_file, file_source, blocks, identifiers, functions)
  file_source = reg_alias_pass.process()
  cond_pass = ConditionPass(input_file, file_source, blocks, identifiers, functions)
  cond_pass.process()
  final_source = file_source

  #save file
  with open(output_file, 'w') as f:
    f.write(Utils.get_flat_text(final_source))

if __name__ == "__main__":
    main()