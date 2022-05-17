#!/usr/bin/env python3

import enum
import os
import re
import argparse
import sys

from enum import Enum
from turtle import clear
from typing import List, Tuple

# sys.tracebacklimit = 0

ALIAS_REGEX = r"^(\s)*alias(\s)*(\w)+,(\s)*(\w)+(\s)*$"
BLOCK_REGEX = r"^(\s)*block(\s)*(prog|loop|func|if|struct)?(\s)*$"
END_REGEX = r"^(\s)*end(\s)*$"

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

  @staticmethod
  def get_flat_text(text: List[str]) -> str:
    flat_text = ""
    for line in text:
      flat_text += line

    return flat_text

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class BlockMarkerType(Enum):
  BLOCK_START = "BLOCK_START"
  BLOCK_END = "BLOCK_END"

class BlockType(Enum):
  GENERIC_BLOCK = "GENERIC_BLOCK"
  IF_BLOCK = "IF_BLOCK"
  LOOP_BLOCK = "LOOP_BLOCK"
  FUNC_BLOCK = "FUNC_BLOCK"

class Block:
  def __init__(self, start: int, end: int,  type: BlockType, id: int):
    self._start = start
    self._end = end
    self._type = type
    self._id = id

  @property
  def start(self) -> int:
    return self._start

  @property
  def end(self) -> int:
    return self._end

  @property
  def id(self) -> int:
    return self._id

  @property
  def type(self) -> BlockType:
    return self._type

class BlockMarker:
  def __init__(self, position: int, type: BlockMarkerType):
    self._position = position
    self._type = type

  @property
  def position(self) -> int:
    return self._position

  @property
  def type(self) -> BlockMarkerType:
    return self._type

class Alias:
  def __init__(self, position: int, name: str, register: str,
                 op: LabelOperation, parent_block_id: int):
    self._position = position
    self._name = name
    self._register = register
    self._op = op
    self._parent_block_id = parent_block_id

  @property
  def position(self) -> int:
    return self._position

  @property
  def parent_block_id(self) -> int:
    return self._parent_block_id

  @property
  def name(self) -> str:
    return self._name

  @property
  def register(self) -> str:
    return self._register

  @property
  def operation(self) -> LabelOperation:
    return self._op

class BlocksMappingPass:
  def __init__(self, input_file: str, source: List[str]):
    self._raw_source = source
    self._input_file = input_file

  def process(self) -> Tuple[List[str], List[Block]]:
    self._processed_source = self._raw_source
    self._detect_blocks()
    self._validate_blocks()
    blocks = self._generate_blocks()
    return self._processed_source, blocks

  def _detect_blocks(self) -> None:
    self._block_list = []

    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      if re.match(BLOCK_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_START))
      elif re.match(END_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_END))

  def _validate_blocks(self) -> None:
    block_stack = []

    for block in self._block_list:
      if block.type == BlockMarkerType.BLOCK_START:
        block_stack.append(1)
      elif block.type == BlockMarkerType.BLOCK_END:
        if len(block_stack) == 0:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{block.position + 1}: unexpected 'end'")
        block_stack.pop()

    if len(block_stack) != 0:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{len(self._processed_source)}: 'end' expected")

  def _generate_blocks(self) -> List[Block]:
    blocks = []
    blocks_start = []
    block_start = 0
    block_end = 0
    block_type = BlockType.GENERIC_BLOCK

    for block in self._block_list:
      if block.type == BlockMarkerType.BLOCK_START:
        blocks_start.append(block.position)
        block_type = BlockType.GENERIC_BLOCK
      elif block.type == BlockMarkerType.BLOCK_END:
        block_start = blocks_start.pop()
        block_end = block.position
        blocks.append(Block(block_start, block_end, block_type, len(blocks)))

    return blocks

