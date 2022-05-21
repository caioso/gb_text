#!/usr/bin/env python3

from ast import keyword
from calendar import c
import os
import re
import argparse
import sys

from enum import Enum
from turtle import clear
from typing import List, Tuple

# sys.tracebacklimit = 0

# Keywords
# General
KEYWORD_BLOCK = "blk"
KEYWORD_END = "end"
KEYWORD_NAME = "name"

# Alias
KEYWORD_ALIAS = "als"

# Loop
KEYWORD_LOOP = "lp"
KEYWORD_BREAK = "brk"

# Progam
KEYWORD_PROGRAM = "prg"

# Functions
KEYWORD_FUNCTION = "fn"
KEYWORD_IN = "in"
KEYWORD_OUT = "out"
KEYWORD_INVOKE = "invk"

# Conditions
KEYWORD_CONDITION = "cnd"

# Structs
KEYWORD_DATA_STRUCT = "ds"

# Regex Templates
ALIAS_REGEX = r"^(\s)*" + KEYWORD_ALIAS + "(\s)*(\w)+,(\s)*(\w)+(\s)*$"
BLOCK_REGEX = r"^(\s)*" + KEYWORD_BLOCK + "(\s)*(" + KEYWORD_PROGRAM + "|" + \
                                     KEYWORD_LOOP + "|" + \
                                     KEYWORD_FUNCTION + "|" + \
                                     KEYWORD_CONDITION + "|" + \
                                     KEYWORD_DATA_STRUCT + ")?(\s)*$"
NAME_REGEX = r"^(\s)*" + KEYWORD_NAME + "(\s)*(\w)+(\s)*$"
FUNCTION_ARG_REGEX = r"^(\s)*(" + KEYWORD_IN + "|" + KEYWORD_OUT + ")(&)?(\s)*(\w)+(\s)*$"
END_REGEX = r"^(\s)*" + KEYWORD_END +"(\s)*$"

class Utils:
  @staticmethod
  def extract_line_no_comments(line: str) -> str:
    index = line.find(';')
    return line if index == -1 else line[:index]

  @staticmethod
  def extract_code_fragment_no_comment(lines: List[str], start: int, end: int) -> str:
    fragment = ""

    for line in range(start, end):
      fragment += Utils.extract_line_no_comments(lines[line])
    return fragment

  @staticmethod
  def get_flat_text(text: List[str]) -> str:
    flat_text = ""
    for line in text:
      flat_text += line

    return flat_text

  @staticmethod
  def split_tokens(text: str) -> List[str]:
    tokens = re.split('\s+', text)
    tokens = [x for x in tokens if len(x) != 0]
    return tokens

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class BlockMarkerType(Enum):
  BLOCK_START = "BLOCK_START"
  BLOCK_END = "BLOCK_END"

class BlockType(Enum):
  GENERIC_BLOCK = "GENERIC_BLOCK"
  CND_BLOCK = "CND_BLOCK"
  LP_BLOCK = "LP_BLOCK"
  FNC_BLOCK = "FNC_BLOCK"
  DS_BLOCK = "DS_BLOCK"
  PRG_BLOCK = "PRG_BLOCK"
  NONE_BLOCK = "NONE_BLOCK" # Used to mark an 'end' token

class FunctionArgumentType(Enum):
  IN_ARG = "IN_ARG"
  OUT_ARG = "OUT_ARG"

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

class FunctionArgument:
  def __init__(self,
               name:str,
               is_reference: bool,
               arg_type: FunctionArgumentType, pos:int) -> None:
    self._name = name
    self._arg_type = arg_type
    self._pos = pos
    self._is_reference = is_reference

  @property
  def name(self) -> str:
    return self._name

  @property
  def argument_type(self) -> FunctionArgumentType:
    return self._arg_type

  @property
  def is_reference(self) -> bool:
    return self._is_reference

  @property
  def position(self) -> int:
    return self._pos

