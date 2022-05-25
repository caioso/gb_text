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
KEYWORD_JUMP = "jp"
KEYWORD_JUMP_RELATIVE = "jr"

# Functions
KEYWORD_FUNCTION = "fn"
KEYWORD_CALL = "call"
KEYWORD_RETURN = "ret"
KEYWORD_RETURN_I = "reti"

# Conditions
KEYWORD_IF = "if"
KEYWORD_ELSE = "else"
KEYWORD_CND = "cnd"

# Structs
KEYWORD_DATA_STRUCT = "ds"

# Regex Templates
ALIAS_REGEX = r"^(\s)*" + KEYWORD_ALIAS + "(\s)*(\w)+,(\s)*(\w)+(\s)*$"
BLOCK_REGEX = r"^(\s)*" + KEYWORD_BLOCK + "(\s)*(" + KEYWORD_PROGRAM + "|" + \
                                     KEYWORD_LOOP + "|" + \
                                     KEYWORD_FUNCTION + "|" + \
                                     KEYWORD_IF + "|" + \
                                     KEYWORD_DATA_STRUCT + ")?(\s)*$"
NAME_REGEX = r"^(\s)*" + KEYWORD_NAME + "(\s)*(\w)+(\s)*$"
END_REGEX = r"^(\s)*" + KEYWORD_END +"(\s)*$"
CONDITION_REGEX = r"^(\s*)cnd(\s+)(\b(\w+)\b)(\s+)" + \
                  r"(ge|gt|eq|ne|le|lt|\=\=|\!\=|\>|\<|\<\=|\>\=)(\s+)" + \
                  r"\$?(\b(\w*)\b)(\s+)(and|or)?(\s*)$"
CONDITIONAL_OPERATORS = ["ge", "gt", "eq", "ne",
                         "le", "lt", "==", "!=",
                         ">" , "<" , ">=", "<="]
BOOLEAN_OPERATORS = ["and", "or"]

TOKEN_REGISTER_A = ["a", "A"]
TOKEN_REGISTER_B = ["b", "B"]
TOKEN_REGISTER_C = ["c", "C"]
TOKEN_REGISTER_D = ["d", "D"]
TOKEN_REGISTER_E = ["e", "E"]
TOKEN_REGISTER_H = ["h", "H"]
TOKEN_REGISTER_L = ["l", "L"]

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

  @staticmethod
  def get_alignment(line: str) -> str:
    alignment = ""
    for char in range(0,len(line) - 1):
      if line[char:char+1].isspace():
        alignment += line[char:char+1]
    return alignment

class LabelOperation(Enum):
  DEF_LABEL = "DEF_LABEL"
  UNDEF_LABEL = "UNDEF_LABEL"

class BlockMarkerType(Enum):
  BLOCK_START = "BLOCK_START"
  BLOCK_END = "BLOCK_END"

class BlockType(Enum):
  GENERIC_BLOCK = "GENERIC_BLOCK"
  IF_BLOCK = "IF_BLOCK"
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
               is_reference: bool) -> None:
    self._name = name
    self._arg_type = arg_type
    self._pos = pos
    self._is_reference = is_reference

  @property
  def name(self) -> str:
    return self._name

  @property
  def is_reference(self) -> bool:
    return self._is_reference

  @property
  def position(self) -> int:
    return self._pos

class Function:
  def __init__(self, name: str, block: Block):
    self._name = name
    self._block = block
    self._label = f"fn__{self._name}"

  @property
  def name(self) -> str:
    return self._name

  @property
  def block(self) -> Block:
    return self._block

  @property
  def label(self) -> str:
    return self._label

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
      elif tokens[1] == KEYWORD_IF:
        return BlockType.IF_BLOCK
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
    self._correct_calls(functions)
    self._issue_warnings(functions)
    return self._processed_source

  def _find_functions(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.FNC_BLOCK]

  def _process_function(self, func_blocks: List[Block]) -> Function:
    functions = []

    for block in func_blocks:
      self._validate_function_body(block)
      name = self._extract_function_name(block)

      function = Function(name, block)
      functions.append(function)
    return functions

  def _validate_function_body(self, blk: Block) -> None:
    name_found = False
    function_body = False

    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])

      if re.match(NAME_REGEX, clear_line) and function_body == False:
        if name_found == False:
          name_found = True
        else:
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                             f"{line + 1}: only one 'name' allowed per function body")
      else:
          if name_found == True and function_body == False:
            function_body = True
          else:
            if re.match(NAME_REGEX, clear_line):
              raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected '{clear_line.strip()}' found")

  def _extract_function_name(self, blk: Block) -> str:
    name = ""
    for line in range(blk.start, blk.end):
      clear_line = Utils.extract_line_no_comments(self._raw_source[line])
      if re.match(NAME_REGEX, clear_line):
        tokens = Utils.split_tokens(clear_line)

        if name != "":
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: unexpected keyword 'name' " +
                               f"in function '{name}'")
        self._processed_source[line] = f"; {self._raw_source[line]}"
        name = tokens[1]

    return name

  def _emit_function_body(self, functions: List[Function]) -> None:
    for func in functions:
      self._processed_source[func.block.start] =\
        f"{func.label}: {self._processed_source[func.block.start]}"

  def _correct_calls(self, functions: List[Function]) -> None:
    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      tokens = Utils.split_tokens(clear_line)
      if KEYWORD_CALL in tokens:
        for func in functions:
          if func.name in tokens:
            self._processed_source[idx] = line.replace(func.name, func.label)

  def _issue_warnings(self, functions) -> None:
    for func in functions:
      has_return = False
      for line in range(func.block.start, func.block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])
        tokens = Utils.split_tokens(clear_line)
        if KEYWORD_RETURN in tokens or \
           KEYWORD_RETURN_I in tokens:
           has_return = True

      if has_return != True:
         print(f"Warning: {os.path.basename(self._input_file)} line " +
               f"{line + 1}: function '{func.name}' expected to have a return point ('ret'/'reti')")

    for idx, line in enumerate(self._processed_source):
      clear_line = Utils.extract_line_no_comments(line)
      tokens = Utils.split_tokens(clear_line)
      if KEYWORD_JUMP in tokens or \
         KEYWORD_JUMP_RELATIVE in tokens:
        for func in functions:
          if func.name in tokens:
            print(f"Warning: {os.path.basename(self._input_file)} line " +
                  f"{idx + 1}: branching to function '{func.name}' without using 'call'")

