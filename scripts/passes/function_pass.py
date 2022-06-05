import os
import re
from typing import List, Tuple

from enums import BlockType
from support.function import Function
from constants import *
from support.block import (
  Block
)
from utils import Utils

class FunctionPass:
  def __init__(self, input_file: str, source: List[str], blocks: List[Block]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks

  def process(self) -> Tuple[List[Function], List[str]]:
    self._processed_source = self._raw_source
    functions_blocks = self._find_functions()
    functions = self._process_function(functions_blocks)
    self._emit_function_body(functions)
    self._correct_calls(functions)
    self._issue_warnings(functions)
    return functions, self._processed_source

  def _find_functions(self) -> List[Block]:
    return [x for x in self._blocks if x.type == BlockType.FNC_BLOCK]

  def _process_function(self, func_blocks: List[Block]) -> List[Function]:
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
