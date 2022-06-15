from ctypes import alignment
import os
import re
from typing import List, Tuple

from numpy import var

from constants import *
from enums import *
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

    func_or_prg_blocks = [x for x in self._blocks if (x.type == BlockType.FNC_BLOCK or x.type == BlockType.PRG_BLOCK)]
    for block in func_or_prg_blocks:
      self._map_variables_per_block(block)
      stack_allocation = block.get_stack_allocation_size(self._structs, block.start, self._input_file);
      self._insert_stack_allocation_code(block, stack_allocation)
      self._insert_stack_deallocation_code(block, stack_allocation)
    return self._processed_source, self._blocks

  def _insert_stack_allocation_code(self, block: Block, allocation: int) -> None:
    if allocation != 0:
      for line in range(block.start, block.end):
        tokens = Utils.split_tokens(self._processed_source[line])
        if (KEYWORD_BGN[0] in tokens or \
            KEYWORD_BGN[1] in tokens) and \
           Utils.find_parent_block_id(line, self._blocks) == block.id:
          alignment = Utils.get_alignment(self._raw_source[block.start])
          self._processed_source[line] += f"{alignment}add sp, {allocation}\n"
          return

      raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                        f"{block.start + 1}: expected keyword '{KEYWORD_BGN[0]}' or '{KEYWORD_BGN[1]}'")

  def _insert_stack_deallocation_code(self, block: Block, allocation: int) -> None:
    if allocation != 0:
      # add dealocation to the end of the block
      tokens = Utils.split_tokens(self._processed_source[block.end])
      if (KEYWORD_END[0] in tokens or \
          KEYWORD_END[1] in tokens) and \
          Utils.find_parent_block_id(block.end, self._blocks) == block.id:
        alignment = Utils.get_alignment(self._raw_source[block.end - 1])
        self._processed_source[block.end] = f"{alignment}sub sp, {allocation}\n{self._processed_source[block.end]}"
      else:
        raise RuntimeError(f"{os.path.basename(self._input_file)} line " +
                           f"{block.start + 1}: expected keyword '{KEYWORD_END[0]}' or '{KEYWORD_END[1]}'")

    for line in range(block.start, block.end):
      tokens = Utils.split_tokens(self._processed_source[line])
      if (KEYWORD_RETURN in tokens or KEYWORD_RETURN_I in tokens):
        alignment = Utils.get_alignment(self._raw_source[line])
        self._processed_source[line] = f"{alignment}sub sp, {allocation}\n{self._processed_source[line]}"

  def _map_variables_per_block(self, block: Block) -> None:
    for line in range(block.start, block.end):
        clear_line = Utils.extract_line_no_comments(self._processed_source[line])
        if re.match(VARIABLE_DEFINITION_REGEX, clear_line):

          clear_line = clear_line.replace(',', ' ')
          tokens = Utils.split_tokens(clear_line)

          variable = self._construct_variable_object(tokens, line)
          block.register_variable(variable, line, self._input_file)

          self._processed_source[line] = f";{self._processed_source[line]}"

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