class ConditionPass:
  def __init__(self, input_file: str, source: List[str], raw_source: List[str], blocks: List[Block]):
    self._raw_source = raw_source
    self._processed_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> None:
    conditional_blocks = self._find_conditional_blocks()
    self._validate_conditional_blocks(conditional_blocks)
    self._parse_conditions(conditional_blocks)

    return self._processed_source

  def _find_conditional_blocks(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.IF_BLOCK]

  def _parse_conditions(self, conditional_blocks: List[Block]) -> None:
    for block in conditional_blocks:
      print(f"Condition block at {block.start + 1}")
      for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if re.match(CONDITION_REGEX, clear_line):
          tokens = Utils.split_tokens(clear_line)
          self._validate_condition(tokens, line)
          converted_condition = self._convert_condition(tokens, clear_line)
          print(converted_condition)

  def _validate_conditional_blocks(self, conditional_blocks: List[Block]) -> None:
    for block in conditional_blocks:
      in_conditions_list = False
      in_condition_body = False
      skip_inner_block = []
      for line in range(block.start + 1, block.end):
        clear_line = Utils.extract_line_no_comments(self._raw_source[line])
        if len(skip_inner_block) != 0:
          if re.match(BLOCK_REGEX, clear_line):
            skip_inner_block.append(1)
          elif re.match(END_REGEX, clear_line):
            skip_inner_block.pop()
        else:
          if in_conditions_list == False and \
            in_condition_body == False and \
            re.match(CONDITION_REGEX, clear_line):
            in_conditions_list = True
          elif in_conditions_list == True and \
              in_condition_body == False and \
              not re.match(CONDITION_REGEX, clear_line):
            in_condition_body = True
            in_conditions_list = False
          elif in_condition_body == True and \
               in_conditions_list == False and \
               re.match(BLOCK_REGEX, clear_line):
            skip_inner_block.append(1)
          elif in_condition_body == True and \
            re.match(CONDITION_REGEX, clear_line):
            raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                  f"{line + 1}: unexpected 'cnd' found")

  def _convert_condition(self, tokens: List[str], clear_line: str) -> str:
    alignment = Utils.get_alignment(clear_line)
    condition = f";{clear_line}\n"
    if tokens[1] not in TOKEN_REGISTER_A:
      condition += f"{alignment}ld a, {tokens[1]}\n"
    else:
      condition += f"{alignment}pop AF\n"
      condition += f"{alignment}push AF\n"
    condition += f"{alignment}cp {tokens[3]}\n"

    return condition

  def _validate_condition(self, tokens: List[str], line: int) -> None:
    if tokens[0] != KEYWORD_CND:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: expected 'cnd' found {tokens[0]}")
    if tokens[2] not in CONDITIONAL_OPERATORS:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected {tokens[2]} found")
    if len(tokens) == 5 and tokens[4] not in BOOLEAN_OPERATORS:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                                 f"{line + 1}: unexpected {tokens[4]} found")

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
  raw_source = file_source.copy()
  blocks_detection_pass = BlocksMappingPass(input_file, file_source)
  file_source, blocks = blocks_detection_pass.process()
  reg_alias_pass = RegisterLabelPass(input_file, file_source, blocks)
  file_source = reg_alias_pass.process()
  functions_pass = FunctionPass(input_file, file_source, blocks)
  file_source = functions_pass.process()
  conditions_pass = ConditionPass(input_file, file_source, raw_source, blocks)
  file_source = conditions_pass.process()

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