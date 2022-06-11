import os
from pydoc import splitdoc
import re
from typing import List

from constants import *
from support.assembler_identifier import AssemblerIdentifier
from support.block import (
  Block
)
from passes.struct_declaration_pass import DataStructure
from support.variable import Variable
from utils import Utils

class VariablesPass:
  def __init__(self,
               input_file: str,
               source: List[str],
               blocks: List[Block],
               structs: List[DataStructure],
               identifiers: List[AssemblerIdentifier]):
    self._raw_source = source
    self._input_file = input_file
    self._blocks = blocks
    self._identifiers = identifiers
    self._structs = structs


  def process(self) -> List[str]:
    self._processed_source = self._raw_source

    for block in self._blocks:
      print (f"Block: {block.id}")
      self._map_variables_per_block(block)
      print('\n')

    return self._processed_source

  def _map_variables_per_block(self, block: Block) -> None:
    for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if re.match(VARIABLE_DEFINITION_REGEX, clear_line):

          clear_line = clear_line.replace(',', ' ')
          tokens = Utils.split_tokens(clear_line)

          if Utils.find_parent_block_id(line, self._blocks) == block.id:
            self._construct_variable_object(tokens, line)

        elif re.search(r"\b" + KEYWORD_VAR + r"\b", clear_line):
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: invalid variable definition")

  def _construct_variable_object(self, tokens: List[str], line: int) -> Variable:
    if tokens[3] == KEYWORD_STACK:
      print('stack')
    elif KEYWORD_HEAP in tokens[3]:
      print ("heap")
    else:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: invalid variable storage")