class Function:
  def __init__(self, name: str, block: Block, args: List[FunctionArgument]):
    self._name = name
    self._block = block
    self._args = args

  @property
  def name(self) -> str:
    return self._name

  @property
  def block(self) -> Block:
    return self._block

  @property
  def arguments(self) -> List[FunctionArgument]:
    return self._args

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
    self._block_type_list = []

    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      if re.match(BLOCK_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_START))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))
      elif re.match(END_REGEX, clear_line):
        self._processed_source[idx] = f"; {line}"
        self._block_list.append(BlockMarker(idx, BlockMarkerType.BLOCK_END))
        self._block_type_list.append(self._detect_block_type(clear_line, idx))

  def _detect_block_type(self, line: str, idx: int) -> BlockType:
    # This function assumes a clear line as input (no comments)
    tokens = Utils.split_tokens(line)

    if len(tokens) == 1:
      return BlockType.GENERIC_BLOCK
    elif len(tokens) == 2:
      if tokens[1] == KEYWORD_LOOP:
        return BlockType.LP_BLOCK
      elif tokens[1] == KEYWORD_CONDITION:
        return BlockType.CND_BLOCK
      elif tokens[1] == KEYWORD_FUNCTION:
        return BlockType.FNC_BLOCK
      elif tokens[1] == KEYWORD_DATA_STRUCT:
        return BlockType.DS_BLOCK
      elif tokens[1] == KEYWORD_PROGRAM:
        return BlockType.PRG_BLOCK
      else:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block type")
    else:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{idx + 1}: invalid block structure")

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
    block_start = []
    blocks_type = []
    block_end = 0

    for idx, block in enumerate(self._block_list):
      if block.type == BlockMarkerType.BLOCK_START:
        blocks_start.append(block.position)
        blocks_type.append(self._block_type_list[idx])
      elif block.type == BlockMarkerType.BLOCK_END:
        block_start = blocks_start.pop()
        block_type = blocks_type.pop()
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

    return self._processed_source

  def _locate_alias_operations(self) -> List[Alias]:
    aliasses = []
    for idx, line in enumerate(self._raw_source):
      clear_line = Utils.extract_line_no_comments(line)

      if re.match(ALIAS_REGEX, clear_line):
        self._raw_source[idx] = f"; {line}"

        proper_command = re.split(KEYWORD_ALIAS, clear_line)[1]
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
      split_line = Utils.split_tokens(clear_line)

      line_text = line
      for _ in split_line:
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

class FunctionPass:
  def __init__(self, input_file: str, source: List[str], blocks: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> None:
    self._processed_source = self._raw_source
    functions_blocks = self._find_functions()
    functions = self._process_function(functions_blocks)
    self._emit_function_body(functions)
    return self._processed_source

  def _find_functions(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.FNC_BLOCK]

  def _process_function(self, func_blocks: List[Block]) -> Function:
    functions = []

    for block in func_blocks:
      self._validate_function_body(block)
      name = self._extract_function_name(block)
      args = self._extract_function_arguments(block)

      print(f"Function {name}")
      for arg in args:
        print(f"\tArgument[{arg.argument_type.value}] {arg.name} ({arg.position}) (is reference: {arg.is_reference})")

      function = Function(name, block, args)
      functions.append(function)
    return functions

  def _validate_function_body(self, blk: Block) -> None:
    name_found = False
    argument_list = False
    function_body = False

    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])

      if re.match(NAME_REGEX, clear_line) and function_body == False:
        if name_found == False:
          name_found = True
        else:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: only one 'name' allowed per function body")
      elif re.match(FUNCTION_ARG_REGEX, clear_line) and function_body == False:
        if name_found == False:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1} expected function 'name', found argument declaration '{clear_line.strip()}'")
        else:
          argument_list = True
      else:
          if name_found == True and argument_list == True and function_body == False:
            function_body = True
          else:
            if re.match(NAME_REGEX, clear_line) or \
               re.match(FUNCTION_ARG_REGEX, clear_line):
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected '{clear_line.strip()}' found")

  def _extract_function_name(self, blk: Block) -> str:
    name = ""
    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])
      if (re.match(NAME_REGEX, clear_line)):
        tokens = Utils.split_tokens(clear_line)

        if name != "":
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: unexpected keyword 'name' " +
                               f"in function '{name}'")
        self._processed_source[line] = f"; {self._raw_source[line]}"
        name = tokens[1]

    return name

  def _extract_function_arguments(self,
                                  blk: Block) -> List[FunctionArgument]:
    args = []
    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])
      if (re.match(FUNCTION_ARG_REGEX, clear_line)):
        tokens = Utils.split_tokens(clear_line)
        self._processed_source[line] = f"; {self._raw_source[line]}"
        args.append(FunctionArgument(tokens[1],
                    True if '&' in tokens[0] else False,
                    (FunctionArgumentType.IN_ARG if "in" in tokens[0] else FunctionArgumentType.OUT_ARG),
                    line))
    return args

  def _emit_function_body(self, functions: List[Function]) -> None:
    for func in functions:
      for line in range(func.block.start, func.block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if clear_line.strip() != "":
          found_arguments = [x for x in func.arguments if x.name in clear_line]
          if len(found_arguments) != 0:
            print(f"Arguments found in {clear_line}")

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
  file_source = reg_alias_pass.process()
  function_detection_pass = FunctionPass(input_file, file_source, blocks)
  file_source = function_detection_pass.process()

  final_source = file_source
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