from ctypes import alignment
import os
import re
from typing import List, Tuple

from constants import *
from enums import StorageType
from support.assembler_identifier import AssemblerIdentifier
from support.block import (
  Block
)
from passes.struct_declaration_pass import DataStructure
from support.variable import Variable
from support.variable_storage import VariableStorage
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


  def process(self) -> Tuple[List[str], List[Block]]:
    self._processed_source = self._raw_source

    for block in self._blocks:
      self._map_variables_per_block(block)

      # add code to reserve variable space
      stack_allocation = block.get_stack_allocation_size(self._structs, 0, self._input_file)
      if stack_allocation != 0:
        for line in range(block.start, block.end):
          if Utils.find_parent_block_id(line, self._blocks) == block.id:
            if KEYWORD_BGN[0] in self._processed_source[line]:
              alignment = Utils.get_alignment(self._processed_source[block.start])
              self._processed_source[line] += f"{alignment}add sp, {stack_allocation}\n"
              self._processed_source[block.end] = f"{alignment}sub sp, {stack_allocation}\n" + self._processed_source[block.end]
              break

    return self._processed_source, self._blocks

  def _map_variables_per_block(self, block: Block) -> None:
    for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if re.match(VARIABLE_DEFINITION_REGEX, clear_line):

          clear_line = clear_line.replace(',', ' ')
          tokens = Utils.split_tokens(clear_line)

          if Utils.find_parent_block_id(line, self._blocks) == block.id:
            variable = self._construct_variable_object(tokens, line)
            block.register_variable(variable, line, self._input_file)

        elif re.search(r"\b" + KEYWORD_VAR + r"\b", clear_line):
          raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                               f"{line + 1}: invalid variable definition")

  def _construct_variable_object(self, tokens: List[str], line: int) -> Variable:
    storage = StorageType.INVALID_STORAGE
    heap_address = ""
    if tokens[3] == KEYWORD_STACK:
      storage = StorageType.STACK_STORAGE
    elif KEYWORD_HEAP in tokens[3]:
      storage = StorageType.HEAP_STORAGE
      address = tokens[3].replace('[', ' ')
      address = address.replace(']', ' ')
      heap_address = Utils.split_tokens(address)[1]
    else:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: invalid variable storage")

    name = tokens[1]
    if Utils.is_valid_identifier(name) == False:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: invalid variable identifier '{tokens[1]}'")
    type = tokens[2]
    struct_type_names = [x.name for x in self._structs]
    if type not in VARIABLE_BASIC_TYPES and type not in struct_type_names:
      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                         f"{line + 1}: invalid variable type '{tokens[2]}'")

    return Variable(line, name, type, VariableStorage(storage, heap_address))