class RegisterLabelPass:
  def __init__(self, input_file: str, source: List[str], blocks: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks

  @property
  def processed_source(self) -> List[str]:
    return self._processed_source

  def process(self) -> None:
    aliasses = self._locate_alias_operations()

    self._process_source(aliasses)
    self._correct_remaining_aliases(aliasses)

  def _locate_alias_operations(self) -> List[Alias]:
    aliasses = []
    for block in self._blocks:
      print(f"Block id {block.id} start {block.start} end {block.end}")

    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(ALIAS_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split('alias', clear_line)[1]
        target_alias = re.split(',', proper_command)[1].strip()
        target_register = re.split(',', proper_command)[0].strip()

        parent_block_id = self._find_parent_block_id(idx)

        for alias in [x for x in aliasses if x.parent_block_id == parent_block_id]:
          if alias.name == target_alias:
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: alias '{target_alias}' " +
                                "has already been defined in this scope")

        aliasses.append(Alias(idx, target_alias,
                              target_register,
                              LabelOperation.DEF_LABEL, parent_block_id))
    return aliasses

  def _find_parent_block_id(self, line_number: int) -> int:
    min_diff = sys.maxsize
    min_id = -1

    for block in self._blocks:
      if line_number >= block.start and line_number <= block.end:
        diff = abs(block.start - line_number)
        if min_diff >= diff:
          min_diff = diff
          min_id = block.id

    return min_id

  def _find_decendent_blocks(self, line_number: int) -> List[Block]:
    blocks = []
    for block in self._blocks:
      if line_number >= block.start and line_number <= block.end:
        blocks.append(block)

    return blocks

  def _process_source(self, aliasses: List[Alias]) -> None:
    self._processed_source = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)
      split_line = re.split('\s+', clear_line)

      line_text = line
      for line_token in split_line:
        for target_alias in [x for x in aliasses if x.parent_block_id == self._find_parent_block_id(idx)]:
          if re.search(r"\b" + (target_alias.name) + r"\b" , clear_line):
            line_text = line.replace(target_alias.name, target_alias.register)

      self._processed_source.append(line_text)

  def _correct_remaining_aliases(self, aliasses: List[Alias]) -> None:
    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      for target_alias in aliasses:
          if re.search(r"\b" + (target_alias.name) + r"\b" , clear_line):
            decendent = [x.id for x in self._find_decendent_blocks(idx)]
            allowed_aliases = []
            for alias in aliasses:
              if idx >= alias.position and \
                 alias.parent_block_id in decendent and \
                 alias.name == target_alias.name:
                 allowed_aliases.append(alias)

            if len(allowed_aliases) == 0:
              print(f"Warning: {os.path.basename(self._input_file)} line " +
                    f"{idx + 1}: likely undefined register alias '{target_alias.name}'")
            else:
              print (idx)
              print (decendent)
              print ([x.name for x in allowed_aliases if x.parent_block_id in decendent])
              print(target_alias.name)
              print (([x.register for x in allowed_aliases if x.name == target_alias.name]))
              candidate_alias = [x for x in allowed_aliases if x.name == target_alias.name]
              closest_index = -1
              min_diff = sys.maxsize
              for alias_index, alias in enumerate(candidate_alias):
                diff = abs(idx - alias.position)
                if min_diff >= diff:
                  min_diff = diff
                  closest_index = alias_index

              line_text = line.replace(target_alias.name, candidate_alias[closest_index].register)
              self._processed_source[idx] = line_text


def main():
  parser = argparse.ArgumentParser(description='rgb pre-processor')
  parser.add_argument('Input', metavar='input', type=str,
                      help='Input file name')
  parser.add_argument('Output', metavar='output', type=str,
                      help='Output file name')
  args = parser.parse_args()

  # Acquire arguments
  input_path = args.Input
  output_path = args.Output

  # process file
  process_file(input_path, output_path)


def process_file(input_file: str, output_file: str) -> None:
  file_source = load_file_source(input_file)

  blocks_detection_pass = BlocksMappingPass(input_file, file_source)
  file_source, blocks = blocks_detection_pass.process()
  reg_alias_pass = RegisterLabelPass(input_file, file_source, blocks)
  reg_alias_pass.process()


  final_source = reg_alias_pass.processed_source
  #save file
  with open(output_file, 'w') as f:
    f.write(Utils.get_flat_text(final_source))

def load_file_source(file_path: str) -> List[str]:
  contents = []
  try:
    with open(file_path) as f:
      contents = f.readlines()
  except:
    raise RuntimeError(f"Unable to open file {file_path}")

  return contents

if __name__ == "__main__":
    main()